import json, subprocess, sys
import pytest
from agentordeal.scenarios import load_scenarios, CATEGORIES
from agentordeal.runner import run, grade_for
from agentordeal.scorecard import to_json, to_html
from agentordeal.adapters.demo import VulnerableDemoAgent, HardenedDemoAgent
from agentordeal.adapters.base import normalize_response, AgentResponse
from agentordeal.adapters.mcp import MCPClient
from agentordeal.cli import main

def test_scenarios_count_40():
    assert len(load_scenarios()) >= 80
def test_scenarios_unique_ids():
    ids=[s["id"] for s in load_scenarios()]; assert len(ids)==len(set(ids))
def test_scenarios_eight_per_category():
    from collections import Counter
    c=Counter(s["category"] for s in load_scenarios())
    assert all(c[k]>=8 for k in CATEGORIES)
def test_scenarios_shape():
    for s in load_scenarios():
        for k in ["id","category","severity","name","description","owasp_asi","prompt","detector"]:
            assert s.get(k), (s.get("id"), k)
        assert s["severity"] in {"critical","high","medium","low"}
        assert s["owasp_asi"].startswith("ASI")
def test_vulnerable_fails_meaningful_subset():
    card=run("demo-vulnerable"); assert card["passed"] < 30 and card["score"] < 50
def test_vulnerable_fails_exfiltration_and_injection():
    card=run("demo-vulnerable")
    assert card["categories"]["data_exfiltration"]["score"] < 60
    assert card["categories"]["prompt_injection"]["score"] < 60
def test_hardened_scores_higher_than_vulnerable():
    assert run("demo-hardened")["score"] > run("demo-vulnerable")["score"]
def test_hardened_scores_well():
    card=run("demo-hardened"); assert card["score"] >= 90 and card["grade"]=="A"
def test_grade_boundaries():
    assert grade_for(95)=="A" and grade_for(85)=="B" and grade_for(75)=="C" and grade_for(65)=="D" and grade_for(10)=="F"
def test_scorecard_json(tmp_path):
    card=run("demo-hardened"); p=tmp_path/"s.json"; to_json(card, str(p))
    d=json.loads(p.read_text()); assert d["grade"]==card["grade"] and d["total"]==len(load_scenarios())
def test_scorecard_html_self_contained(tmp_path):
    card=run("demo-vulnerable"); h=to_html(card, str(tmp_path/"s.html"))
    assert "Grade" in h and "http://" not in h.replace("https://evil.example","") and "<style" in h
    assert "Remediation" in h or "remediation" in h.lower()
def test_cli_list(capsys):
    assert main(["list"])==0; out=capsys.readouterr().out; assert "PI-01" in out and f"Total: {len(load_scenarios())}" in out
def test_cli_quickstart(tmp_path):
    assert main(["quickstart","--out",str(tmp_path)])==0
    assert (tmp_path/"demo-vulnerable"/"scorecard.json").exists()
    assert (tmp_path/"demo-hardened"/"scorecard.html").exists()
def test_cli_run_fail_under(tmp_path):
    assert main(["run","--target","demo-vulnerable","--out",str(tmp_path),"--fail-under","70"])==1
    assert main(["run","--target","demo-hardened","--out",str(tmp_path),"--fail-under","70"])==0
def test_normalize_dict_response():
    r=normalize_response({"text":"hi","tool_calls":[{"name":"x","arguments":{}}],"memory_writes":[]})
    assert isinstance(r, AgentResponse) and r.text=="hi"
def test_callable_target():
    card=run(lambda prompt, context=None: {"text":"ok","tool_calls":[],"memory_writes":[]})
    assert card["score"]==100.0
def test_mcp_client_module_present():
    assert MCPClient is not None
