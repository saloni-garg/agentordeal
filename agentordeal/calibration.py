"""Calibration set: pinned expected verdicts for the reference agents.

The three demo agents are deterministic, so their verdict on every
scenario is a fact that can be pinned. tests/fixtures/calibration.json
holds those facts; the calibration test re-runs all three agents and
asserts an exact match. If a detector, a scenario, or a demo agent
changes behaviour, the test fails and the change must be made
deliberately: regenerate with `python -m agentordeal.calibration --write`
and bump the battery version (docs/BATTERY.md).

Run as a module:
  python -m agentordeal.calibration --write [path]
"""
import json, os, sys

AGENTS = ["demo-vulnerable", "demo-hardened", "demo-refuse-all"]
DEFAULT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "tests", "fixtures", "calibration.json")

def build_calibration():
    from .runner import run, run_usefulness
    from .scenarios import BATTERY_VERSION
    from . import __version__
    out = {"battery_version": BATTERY_VERSION, "tool_version": __version__,
           "agents": {}, "usefulness": {}}
    for name in AGENTS:
        card = run(name)
        out["agents"][name] = {
            "score": card["score"], "grade": card["grade"],
            "verdicts": {r["id"]: bool(r["passed"]) for r in card["results"]}}
        u = run_usefulness(name)
        out["usefulness"][name] = {"score": u["score"],
                                   "verdicts": {r["id"]: bool(r["passed"]) for r in u["results"]}}
    return out

def check_conformance(expected=None, agents=None):
    """Conformance check against the specification's calibration set.

    Runs the reference agents and compares every verdict, score, and
    grade against `expected` (a calibration dict as produced by
    build_calibration(), e.g. the spec repo's calibration/calibration.json
    or tests/fixtures/calibration.json). Returns a list of mismatch
    strings; an empty list means this implementation conforms to the
    specification's calibration protocol for the pinned battery.
    """
    if expected is None:
        with open(DEFAULT_PATH) as f: expected = json.load(f)
    from .runner import run, run_usefulness
    mismatches = []
    for name in (agents or AGENTS):
        exp = expected.get("agents", {}).get(name)
        if exp is None:
            mismatches.append(f"{name}: no calibration entry"); continue
        card = run(name)
        got = {r["id"]: bool(r["passed"]) for r in card["results"]}
        if got != exp["verdicts"]:
            diff = [sid for sid in exp["verdicts"] if got.get(sid) != exp["verdicts"][sid]]
            mismatches.append(f"{name}: verdict drift on {diff}")
        if card["score"] != exp["score"] or card["grade"] != exp["grade"]:
            mismatches.append(f"{name}: score/grade {card['score']}/{card['grade']} != calibration {exp['score']}/{exp['grade']}")
        uexp = expected.get("usefulness", {}).get(name)
        if uexp is not None:
            u = run_usefulness(name)
            ugot = {r["id"]: bool(r["passed"]) for r in u["results"]}
            if ugot != uexp["verdicts"]:
                mismatches.append(f"{name}: usefulness verdict drift")
    return mismatches

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    path = DEFAULT_PATH
    if "--write" in argv:
        argv.remove("--write")
        if argv: path = argv[0]
        cal = build_calibration()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f: json.dump(cal, f, indent=1, sort_keys=True)
        print(f"calibration written to {path} (battery {cal['battery_version']})")
        return 0
    print(__doc__)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
