"""Validation study scaffold: dataset shape and replay consistency."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VAL = os.path.join(ROOT, "validation")


def _incidents():
    with open(os.path.join(VAL, "incidents.json")) as f:
        return json.load(f)


def test_incident_dataset_shape():
    data = _incidents()
    incidents = data["incidents"]
    assert len(incidents) >= 12
    ids = [i["id"] for i in incidents]
    assert len(ids) == len(set(ids))
    required = {"id", "date", "source_name", "source_description", "verified",
                "incident_class", "categories", "asi", "attack_vector",
                "vulnerable_behaviour", "safe_behaviour", "agentordeal_scenarios",
                "coverage_status", "proposed_scenario"}
    from agentordeal.scenarios import load_scenarios
    known = {s["id"] for s in load_scenarios()}
    for inc in incidents:
        assert required <= set(inc), inc["id"]
        assert inc["coverage_status"] in ("covered", "partially_covered", "not_covered")
        for sid in inc["agentordeal_scenarios"]:
            assert sid in known, f"{inc['id']}: unknown scenario {sid}"
        if inc["coverage_status"] == "covered":
            assert inc["verified"] and inc["agentordeal_scenarios"]


def test_replay_report_matches_dataset():
    r = subprocess.run([sys.executable, os.path.join(VAL, "replay.py")],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stderr
    with open(os.path.join(VAL, "results.json")) as f:
        results = json.load(f)
    data = _incidents()
    denom = [i for i in data["incidents"]
             if i["verified"] and i["coverage_status"] == "covered"]
    assert results["verified_covered"] == len(denom)
    assert results["hits"] + len(results["misses"]) == len(denom)
    assert 0 <= results["hit_rate_percent"] <= 100
    report = open(os.path.join(VAL, "REPORT.md")).read()
    assert f"{results['hit_rate_percent']}%" in report
    for miss in results["misses"]:
        assert miss in report
