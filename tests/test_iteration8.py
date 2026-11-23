import json
from agentordeal.runner import run
from agentordeal.trace import write_trace, read_trace, replay
from agentordeal.cli import main

def _trace(tmp_path, target="demo-vulnerable"):
    card=run(target); p=str(tmp_path/"t.jsonl"); write_trace(card, p); return p, card

def test_trace_written_per_scenario(tmp_path):
    p, card=_trace(tmp_path); entries=read_trace(p)
    assert len(entries)==91 and entries[0]["scenario_id"]=="PI-01" and "response" in entries[0]

def test_replay_matches_original(tmp_path):
    p, card=_trace(tmp_path); rep=replay(p)
    assert rep["score"]==card["score"] and rep["passed"]==card["passed"]

def test_replay_hardened(tmp_path):
    p, card=_trace(tmp_path, "demo-hardened"); assert replay(p)["grade"]=="A"

def test_cli_run_writes_trace_and_replay(tmp_path):
    out=tmp_path/"o"; assert main(["run","--target","demo-vulnerable","--out",str(out)])==0
    assert (out/"trace.jsonl").exists()
    assert main(["replay",str(out/"trace.jsonl"),"--fail-under","70"])==1
