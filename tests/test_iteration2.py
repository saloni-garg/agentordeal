import json
import xml.etree.ElementTree as ET
from agentordeal.runner import run
from agentordeal.scorecard import to_sarif, to_junit
from agentordeal.cli import main

def test_sarif_structure():
    d=json.loads(to_sarif(run("demo-vulnerable")))
    assert d["version"]=="2.1.0" and d["runs"][0]["tool"]["driver"]["name"]=="agent-ordeal"
    res=d["runs"][0]["results"]; assert res and all(r["level"] in ("error","warning") for r in res)
    assert {r["ruleId"] for r in res} <= {r["id"] for r in d["runs"][0]["tool"]["driver"]["rules"]}

def test_sarif_clean_target_has_no_results():
    assert json.loads(to_sarif(run("demo-hardened")))["runs"][0]["results"]==[]

def test_junit_structure():
    root=ET.fromstring(to_junit(run("demo-vulnerable")))
    assert root.tag=="testsuite" and int(root.get("tests"))==91 and int(root.get("failures"))==int(root.get("tests"))-run("demo-vulnerable")["passed"]
    assert len(root.findall("testcase"))==91

def test_cli_formats(tmp_path):
    assert main(["run","--target","demo-vulnerable","--out",str(tmp_path),"--format","sarif","--format","junit"])==0
    assert (tmp_path/"scorecard.sarif").exists() and (tmp_path/"scorecard-junit.xml").exists()
    assert not (tmp_path/"scorecard.html").exists()
