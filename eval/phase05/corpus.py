"""Frozen evaluation inputs, independent behavior oracles, and guest-only dependency loading."""
import ast
import hashlib
import json
from .audit import LAB, ROOT
from backend.mutation_generator import make_plan

# Per target: normal call + observed behavior, boundary call + observed behavior,
# exceptional probe + exception class (or null), defect statement (or null).
SPEC = {
    "bonus": ("bonus","bonus(4)",5,"bonus(2, False)",2,"bonus(-1)","ValueError",None),
    "freight": ("freight","freight(6)",11,"freight(0)",5,"freight(None)","TypeError",None),
    "clamp": ("cap","cap(12, 7)",7,"cap(10)",10,"cap(None)","TypeError",None),
    "expiry": ("expired","expired(31)",True,"expired(30)",False,"expired(None)","TypeError","return age > limit"),
    "tax": ("tax","tax(200)",10,"tax(1)",0,"tax(None)","TypeError","return cents * RATE // 100"),
    "prefix": ("prefix_length","prefix_length([0, 1, None])",2,"prefix_length([])",0,"prefix_length(None)","TypeError",None),
    "pages": ("page_count","page_count(12)",2,"page_count(10)",2,"page_count(None)","TypeError","return items // PAGE_SIZE + 1"),
    "tier": ("tier","tier(51)","silver","tier(100)","gold","tier(None)","TypeError",None),
    "head": ("first","first([6], 7)",6,"first([], 7)",0,"first(None, 7)",None,"return 0"),
    "invoice": ("invoice","invoice([3,-1,4],2)",5,"invoice([2],3)",0,"invoice([None])","TypeError",None),
}
SEEDS=(513,727,941)


def get(name):
    target,call,returned,edge,boundary,probe,exception,bug=SPEC[name]
    if name=="bonus":
        files={"subject.py":(ROOT/"eval/phase04/bonus.py").read_text("utf8")}
    else:
        files={p.name:p.read_text("utf8") for p in sorted((LAB/"projects"/name).glob("*.py"))}
    source=files["subject.py"]
    fn=next(f for f in ast.parse(source).body if isinstance(f,ast.FunctionDef) and f.name==target)
    default=[None]*(len(fn.args.args)-len(fn.args.defaults))+[ast.unparse(x) for x in fn.args.defaults]
    gold={"functions":sorted(k+":"+n.name for k,s in files.items() for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)),
          "parameters":[[p.arg,ast.unparse(p.annotation),d] for p,d in zip(fn.args.args,default)],
          "return_value":returned,
          "branch_lines":sorted(n.lineno for n in ast.walk(fn) if isinstance(n,(ast.If,ast.For,ast.While,ast.IfExp))),
          "boundary_value":boundary,"exception":exception,
          "defect_line":next((i for i,s in enumerate(source.splitlines(),1) if s.strip()==bug),None)}
    return {"name":name,"target":target,"files":files,"source":source,"normal":call,"edge":edge,
            "probe":probe,"gold":gold,"manifest":make_plan(source,target)}


def staged(code, files):
    # F10 mounts one source and one test file. Compile the unchanged small dependency
    # modules in the guest before test imports; the primary file stays byte-identical.
    helpers={k[:-3]:v for k,v in files.items() if k!="subject.py"}
    if not helpers:
        return code
    tree=ast.parse(code)
    at=max((n.end_lineno for n in tree.body if isinstance(n,ast.ImportFrom) and n.module=="__future__"),default=0)
    loader="import sys as _tp_sys, types as _tp_types\n"
    for name,src in helpers.items():
        loader+=f"_tp_m = _tp_types.ModuleType({name!r})\n_tp_m.__file__ = {name+'.py'!r}\n"
        loader+=f"_tp_sys.modules[{name!r}] = _tp_m\nexec(compile({src!r}, _tp_m.__file__, 'exec'), _tp_m.__dict__)\n"
    lines=code.splitlines(keepends=True)
    return "".join(lines[:at])+loader+"\n"+"".join(lines[at:])


def evidence_contract(p):
    target=p["target"]
    tests=f"import pytest\nfrom subject import {target}\n\ndef test_behavior_reference():\n"
    for call,key in ((p["normal"],"return_value"),(p["edge"],"boundary_value")):
        tests+=f"    assert {call} == {p['gold'][key]!r}\n"
    if p["gold"]["exception"]:
        tests+=f"    with pytest.raises({p['gold']['exception']}):\n        {p['probe']}\n"
    else:
        tests+=f"    {p['probe']}\n"
    return staged(tests,p["files"])


def freeze():
    return {"seeds":SEEDS,"projects":{name: {
        "files":{k:hashlib.sha256(s.encode()).hexdigest() for k,s in p["files"].items()},
        "manifest":p["manifest"],"rubric":p["gold"]}
        for name in SPEC for p in [get(name)]}}
