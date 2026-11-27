"""Exercise the actual FastAPI stack and WASI through a local service."""
import argparse
import json
from pathlib import Path
from urllib.request import ProxyHandler, Request, build_opener
from urllib.error import HTTPError

from backend.model_identity import MODEL
from eval.phase06.quality import checked_project, save


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--port",type=int,default=11806)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    path=a.output
    client=build_opener(ProxyHandler({}))
    records={}
    def request(key,route,body=None):
        data=json.dumps(body).encode() if body is not None else None
        req=Request(f"http://127.0.0.1:{a.port}"+route,data=data,
                    headers={"Content-Type":"application/json"})
        try:
            with client.open(req,timeout=720) as res:
                value=json.load(res)
                status=res.status
        except HTTPError as exc:
            status=exc.code
            value=json.load(exc)
        records[key]={"path":route,"http":status,"payload":value}
        save(path,records)
        if not 200<=status<300:
            raise RuntimeError(f"{key}: HTTP {status}: {value}")
        return value
    assert request("model","/api/model/health")["state"]=="ready"
    p=checked_project("bonus")
    project=request("F01/project","/api/projects",{"name":"Phase 06 live validation"})
    file=request("F01/file",f"/api/projects/{project['id']}/files",{"filename":"bonus.py","source":p["source"]})
    fid=file["id"]
    analysis=request("F02/ast",f"/api/engine/files/{fid}/analysis")
    assert analysis["valid"]
    u=request("F02/ai",f"/api/engine/files/{fid}/understanding",
              {"target":"bonus","normal":"bonus(4)","boundary":"bonus(2, False)","exception_probe":"bonus(-1)"})
    assert all(isinstance(x,list) and len(x)==3 for x in u["result"]["parameters"])
    suite=request("F03/suite",f"/api/files/{fid}/suites",{"target":"bonus","mode":"ai"})
    assert suite["mode"]=="ai" and suite["initial_run"]["status"]=="passed"
    execution=request("F04/execution",f"/api/runs/{suite['initial_run']['id']}")
    assert execution["status"]=="passed"
    route=f"/api/engine/files/{fid}/tasks"
    ai=request("F09/configured",route,{"target":"bonus","max_repairs":0,"generation_mode":"configured"})
    assert any(r["kind"]=="GeneratedTest" and r["payload"].get("model")==MODEL for r in ai["records"])
    assert ai["status"]=="completed"
    # The deterministic baseline has known surviving mutants to exercise real model feedback.
    template=request("F13/explicit-template",route,{"target":"bonus","max_repairs":0,"generation_mode":"template"})
    row=request("F13/plan",f"/api/engine/tasks/{template['id']}/mutations",{"feedback":True})
    campaign=request("F13/run",f"/api/mutations/{row['id']}/run",{})
    full=request("F13/evidence",f"/api/mutations/{row['id']}/report")
    assert [x["id"] for x in full["manifest"]]==[x["id"] for x in p["manifest"]]
    feedback=next(e for e in full["events"] if e["kind"]=="feedback")
    assert feedback["payload"]["model"]==MODEL and feedback["payload"]["attempts"]
    assert campaign["after"] is not None and campaign["after"]["total"]==campaign["before"]["total"]==9
    assert campaign["after"]["killed"]>campaign["before"]["killed"]
    print("F01-F04, F09, F13 live end-to-end passed",campaign["before"]["killed"],campaign["after"]["killed"])

if __name__=="__main__":
    main()
