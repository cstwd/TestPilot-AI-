"""Measure real context occupancy under the same supervisor guard."""
import argparse
import json
from pathlib import Path
import time

from backend.model_provider import ModelError, provider
from eval.phase06.stability import Check


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--context",type=int,choices=(4096,8192,16384),required=True)
    a=p.parse_args()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open("x",encoding="utf8") as file:
        for n in range(2):
            sentinel=1123+n
            text="Process the full text. Disregard padding."+" a"*int(a.context*.80)+f"\nReturn {{\"answer\": {sentinel}}}."
            start=time.monotonic()
            try:
                result=provider.infer("context-pressure", [{"role":"user","content":text}],Check,max_tokens=40)
                tokens=max((r["tokens_in"] or 0 for r in result.attempts),default=0)
                row={"context":a.context,"tokens_in":tokens,"answer":result.value.answer,
                     "ok":tokens>=.70*a.context and result.value.answer==sentinel,
                     "run_id":result.run_id,"attempts":result.attempts}
            except ModelError as e:
                row={"context":a.context,"ok":False,"error":e.kind,"reason":str(e),"run_id":e.run_id,
                     "attempts":e.attempts}
            file.write(json.dumps({"round":n,"wall_s":time.monotonic()-start,**row},ensure_ascii=False)+"\n")
            file.flush()
            if row.get("error") in {"resource","unavailable"}:
                break

if __name__=="__main__":
    main()
