"""Iteration 21: benchmark repositioning -- specification field, citation
string, battery boundary, conformance to the specification calibration set."""
import json, os, re

import agentordeal
from agentordeal.runner import run
from agentordeal.scorecard import to_json, to_html, to_sarif, to_junit
from agentordeal.spec import citation_string, SPEC_VERSION

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC_REPO = os.path.join(ROOT, "..", "agentordeal-spec")
CITATION_RE = re.compile(r"^AgentOrdeal-1\.0 / battery=\d+\.\d+\.\d+ / seed=\S+ / score=\d+\.\d$")


def test_spec_version_and_citation_format():
    assert SPEC_VERSION == "1.0" and agentordeal.SPEC_VERSION == "1.0"
    assert citation_string(91.3, "1.2.0", 42) == "AgentOrdeal-1.0 / battery=1.2.0 / seed=42 / score=91.3"
    assert citation_string(100.0, "1.2.0") == "AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=100.0"


def test_scorecard_carries_specification():
    card = run("demo-hardened", seed=42)
    spec = card["specification"]
    assert spec["spec_version"] == "1.0"
    assert spec["battery_version"] == card["battery_version"]
    assert spec["seed"] == 42
    assert spec["citation"] == f"AgentOrdeal-1.0 / battery={card['battery_version']} / seed=42 / score=100.0"
    assert CITATION_RE.match(spec["citation"])
    assert card["metadata"]["spec_version"] == "1.0"
    assert card["metadata"]["citation"] == spec["citation"]


def test_citation_in_all_formats():
    card = run("demo-hardened", seed=7)
    cit = card["specification"]["citation"]
    assert cit in to_json(card)
    assert cit in to_html(card)
    sarif = json.loads(to_sarif(card))
    props = sarif["runs"][0]["properties"]
    assert props["citation"] == cit and props["specification"]["spec_version"] == "1.0"
    junit = to_junit(card)
    assert cit in junit and "agentordeal.spec_version" in junit


def test_cli_prints_citation(tmp_path, capsys):
    from agentordeal.cli import main
    out = str(tmp_path / "out")
    assert main(["run", "--target", "demo-hardened", "--out", out]) == 0
    text = capsys.readouterr().out
    assert "citation: AgentOrdeal-1.0 / battery=" in text
    card = json.load(open(os.path.join(out, "scorecard.json")))
    assert card["specification"]["citation"] in text


def test_battery_loader_reads_spec_format(tmp_path):
    from agentordeal.battery import load_battery
    from agentordeal.scenarios import load_scenarios
    bundled = load_battery()
    assert [s["id"] for s in bundled] == [s["id"] for s in load_scenarios()]
    one = dict(load_scenarios()[0])
    with open(tmp_path / "prompt_injection.json", "w") as f:
        json.dump([one], f)
    loaded = load_battery(str(tmp_path))
    assert loaded == [one]


def test_runner_conforms_to_specification_calibration():
    """The conformance test: the runner must reproduce the specification's
    expected verdicts exactly -- spec repo calibration when present,
    otherwise the pinned fixture (identical data, checked by the spec
    repo's own generator check)."""
    from agentordeal.calibration import check_conformance
    spec_cal = os.path.join(SPEC_REPO, "calibration", "calibration.json")
    if os.path.exists(spec_cal):
        with open(spec_cal) as f:
            expected = json.load(f)
    else:
        expected = None  # falls back to tests/fixtures/calibration.json
    assert check_conformance(expected) == []


def test_replay_card_carries_specification(tmp_path):
    from agentordeal.trace import write_trace, replay
    card = run("demo-hardened")
    trace = write_trace(card, str(tmp_path / "trace.jsonl"))
    rep = replay(trace)
    assert rep["specification"]["spec_version"] == "1.0"
    assert CITATION_RE.match(rep["specification"]["citation"])
