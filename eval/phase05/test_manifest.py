from pathlib import Path
import json
import pytest
from backend.mutation_generator import make_plan, apply_site
from .corpus import get

@pytest.mark.parametrize("rhs",["None","node","notary"])
def test_identity_insertion(rhs):
    source=f"def f(value, {rhs if rhs!='None' else 'other'}):\n    return value is {rhs}\n"
    plan=make_plan(source,"f")
    site,=[m for m in plan if m["family"]=="comparison"]
    assert apply_site(source,site)==source.replace(" is "," is not ")
    assert site["after"]=="is not"

def test_bonus_manifest_identical():
    old=Path(__file__).resolve().parents[2]/"reports/phase04/ai-hardened-campaign.json"
    assert get("bonus")["manifest"]==json.loads(old.read_bytes())["manifest"]
