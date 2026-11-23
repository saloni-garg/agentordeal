from collections import Counter
from agentordeal.scenarios import load_scenarios
from agentordeal.runner import run

def test_total_at_least_80():
    assert len(load_scenarios())==91

def test_mcp_category_present():
    c=Counter(s["category"] for s in load_scenarios())
    assert c["mcp_security"]==8 and c["tool_misuse"]==19 and all(c[k]==16 for k in ["prompt_injection","data_exfiltration","memory_poisoning","goal_hijacking"])

def test_multiturn_scenarios_exist_and_run():
    mt=[s for s in load_scenarios() if s.get("turns")]
    assert len(mt)>=4
    card=run("demo-hardened", scenarios=mt); assert card["passed"]==len(mt)

def test_encoded_and_document_scenarios_exist():
    names=" ".join(s["name"].lower() for s in load_scenarios())
    assert "base64" in names and "document" in names and "rag" in names

def test_vulnerable_still_fails_hardened_still_passes():
    v=run("demo-vulnerable"); h=run("demo-hardened")
    assert v["score"]<50 and h["score"]==100.0 and h["passed"]==91

def test_mcp_scenarios_catch_vulnerable():
    scs=[s for s in load_scenarios() if s["category"]=="mcp_security"]
    card=run("demo-vulnerable", scenarios=scs); assert card["passed"]<8
