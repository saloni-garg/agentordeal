import json
from agentordeal.config import load_config
from agentordeal.runner import run, filter_scenarios
from agentordeal.scenarios import load_scenarios
from agentordeal.cli import main

def test_config_yaml_subset(tmp_path):
    p=tmp_path/"agentordeal.yaml"; p.write_text("target: demo-hardened\nfail_under: 70\ncategories: [prompt_injection, tool_misuse]\njobs: 4\nseverities:\n  - critical\n  - high\n")
    cfg=load_config(str(p)); assert cfg["target"]=="demo-hardened" and cfg["fail_under"]==70 and cfg["categories"]==["prompt_injection","tool_misuse"] and cfg["jobs"]==4 and cfg["severities"]==["critical","high"]

def test_config_json(tmp_path):
    p=tmp_path/"c.json"; p.write_text(json.dumps({"target":"demo-hardened"}))
    assert load_config(str(p))["target"]=="demo-hardened"

def test_filter_by_category():
    scs=filter_scenarios(load_scenarios(), categories=["prompt_injection"]); assert len(scs)==16 and all(s["category"]=="prompt_injection" for s in scs)

def test_filter_by_severity_and_id():
    assert all(s["severity"]=="critical" for s in filter_scenarios(load_scenarios(), severities=["critical"]))
    one=filter_scenarios(load_scenarios(), ids=["PI-01"]); assert len(one)==1 and one[0]["id"]=="PI-01"

def test_parallel_matches_sequential():
    a=run("demo-vulnerable"); b=run("demo-vulnerable", jobs=4)
    assert a["score"]==b["score"] and [r["id"] for r in a["results"]]==[r["id"] for r in b["results"]]

def test_cli_run_with_config(tmp_path):
    (tmp_path/"agentordeal.yaml").write_text("target: demo-hardened\nfail_under: 70\n")
    import os; old=os.getcwd(); os.chdir(tmp_path)
    try: assert main(["run","--out",str(tmp_path/"o")])==0
    finally: os.chdir(old)
    assert (tmp_path/"o"/"scorecard.json").exists()

def test_cli_category_filter(tmp_path, capsys):
    assert main(["run","--target","demo-hardened","--out",str(tmp_path),"--category","prompt_injection"])==0
    d=json.loads((tmp_path/"scorecard.json").read_text()); assert d["total"]==16
