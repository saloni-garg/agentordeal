"""Iteration 14: coverage map, battery versioning, calibration set."""
import json, os
from agentordeal.coverage import coverage_report, format_text
from agentordeal.runner import run, run_usefulness
from agentordeal.scenarios import BATTERY_VERSION

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "calibration.json")

def test_coverage_totals_and_frameworks():
    rep = coverage_report()
    assert rep["total_scenarios"] == 91
    assert rep["battery_version"] == BATTERY_VERSION
    assert set(rep["owasp_asi"]) == {f"ASI{i:02d}" for i in range(1, 11)}
    assert sum(v["count"] for v in rep["owasp_asi"].values()) == 91
    assert rep["gaps"] == []                      # every ASI code has >=1 scenario
    assert rep["thin"] == []                       # thin spot closed in battery 1.2.0 (iteration 17)
    assert rep["owasp_asi"]["ASI05"]["count"] == 4

def test_atlas_mapping_present_and_honest():
    rep = coverage_report()
    assert "AML.T0051.000" in rep["mitre_atlas"]
    assert "AML.T0057" in rep["mitre_atlas"]
    # analogue mappings are flagged, not passed off as exact
    assert rep["mitre_atlas"]["AML.T0020"]["mapping"] == "analogue"
    txt = format_text(rep)
    assert "ASI05" in txt and "Thin" in txt

def test_battery_version_stamped_on_scorecard():
    card = run("demo-hardened")
    assert card["battery_version"] == BATTERY_VERSION
    assert card["results"][0]["atlas"]  # per-result ATLAS techniques

def test_calibration_matches_reference_agents():
    cal = json.load(open(FIXTURE))
    assert cal["battery_version"] == BATTERY_VERSION
    for name, expected in cal["agents"].items():
        card = run(name)
        got = {r["id"]: bool(r["passed"]) for r in card["results"]}
        assert got == expected["verdicts"], f"{name}: verdict drift vs calibration"
        assert card["score"] == expected["score"] and card["grade"] == expected["grade"]
    for name, expected in cal["usefulness"].items():
        u = run_usefulness(name)
        got = {r["id"]: bool(r["passed"]) for r in u["results"]}
        assert got == expected["verdicts"], f"{name}: usefulness drift vs calibration"

def test_cli_coverage(tmp_path, capsys):
    from agentordeal.cli import main
    assert main(["coverage"]) == 0
    out = capsys.readouterr().out
    assert "OWASP Agentic" in out and "MITRE ATLAS" in out
    assert main(["coverage", "--format", "json"]) == 0
    rep = json.loads(capsys.readouterr().out)
    assert rep["total_scenarios"] == 91
