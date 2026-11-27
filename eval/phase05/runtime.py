"""Supervise only this experiment's local model processes and measure real streaming responses."""
import argparse
from contextlib import contextmanager
import json
import os
from pathlib import Path
import socket
import subprocess
import threading
import time
from urllib.error import URLError
from urllib.request import ProxyHandler, Request, build_opener

from .audit import ALIAS, BACKEND, BASE, EXPECTED, Monitor, OLLAMA, RAW, SMALL, WEIGHT, gpu_env, record, save, stamp

CLIENT = build_opener(ProxyHandler({}))


def open_local(base, path, payload=None, timeout=180):
    if base not in {BASE, SMALL} or not path.startswith("/"):
        raise ValueError("Unknown local endpoint")
    data = json.dumps(payload).encode() if payload is not None else None
    return CLIENT.open(Request(base+path,data=data,headers={"Content-Type":"application/json"}),timeout=timeout)


def api(base, path, payload=None, timeout=180):
    with open_local(base,path,payload,timeout) as response:
        return json.load(response)


@contextmanager
def launch(command, env, log):
    with log.open("w", encoding="utf8") as f:
        proc = subprocess.Popen(command,env=env,stdout=f,stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            yield proc
        finally:
            if proc.poll() is None:
                subprocess.run(["taskkill","/PID",str(proc.pid),"/T","/F"],capture_output=True)
                proc.wait(timeout=20)


def stability(out):
    rows = []
    for i in range(10):
        payload = {"model":ALIAS,"messages":[{"role":"user","content":
            f"Reply only with one JSON object with integer field answer. Compute {13+i} plus {31-i*2}."}],
            "temperature":0.2,"seed":501+i,"max_tokens":80,"stream":True,"stream_options":{"include_usage":True}}
        start = time.perf_counter()
        first = None
        content = ""
        chunks = []
        try:
            with open_local(BASE,"/v1/chat/completions",payload) as response:
                for line in response:
                    if not line.startswith(b"data: ") or line.strip()==b"data: [DONE]":
                        continue
                    chunk=json.loads(line[6:])
                    chunks.append(chunk)
                    for choice in chunk.get("choices",[]):
                        part=choice["delta"].get("content") or ""
                        if part and first is None:
                            first=time.perf_counter()-start
                        content+=part
            timing=next((c["timings"] for c in reversed(chunks) if c.get("timings")), {})
            usage=next((c["usage"] for c in reversed(chunks) if c.get("usage")), {})
            success=first is not None and any(x.get("finish_reason")=="stop" for c in chunks for x in c.get("choices",[]))
            try:
                correct=json.loads(content.strip())["answer"]==44-i
            except (ValueError,KeyError,TypeError):
                correct=False
            row=dict(request=payload,ttft_visible_s=first,wall_s=time.perf_counter()-start,text=content,
                     timings=timing,usage=usage,success=success,correct=correct,chunks=chunks)
        except (OSError,ValueError) as exc:
            row=dict(request=payload,success=False,error=str(exc),wall_s=time.perf_counter()-start,chunks=chunks)
        rows.append(row)
        record(out/"stability.jsonl",dict(round=i+1,**row))
    return rows


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--attempt",required=True)
    parser.add_argument("--mode",choices=("mmap","dio","none"),default="mmap")
    parser.add_argument("--small-only",action="store_true")
    parser.add_argument("--vulkan", action="store_true")
    ns=parser.parse_args()
    audit=json.loads((RAW/"audit.json").read_bytes())
    if not audit["complete"] or audit["sha256"]!=EXPECTED:
        raise SystemExit("No verified file")
    out=RAW/ns.attempt
    out.mkdir(exist_ok=False)
    monitor=Monitor()
    done=threading.Event()
    def sample():
        while not done.is_set():
            record(out/"memory.jsonl", monitor.sample())
            done.wait(0.5)
    monitor_thread=threading.Thread(target=sample, daemon=True)
    monitor_thread.start()
    dest=int((SMALL if ns.small_only else BASE).rsplit(":",1)[1])
    with socket.socket() as probe:
        probe.bind(("127.0.0.1",dest))
    if ns.small_only:
        args=[str(OLLAMA),"serve"]
        env=dict(os.environ,OLLAMA_HOST=f"127.0.0.1:{dest}",OLLAMA_MODELS=os.getenv("OLLAMA_MODELS","E:/OllamaModels"),
                 OLLAMA_NO_CLOUD="1",OLLAMA_NUM_PARALLEL="1",OLLAMA_MAX_LOADED_MODELS="1",CUDA_VISIBLE_DEVICES="-1")
    else:
        args=[str(BACKEND),"-m",str(WEIGHT),"--alias",ALIAS,"--host","127.0.0.1","--port",str(dest),"--offline",
              "--no-webui","-np","1","-c","8192","-b","128","-ub","64","-ngl","all","--fit","off",
              "--load-mode",ns.mode,"--no-host","--no-repack","-fa","on","-ctk","q8_0","-ctv","q8_0",
              "--reasoning","off","--no-warmup"]
        env=gpu_env()
        if ns.vulkan:
            vk=BACKEND.parent/"vulkan"
            env.update(GGML_BACKEND_PATH=str(vk/"ggml-vulkan.dll"),PATH=str(vk)+os.pathsep+env["PATH"])
            args.extend(["--device","Vulkan1"])
    start=time.perf_counter()
    try:
        with launch(args,env,out/"server.log") as proc:
            save(out/"launch.json", {"utc":stamp(),"pid":proc.pid,"command":args,"cuda_backend":env.get("GGML_BACKEND_PATH")})
            while time.perf_counter()-start<180 and proc.poll() is None:
                try:
                    payload=api(SMALL if ns.small_only else BASE,"/api/tags" if ns.small_only else "/health",timeout=2)
                    break
                except (OSError,ValueError):
                    time.sleep(.25)
            else:
                raise RuntimeError(f"Load failed or readiness timeout, exit={proc.poll()}")
            save(out/"ready.json",{"load_wall_s":time.perf_counter()-start,"response":payload,"at":stamp()})
            if not ns.small_only:
                stability(out)
            print("ready",out,flush=True)
            while not (out/"STOP").exists() and proc.poll() is None:
                time.sleep(1)
    except Exception as exc:
        save(out/"error.json",{"at":stamp(),"error":str(exc),"wall_s":time.perf_counter()-start})
        raise
    finally:
        done.set()
        monitor_thread.join()


if __name__=="__main__":
    main()
