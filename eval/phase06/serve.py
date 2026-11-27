"""Guard a private Ollama Vulkan service and attest the pinned local installation."""
import argparse
from hashlib import file_digest, sha256
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import time

from backend.model_identity import DEFAULT_PORT, MANIFEST_SHA256, MODEL, REVISION, WEIGHT_SHA256, WEIGHT_SIZE
from backend.model_resources import Resources, headroom


def write(path, data):
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf8")
    for attempt in range(10):
        try:
            temp.replace(path)
            return
        except PermissionError:
            if attempt == 9:
                raise
            time.sleep(.03)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--models", type=Path, default=Path("E:/OllamaModels"))
    p.add_argument("--data", type=Path, default=Path(".runtime/phase06-model"))
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--context", type=int, choices=(4096, 8192, 16384), default=4096)
    a = p.parse_args()
    a.data.mkdir(parents=True, exist_ok=True)
    manifest = (a.models/"manifests/hf.co/Jfish123/Qwen3.8-27B-16GB-GGUF/latest").read_bytes()
    if sha256(manifest).hexdigest() != MANIFEST_SHA256:
        raise SystemExit("Manifest SHA256 mismatch")
    weights = a.models/"blobs"/("sha256-"+WEIGHT_SHA256)
    with weights.open("rb") as stream:
        if weights.stat().st_size != WEIGHT_SIZE or file_digest(stream, "sha256").hexdigest() != WEIGHT_SHA256:
            raise SystemExit("Weight SHA256 mismatch")
    resources = Resources()
    if not headroom(resources.sample()):
        raise SystemExit("No safe resource headroom")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", a.port))
    backend = shutil.which("ollama")
    if backend is None:
        raise SystemExit("Ollama executable missing")
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="-1", OLLAMA_VULKAN="1", OLLAMA_NO_CLOUD="1",
               GGML_VK_VISIBLE_DEVICES="1", OLLAMA_HOST=f"127.0.0.1:{a.port}", OLLAMA_MODELS=str(a.models.resolve()),
               OLLAMA_NUM_PARALLEL="1", OLLAMA_MAX_LOADED_MODELS="1", OLLAMA_MAX_QUEUE="4",
               OLLAMA_CONTEXT_LENGTH=str(a.context), OLLAMA_FLASH_ATTENTION="1", OLLAMA_KV_CACHE_TYPE="q4_0",
               OLLAMA_LOAD_TIMEOUT="90s", OLLAMA_KEEP_ALIVE="2m",
               LLAMA_ARG_CTX_CHECKPOINTS="0", LLAMA_ARG_CACHE_RAM="0", LLAMA_ARG_NO_HOST="1")
    state = dict(model=MODEL, manifest=MANIFEST_SHA256, weights=WEIGHT_SHA256, revision=REVISION,
                 port=a.port, context=a.context, vulkan=False, backend="Ollama")
    with (a.data/"ollama.log").open("w", encoding="utf8") as log, (
            a.data/"telemetry.ndjson").open("w", encoding="utf8", buffering=1) as telemetry:
        proc = subprocess.Popen([backend,"serve"], env=env, stdout=log, stderr=subprocess.STDOUT,
                                creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            while proc.poll() is None and not (a.data/"STOP").exists():
                sample = resources.sample()
                logs = (a.data/"ollama.log").read_text("utf8", errors="replace")
                state.update(at=time.time(), pid=proc.pid, resources=sample,
                             vulkan=any("library=Vulkan" in line and "RTX 5080" in line
                                        for line in logs.splitlines() if "inference compute" in line))
                telemetry.write(json.dumps({"at": state["at"], **sample})+"\n")
                if not headroom(sample):
                    state.update(status="resource_guard")
                    break
                state.update(status="serving")
                write(a.data/"attestation.json",state)
                time.sleep(.5)
        finally:
            state.update(at=time.time(), status=state.get("status") if state.get("status")=="resource_guard" else "stopped")
            try:
                write(a.data/"attestation.json",state)
            finally:
                if proc.poll() is None:
                    subprocess.run(["taskkill","/PID",str(proc.pid),"/T","/F"], capture_output=True)
                    proc.wait(timeout=20)
    print(state["status"], state["resources"], flush=True)


if __name__ == "__main__":
    main()
