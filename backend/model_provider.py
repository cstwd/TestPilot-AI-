"""The single outbound inference boundary. Ollama is local, pinned and resource-gated."""
from dataclasses import asdict, dataclass
import http.client
import json
import logging
import os
from pathlib import Path
from threading import BoundedSemaphore, Lock
import time
from uuid import uuid4

from pydantic import ValidationError

from .model_identity import DISPLAY_NAME, MANIFEST_SHA256, MODEL, REVISION, WEIGHT_SHA256
from .model_protocol import Probe
from .model_resources import headroom


LOG = logging.getLogger("testpilot.model")
TIME_LIMIT = 150
MAX_BYTES = 512 * 1024


class ModelError(ValueError):
    def __init__(self, kind, message, run_id=None, attempts=None):
        super().__init__(message)
        self.kind, self.run_id, self.attempts = kind, run_id, attempts or []


@dataclass
class Reply:
    run_id: str
    value: object
    attempts: list
    health: dict | None = None


def json_load(raw):
    def unique(entries):
        obj = {}
        for key, value in entries:
            if key in obj:
                raise ValueError(f"Duplicate key: {key}")
            obj[key] = value
        return obj

    def invalid(value):
        raise ValueError(f"Non-JSON constant: {value}")

    return json.loads(raw, object_pairs_hook=unique, parse_constant=invalid)


class ModelProvider:
    def __init__(self, directory=None):
        default = Path(__file__).resolve().parents[1] / ".runtime/phase06-model"
        self.directory = Path(directory or os.getenv("TESTPILOT_MODEL_RUNTIME", str(default)))
        self.slots = BoundedSemaphore(5)
        self.active = Lock()
        self.log_lock = Lock()
        self.verified = None
        self.status = {"state": "unverified", "model": DISPLAY_NAME}

    def attest(self):
        try:
            for attempt in range(6):
                try:
                    s = json_load((self.directory/"attestation.json").read_bytes())
                    break
                except PermissionError:
                    # Windows readers can race a supervisor snapshot replacement.
                    if attempt==5:
                        raise
                    time.sleep(.025)
            if s.get("status") == "resource_guard":
                raise ModelError("resource", "Ollama 已触发 Windows 资源保护")
            if (s["status"] != "serving" or not 0 <= time.time()-s["at"] <= 4 or
                    not s["vulkan"] or (s["model"], s["manifest"], s["weights"], s["revision"]) !=
                    (MODEL, MANIFEST_SHA256, WEIGHT_SHA256, REVISION)):
                raise ModelError("unavailable", "缺少有效的本机 Ollama / Vulkan 身份和守护状态")
            if not headroom(s["resources"]):
                raise ModelError("resource", "系统资源余量不足")
            if not 1 <= s["port"] <= 65535 or s["context"] not in (4096,8192,16384):
                raise ValueError("Runtime port or context invalid")
            return s
        except ModelError:
            raise
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise ModelError("unavailable", "找不到有效的本机模型运行状态") from exc

    @staticmethod
    def _fetch(port, route, payload, deadline, stream=False):
        def remaining():
            duration = deadline-time.monotonic()
            if duration <= 0:
                raise TimeoutError
            return duration

        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=remaining())
        try:
            started = time.monotonic()
            body = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode() if payload is not None else None
            connection.request("POST" if body is not None else "GET", route, body,
                               {"Content-Type":"application/json"})
            if connection.sock:
                connection.sock.settimeout(remaining())
            response = connection.getresponse()
            if response.status != 200:
                hint = response.read(1024).decode("utf8","replace")
                raise ModelError("http", f"Ollama HTTP {response.status}: {hint}")
            if not stream:
                data = response.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise ModelError("overflow", "Ollama 输出超过字节上限")
                value = json_load(data)
                if not isinstance(value, dict):
                    raise ValueError("Expected a JSON object")
                return value
            parts, length, first, final = [], 0, None, {}
            while True:
                duration = remaining()
                if connection.sock:
                    connection.sock.settimeout(duration)
                line = response.readline(MAX_BYTES+1)
                if not line:
                    break
                length += len(line)
                if length > MAX_BYTES:
                    raise ModelError("overflow", "Ollama 输出超过字节上限")
                event = json_load(line)
                if event.get("error"):
                    raise ModelError("http", str(event["error"])[:500])
                content = event.get("message",{}).get("content","")
                if content:
                    if first is None:
                        first = time.monotonic()-started
                    parts.append(content)
                final = event
                if event.get("done"):
                    break
            return {"raw":"".join(parts), "first_visible_s":first, "end":final}
        except ModelError:
            raise
        except TimeoutError as exc:
            raise ModelError("timeout","本机模型请求超时") from exc
        except (OSError, http.client.HTTPException) as exc:
            raise ModelError("unavailable", f"本机模型连接中断 ({type(exc).__name__})") from exc
        except (ValueError, TypeError, KeyError, AttributeError) as exc:
            raise ModelError("protocol", "Ollama 响应结构无效") from exc
        finally:
            connection.close()

    def verify_identity(self, state, deadline):
        port = state["port"]
        version = self._fetch(port,"/api/version",None,deadline).get("version")
        entries = self._fetch(port,"/api/tags",None,deadline).get("models",[])
        if not isinstance(entries, list):
            raise ModelError("protocol", "Ollama 模型清单格式无效")
        if not isinstance(version, str) or not version or not any(
            isinstance(model, dict) and str(model.get("name", "")).casefold() == MODEL.casefold()
            and model.get("digest") == MANIFEST_SHA256 for model in entries
        ):
            raise ModelError("identity","Ollama 实际清单与固定发布版本不一致")
        key = (state["pid"], port, version)
        if self.verified != key:
            show = self._fetch(port,"/api/show",{"model":MODEL},deadline)
            details = show.get("details",{})
            model_info = show.get("model_info", {})
            if not isinstance(details, dict) or not isinstance(model_info, dict):
                raise ModelError("protocol", "Ollama 模型详情格式无效")
            if (show.get("remote_host") or show.get("remote_model") or details.get("format")!="gguf" or
                    details.get("quantization_level")!="IQ3_XXS" or
                    model_info.get("general.basename")!="Qwen3.8-27B"):
                raise ModelError("identity","Ollama 权重格式和模型身份校验失败")
            self.verified = key
        return version

    def _write(self, item):
        with self.log_lock:
            try:
                self.directory.mkdir(parents=True,exist_ok=True)
                with (self.directory/f"requests-{os.getpid()}.ndjson").open("a",encoding="utf8") as f:
                    f.write(json.dumps(item,ensure_ascii=False,allow_nan=False)+"\n")
            except OSError as exc:
                raise ModelError("audit", "模型审计记录无法写入") from exc

    def infer(self, operation, messages, schema, *, max_tokens, seed=23, temperature=0, validate=None,
              timeout=TIME_LIMIT, check_gpu=False):
        run_id = str(uuid4())
        attempts = []
        start = time.monotonic()
        deadline = start+min(timeout,TIME_LIMIT)
        if not self.slots.acquire(blocking=False):
            self._write({"at":time.time(),"model":MODEL,"operation":operation,"run_id":run_id,
                         "status":"error","kind":"queue","reason":"模型队列已满"})
            raise ModelError("queue","模型队列已满",run_id)
        locked = False
        try:
            locked = self.active.acquire(timeout=max(0,min(45,deadline-time.monotonic())))
            if not locked:
                raise ModelError("queue_timeout","模型排队超时")
            queued_s = time.monotonic()-start
            contract = schema.model_json_schema()
            use_mmap = os.getenv("TESTPILOT_MODEL_USE_MMAP", "1") != "0"
            request_messages = list(messages)
            identity = None
            for attempt in range(1,3):
                state = self.attest()
                if sum(len(m["content"].encode("utf8")) for m in request_messages) > (state["context"]-max_tokens)*3:
                    raise ModelError("context","输入超过当前本机上下文的保守字节预算")
                endpoint = (state["pid"], state["port"])
                if identity != endpoint:
                    version = self.verify_identity(state, deadline)
                    identity = endpoint
                sent = time.monotonic()
                result = self._fetch(state["port"],"/api/chat",{
                    "model":MODEL,"messages":request_messages,"format":contract,"stream":True,
                    "think":False,"keep_alive":"5m","options":{
                        "temperature":temperature,"seed":seed,"num_predict":max_tokens,
                        "num_ctx":state["context"],"num_batch":64,"use_mmap":use_mmap}
                },deadline,stream=True)
                end = result["end"]
                raw = result["raw"]
                if end.get("model","").casefold() != MODEL.casefold():
                    raise ModelError("identity","推理响应的实际模型身份与发布版本不一致")
                note = {"run_id":run_id,"attempt":attempt,"raw":raw,"finish":end.get("done_reason"),
                        "tokens_in":end.get("prompt_eval_count"),"tokens_out":end.get("eval_count"),
                        "generation_ns":end.get("eval_duration"),"load_ns":end.get("load_duration"),
                        "ttft_s":result["first_visible_s"],"elapsed_s":time.monotonic()-sent,
                        "seed":seed,"temperature":temperature,"schema":schema.__name__,
                        "prompt":request_messages,"use_mmap":use_mmap}
                attempts.append(note)
                try:
                    if not end.get("done") or end.get("done_reason")=="length" or not raw.strip():
                        raise ValueError("empty, incomplete or truncated response")
                    json_load(raw)
                    value = schema.model_validate_json(raw)
                    if validate is not None:
                        value = validate(value)
                    note["status"] = "accepted"
                except (ValueError, SyntaxError, RecursionError, ValidationError) as exc:
                    note.update(status="rejected",reason=str(exc)[:300])
                self._write({"operation":operation,"model":MODEL,"manifest":MANIFEST_SHA256,
                             "backend_version":version,"queue_s":queued_s,"at":time.time(),**note})
                if note["status"] == "accepted":
                    health = self.gpu_allocation(state, deadline) if check_gpu else None
                    self.status = {"state":"ready","model":DISPLAY_NAME,"manifest":MANIFEST_SHA256,
                                   "backend_version":version,"at":time.time(),"run_id":run_id,
                                   "pid":state["pid"], "port":state["port"]}
                    return Reply(run_id,value,attempts,{**self.status, **health} if health else None)
                request_messages = [*messages,{"role":"user","content":
                    f"Previous response rejected ({note['reason']}). Return a complete object matching this schema: "
                    +json.dumps(contract,ensure_ascii=False)}]
            raise ModelError("schema","模型响应无法通过冻结协议或模块校验")
        except ModelError as exc:
            self.status = {"state":"unavailable","model":DISPLAY_NAME,"kind":exc.kind,"reason":str(exc)}
            self._write({"at":time.time(),"model":MODEL,"operation":operation,"run_id":run_id,
                         "status":"error","kind":exc.kind,"reason":str(exc)})
            raise ModelError(exc.kind,str(exc),run_id,attempts) from exc
        finally:
            if locked:
                self.active.release()
            self.slots.release()

    def gpu_allocation(self, state, deadline):
        latest = self.attest()
        if (latest["pid"], latest["port"]) != (state["pid"], state["port"]):
            raise ModelError("unavailable", "Ollama 在校验期间已重启")
        ps = self._fetch(state["port"], "/api/ps", None, min(deadline, time.monotonic() + 5))
        models = ps.get("models")
        if not isinstance(models, list):
            raise ModelError("protocol", "Ollama 模型加载清单格式无效")
        for model in models:
            if (isinstance(model, dict) and str(model.get("name", "")).casefold() == MODEL.casefold()
                    and model.get("digest") == MANIFEST_SHA256
                    and type(model.get("size_vram")) is int and model["size_vram"] > 0):
                return {"vulkan": True, "weight_sha256": WEIGHT_SHA256, "revision": REVISION,
                        "context": state["context"], "size_vram": model["size_vram"], "resources": latest["resources"]}
        raise ModelError("identity", "Ollama 未报告已加载的固定权重与 GPU 分配")

    def probe(self):
        try:
            reply = self.infer("health", [{"role":"user","content":"Return the JSON object with ok set to true."}],
                               Probe, max_tokens=32, check_gpu=True)
            return reply.health
        except ModelError as exc:
            return {"state":"unavailable","model":DISPLAY_NAME,"kind":exc.kind,"reason":str(exc)}

    def has_recent_inference(self):
        try:
            state = self.attest()
        except ModelError:
            return False
        observed = self.status
        return (observed["state"]=="ready" and (observed["pid"], observed["port"])==(state["pid"], state["port"])
                and time.time()-observed["at"]<=300)


provider = ModelProvider()
