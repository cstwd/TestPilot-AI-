"""Run the actual F13 HTTP workflow on the real Qwen-generated F09 suite."""
import json
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener

from backend.model_identity import MODEL
from .quality import save

RAW=Path(__file__).resolve().parents[2]/"reports/phase06/raw"


def main():
    path=RAW/"live-ai-mutation.json"
    live=json.loads((RAW/"live.json").read_bytes())
    task=live["F09/configured"]["payload"]
    suite=next(item["payload"] for item in task["records"] if item["kind"]=="GeneratedTest")
    assert suite["model"]==MODEL and suite["mode"]=="ai"
    client=build_opener(ProxyHandler({}))
    def request(route,post=None):
        data=json.dumps(post).encode() if post is not None else None
        req=Request("http://127.0.0.1:11806"+route,data=data,headers={"Content-Type":"application/json"})
        with client.open(req,timeout=720) as response:
            return json.load(response)
    row=request(f"/api/engine/tasks/{task['id']}/mutations",{"feedback":True})
    plan=f"/api/mutations/{row['id']}"
    evidence={"parent_task":task["id"],"generated_run":suite["run_id"],"plan":row}
    save(path,evidence)
    evidence["result"]=request(plan+"/run",{})
    evidence["report"]=request(plan+"/report")
    save(path,evidence)
    assert evidence["report"]["source_sha256"]==row["source_sha256"]
    assert evidence["result"]["before"]["total"]==9 and not evidence["result"]["before"]["unrun"]

if __name__=="__main__":
    main()
