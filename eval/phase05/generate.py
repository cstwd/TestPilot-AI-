"""Record real local inference while exercising the installed F09 adapter and AST checks."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading
import time
from uuid import uuid4

from backend.engine_analyzer import analyze_source
from backend.engine_strategy import build_strategy
from backend.engine_llm import generate_tests, GenerationFailure
from backend.local_ollama import choose_model
from .audit import BASE,SMALL,ALIAS,SMALL_MODEL,RAW,stamp,save,record
from .runtime import api
from .measure import directory
from .corpus import SPEC,SEEDS,get


def generate(p,seed,arm):
    out=directory(p["name"],seed,arm)
    if (out/"generation.json").exists():
        return
    base,model=(BASE,ALIAS) if arm=="C" else (SMALL,SMALL_MODEL)
    uid=str(uuid4())
    log=out/"requests.jsonl"
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):
            pass
        def do_POST(self):
            if self.path!="/v1/chat/completions":
                return self.send_error(404)
            req=json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            if req.get("model")!=model:
                return self.send_error(400)
            req.update(seed=seed,temperature=.35,max_tokens=700)
            t=time.monotonic()
            try:
                actual=api(base,"/v1/chat/completions",req,timeout=115)
                record(log,dict(id=uid,backend=base,request=req,response=actual,seconds=time.monotonic()-t))
                response=json.dumps(actual).encode()
                self.send_response(200)
                self.send_header("Content-Type","application/json")
                self.send_header("Content-Length",str(len(response)))
                self.end_headers()
                self.wfile.write(response)
            except (OSError,ValueError) as e:
                record(log,dict(id=uid,backend=base,request=req,error=str(e),seconds=time.monotonic()-t))
                self.send_error(502)
    analysis=analyze_source(p["source"])
    strategy=build_strategy(analysis,p["target"])
    symbol=next(n for n in analysis["symbols"] if n["name"]==p["target"])
    context={k:symbol[k] for k in ("name","parameters","returns","docstring")}
    context["dependencies"]={k:v for k,v in p["files"].items() if k!="subject.py"}
    design={"target":p["target"],"contracts":strategy["contracts"],
            "strategies":[[c["type"],c["inputs"]] for c in strategy["cases"]
                           if c["type"] in {"boundary","branch","exception","missing"}][:10]}
    instructions={"task":f"Write pytest tests. Start with 'from subject import {p['target']}'. "
                 "Check exact outcomes, boundaries, branches and exceptions where justified. "
                 "Do not reproduce the subject function. Test dependencies are provided by the runner."}
    t=time.monotonic()
    with HTTPServer(("127.0.0.1",0),Handler) as relay:
        thread=threading.Thread(target=relay.serve_forever,daemon=True)
        thread.start()
        try:
            artifact=generate_tests(p["source"],p["target"],context,design,feedback=instructions,
                config={"provider":"openai-compatible","model":model,"base_url":f"http://127.0.0.1:{relay.server_port}/v1",
                        "timeout":120,"retries":1})
        except GenerationFailure as e:
            artifact=e.evidence
        finally:
            relay.shutdown()
            thread.join()
    if artifact.get("code") and artifact.get("mode")=="ai":
        (out/"proposed_test.py").write_text(artifact["code"],encoding="utf8")
    save(out/"generation.json",dict(at=stamp(),id=uid,arm=arm,seed=seed,artifact=artifact,seconds=time.monotonic()-t))
    print(p["name"],seed,arm,artifact.get("mode"),flush=True)


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("arm",choices=["A","C"])
    args=parser.parse_args()
    if args.arm=="A":
        name,digest=choose_model(SMALL,SMALL_MODEL)
        save(RAW/"small-identity.json",dict(name=name,digest=digest,show=api(SMALL,"/api/show",{"model":name})))
    for seed in SEEDS:
        for project in SPEC:
            generate(get(project),seed,args.arm)
