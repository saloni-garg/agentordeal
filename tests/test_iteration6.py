from agentordeal.runner import run_usefulness, combined_grade, run_full

def test_hardened_usefulness_high():
    u=run_usefulness("demo-hardened"); assert u["score"]>=80, u

def test_vulnerable_usefulness_high():
    assert run_usefulness("demo-vulnerable")["score"]>=80

def test_refuse_all_usefulness_zero():
    u=run_usefulness("demo-refuse-all"); assert u["score"]==0.0 and u["passed"]==0

def test_combined_grade_caps():
    assert combined_grade(100, 0)=="D"
    assert combined_grade(100, 60)=="B"
    assert combined_grade(100, 100)=="A"
    assert combined_grade(30, 100)=="F"

def test_run_full_fields():
    card=run_full("demo-hardened")
    assert card["combined_grade"]=="A" and card["usefulness"]["total"]==10 and card["score"]==100.0
