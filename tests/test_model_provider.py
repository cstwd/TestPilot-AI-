"""Protocol regression controls. Real model evidence is in reports/phase06."""
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Event, Thread
import time

import pytest

from backend.model_identity import MODEL, MANIFEST_SHA256, REVISION, WEIGHT_SHA256
from backend.model_protocol import Probe, Understanding
from backend.model_provider import ModelError, ModelProvider, json_load


@pytest.fixture
def service(tmp_path, monkeypatch):
    p=ModelProvider(tmp_path)
    route_calls, responses = [], []
    monkeypatch.setattr(p,"attest",lambda:{"port":11763,"context":4096,"pid":1})
    def fetch(port,route,payload,deadline,stream=False):
        route_calls.append((port,route,payload))
        if route=="/api/version":
            return {"version":"fixture"}
        if route=="/api/tags":
            return {"models":[{"name":MODEL,"digest":MANIFEST_SHA256}]}
        if route=="/api/show":
            return {"details":{"format":"gguf","quantization_level":"IQ3_XXS"},"model_info":{"general.basename":"Qwen3.8-27B"}}
        if route=="/api/ps":
            return {"models":[]}
        raw=responses.pop(0)
        if isinstance(raw,Exception):
            raise raw
        return {"raw":raw,"first_visible_s":.2,"end":{"model":MODEL,"done":True,"done_reason":"stop","eval_count":10}}
    monkeypatch.setattr(p,"_fetch",fetch)
    return p,route_calls,responses


@pytest.mark.parametrize("raw",["", "{garbage}", '{"ok":false}', '{"ok":true,"ok":true}'])
def test_retry_retains_raw_and_fixed_identity(service,raw):
    p,calls,responses=service
    responses.extend([raw,'{"ok":true}'])
    result=p.infer("unit",[{"role":"user","content":"data"}],Probe,max_tokens=32)
    assert result.value.ok and len(result.attempts)==2
    assert [a["status"] for a in result.attempts]==["rejected","accepted"]
    assert result.attempts[0]["raw"]==raw and result.attempts[1]["raw"]=='{"ok":true}'
    sent=[body for _,route,body in calls if route=="/api/chat"]
    assert all(body["model"]==MODEL and body["format"]==Probe.model_json_schema() for body in sent)


def test_frozen_parameter_array(service):
    p,_,responses=service
    base={"functions":["subject.py:example"],"parameters":[{"name":"n","type":"int","default":None}],
          "return_value":1,"branch_lines":[],"boundary_value":0,"exception":None,"defect_line":None}
    responses.extend([json.dumps(base),json.dumps({**base,"parameters":[["n","int",None]]})])
    res=p.infer("understand",[{"role":"user","content":"fixture"}],Understanding,max_tokens=100)
    assert res.value.parameters==[("n","int",None)]
    assert len(res.attempts)==2


def test_timeout_and_recovery(service):
    p,_,responses=service
    responses.extend([ModelError("timeout","timeout"),'{"ok":true}'])
    with pytest.raises(ModelError,match="timeout") as raised:
        p.infer("timeout",[],Probe,max_tokens=32)
    assert raised.value.kind=="timeout" and p.status["state"]=="unavailable"
    assert p.infer("recover",[],Probe,max_tokens=32).value.ok


def test_wrong_identity_stops_before_source(service,monkeypatch):
    p,_,_=service
    def fetch(port,path,*args,**kwargs):
        if path=="/api/version":
            return {"version":"fixture"}
        if path=="/api/tags":
            return {"models":[{"name":MODEL,"digest":"different"}]}
        pytest.fail(f"Unexpected route {path}")
    monkeypatch.setattr(p,"_fetch",fetch)
    with pytest.raises(ModelError) as err:
        p.infer("wrong",[],Probe,max_tokens=32)
    assert err.value.kind=="identity"


def test_retry_rechecks_changed_endpoint_before_sending_source(service, monkeypatch):
    p, calls, responses = service
    states = iter([{"port":11763, "context":4096, "pid":1},
                   {"port":12763, "context":4096, "pid":2}])
    monkeypatch.setattr(p, "attest", lambda: next(states))
    responses.extend(["invalid", '{"ok":true}'])
    assert p.infer("retry", [], Probe, max_tokens=32).value.ok
    assert [route for port, route, _ in calls if port == 12763] == [
        "/api/version", "/api/tags", "/api/show", "/api/chat"]


def test_failed_gpu_probe_does_not_report_recent_inference(service):
    p, _, responses = service
    responses.append('{"ok":true}')
    assert p.probe()["state"] == "unavailable"
    assert not p.has_recent_inference()


def test_windows_snapshot_read_retries_without_trusting_stale_state(tmp_path,monkeypatch):
    path = tmp_path/"attestation.json"
    valid = {"status":"serving","at":time.time(),"vulkan":True,"model":MODEL,"manifest":MANIFEST_SHA256,
             "weights":WEIGHT_SHA256,"revision":REVISION,"port":11763,"context":4096,"pid":1,
             "resources":{"physical_free_gib":3,"commit_free_gib":3,"gpu_free_mib":600}}
    path.write_text(json.dumps(valid),encoding="utf8")
    cls=type(path)
    reader=cls.read_bytes
    calls=[]
    def flaky(self):
        if self==path:
            calls.append(self)
            if len(calls)==1:
                raise PermissionError("sharing violation")
        return reader(self)
    monkeypatch.setattr(cls,"read_bytes",flaky)
    p=ModelProvider(tmp_path)
    assert p.attest()["pid"]==1 and len(calls)==2
    path.write_text(json.dumps({**valid,"at":time.time()-20}),encoding="utf8")
    with pytest.raises(ModelError,match="缺少有效"):
        p.attest()


def test_queue_rejects_overflow_and_waiter_recovers(service,monkeypatch):
    p,_,_=service
    entered,release=Event(),Event()
    monkeypatch.setattr(p,"verify_identity",lambda *_:"unit")
    def fetch(*args,**kwargs):
        entered.set()
        assert release.wait(5)
        return {"raw":'{"ok":true}',"first_visible_s":.1,
                "end":{"model":MODEL,"done":True,"done_reason":"stop"}}
    monkeypatch.setattr(p,"_fetch",fetch)
    work=lambda: p.infer("queue",[],Probe,max_tokens=32)
    with ThreadPoolExecutor(5) as pool:
        futures=[pool.submit(work) for _ in range(5)]
        try:
            assert entered.wait(2)
            deadline=time.monotonic()+2
            while p.slots._value and time.monotonic()<deadline:
                time.sleep(.01)
            with pytest.raises(ModelError) as err:
                work()
            assert err.value.kind=="queue"
        finally:
            release.set()
        assert len({f.result().run_id for f in futures})==5


def test_transport_does_not_follow_redirect():
    requests=[]
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            requests.append(self.path)
            self.send_response(307)
            self.send_header("Location","/forbidden")
            self.end_headers()
    with ThreadingHTTPServer(("127.0.0.1",0),Handler) as server:
        thread=Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            with pytest.raises(ModelError,match="307"):
                ModelProvider._fetch(server.server_port,"/first",None,time.monotonic()+3)
        finally:
            server.shutdown()
            thread.join()
    assert requests==["/first"]
