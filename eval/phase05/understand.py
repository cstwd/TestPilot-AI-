"""Seven prespecified source-understanding questions per project, no answers in model requests."""
import json
import time
from .audit import BASE, ALIAS, RAW, save
from .runtime import api
from .corpus import SPEC,get


def main():
    for name in SPEC:
        p=get(name)
        out=RAW/"understanding"/(name+".json")
        if out.exists():
            continue
        prompt={"files":{k:"\n".join(f"{i}: {line}" for i,line in enumerate(src.splitlines(),1))
                         for k,src in p["files"].items()}, "target":p["target"],"normal":p["normal"],
                "boundary":p["edge"],"exception_probe":p["probe"]}
        instruction=("Inspect the numbered Python files. Return a single JSON object with exactly these fields: "
        "functions (all top-level definitions in all files, sorted 'filename.py:name'), parameters (target function "
        "in declaration order: arrays of name, annotated type as string, Python source default as STRING, JSON null if required), "
        "return_value (actual value of normal call), branch_lines (sorted line numbers of explicit if, for, while, ternary "
        "statements in target only; omit comparisons without such a statement), boundary_value (actual value of boundary call), "
        "exception (actual exception class name for exception_probe or null), defect_line (line in subject.py with the "
        "implementation that conflicts with its docstring, or null if no conflict). Evaluate behavior as written.")
        req={"model":ALIAS,"messages":[{"role":"system","content":instruction},{"role":"user","content":json.dumps(prompt)}],
             "temperature":0.2,"seed":513,"max_tokens":350,"response_format":{"type":"json_object"}}
        t=time.monotonic()
        row={"request":req,"name":name,"raw":None}
        try:
            row["raw"]=api(BASE,"/v1/chat/completions",req)
            predicted=json.loads(row["raw"]["choices"][0]["message"]["content"])
            if not isinstance(predicted,dict):
                raise ValueError("Expected an object")
        except (OSError,KeyError,ValueError) as e:
            predicted={}
            row["error"]=str(e)
        # json type equality distinguishes boolean from integer or quoted numeric.
        row.update(expected=p["gold"],predicted=predicted,scores={k:int(k in predicted and
                   json.dumps(predicted[k],sort_keys=True)==json.dumps(v,sort_keys=True))
                   for k,v in p["gold"].items()},seconds=time.monotonic()-t)
        save(out,row)
        print(name,sum(row["scores"].values()),flush=True)

if __name__=="__main__":
    main()
