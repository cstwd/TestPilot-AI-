"""Stop the owned 4K instance, observe real HTTP recovery, and test 8K/16K safely."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.request import ProxyHandler, build_opener
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT/".runtime/phase06-model"
RAW = ROOT/"reports/phase06/raw"


def state():
    try:
        return json.loads((RUNTIME/"attestation.json").read_bytes())
    except (OSError, ValueError):
        return {}


def capture(tag):
    target = RAW/tag
    target.mkdir(exist_ok=False)
    for file in RUNTIME.iterdir():
        if file.suffix in {".json",".log",".ndjson"}:
            shutil.copy2(file,target/file.name)


def application(route,timeout=160):
    try:
        with build_opener(ProxyHandler({})).open("http://127.0.0.1:11806"+route,timeout=timeout) as r:
            return {"http":r.status,"body":json.load(r)}
    except HTTPError as exc:
        return {"http":exc.code,"body":json.load(exc)}
    except (OSError,URLError) as exc:
        return {"network_error":str(exc)}


def terminal():
    st=state()
    port=st.get("port",11763)
    try:
        with build_opener(ProxyHandler({})).open(f"http://127.0.0.1:{port}/api/version",timeout=1):
            return False
    except (OSError,URLError):
        return st.get("status") in {"stopped","resource_guard"}


def stop():
    (RUNTIME/"STOP").touch()
    for _ in range(80):
        if terminal():
            return
        time.sleep(.5)
    raise RuntimeError("Owned runtime did not stop")


def restart(context,tag,proof):
    shutil.move(str(RUNTIME),str(ROOT/".runtime"/f"phase06-model-{tag}-predecessor"))
    run_log = RAW/f"supervisor-{tag}.txt"
    with run_log.open("w",encoding="utf8") as log:
        proc=subprocess.Popen([sys.executable,"-m","eval.phase06.serve","--context",str(context)],
                              cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
        try:
            for _ in range(150):
                s=state()
                if s.get("vulkan") and s.get("status")=="serving":
                    break
                if proc.poll() is not None:
                    break
                time.sleep(.5)
            proof[f"{tag}_health"]=application("/api/model/health")
            with (RAW/f"pressure-{tag}.log").open("w",encoding="utf8") as out:
                if proof[f"{tag}_health"].get("http")==200:
                    r=subprocess.run([sys.executable,"-m","eval.phase06.pressure","--context",str(context),
                        "--output",str(RAW/f"pressure-{tag}.ndjson")],cwd=ROOT,stdout=out,stderr=subprocess.STDOUT,timeout=340)
                    proof[f"{tag}_pressure_exit"]=r.returncode
            proof[f"{tag}_end_state"]=state()
        finally:
            if proc.poll() is None:
                stop()
                proc.wait(timeout=30)
            capture(f"runtime-{tag}")
            (RAW/"recovery.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding="utf8")


if __name__=="__main__":
    proof={"before":application("/api/model/health")}
    stop()
    proof["offline_model"]=application("/api/model/health")
    proof["offline_dashboard"]=application("/api/health")
    capture("runtime-4k")
    (RAW/"recovery.json").write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding="utf8")
    restart(8192,"8k",proof)
    restart(16384,"16k",proof)
