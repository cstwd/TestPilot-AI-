"""Archive consecutive real requests without restarting or changing the model."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import time

from pydantic import Field
from backend.model_protocol import Protocol
from backend.model_provider import ModelError, provider


class Check(Protocol):
    answer: int = Field(ge=0)


def run(i):
    expected = 801 + i*2
    started = time.monotonic()
    try:
        result = provider.infer("stability",[{"role":"user","content":
            f"Calculate {621+i} plus {180+i}. Return only a JSON object with integer key answer."}],
            Check,max_tokens=32)
        return {"round":i,"expected":expected,"actual":result.value.answer,"ok":result.value.answer==expected,
                "run_id":result.run_id,"attempts":result.attempts,"seconds":time.monotonic()-started}
    except ModelError as exc:
        return {"round":i,"ok":False,"kind":exc.kind,"reason":str(exc),"run_id":exc.run_id,
                "attempts":exc.attempts,"seconds":time.monotonic()-started}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--count",type=int,default=100)
    p.add_argument("--interval",type=float,default=1)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--concurrent",type=int,default=1)
    a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x",encoding="utf8") as out, ThreadPoolExecutor(a.concurrent) as pool:
        for start in range(0,a.count,a.concurrent):
            for row in pool.map(run,range(start,min(start+a.concurrent,a.count))):
                out.write(json.dumps(row,ensure_ascii=False)+"\n")
                out.flush()
                if row.get("kind")=="resource":
                    return
            if a.interval:
                time.sleep(a.interval)

if __name__=="__main__":
    main()
