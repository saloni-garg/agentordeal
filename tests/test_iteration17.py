def test_battery_bumped():
    from agentordeal.scenarios import BATTERY_VERSION, load_scenarios
    assert BATTERY_VERSION == "1.2.0"
    assert len(load_scenarios()) == 91

def test_no_thin_asi():
    from agentordeal.coverage import coverage_report
    rep = coverage_report()
    assert all(v["count"] >= 3 for v in rep["owasp_asi"].values()), rep["owasp_asi"]
    assert rep["owasp_asi"]["ASI05"]["count"] >= 4

def test_new_scenarios_shape():
    from agentordeal.scenarios import load_scenarios
    by = {s["id"]: s for s in load_scenarios()}
    for i in ("TM-17","TM-18","TM-19"):
        assert by[i]["owasp_asi"] == "ASI05" and by[i]["detector"]
