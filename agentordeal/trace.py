"""Trace recording (JSONL) and deterministic replay."""
import json
from .adapters.base import normalize_response
from .detectors import check
from .scenarios import load_scenarios
from .runner import WEIGHTS, grade_for

def write_trace(card, path):
    with open(path, "w") as f:
        for r in card["results"]:
            if "trace" in r: f.write(json.dumps(r["trace"]) + "\n")
    return path

def read_trace(path):
    return [json.loads(line) for line in open(path) if line.strip()]

def replay(path):
    """Re-score a recorded trace with the current detectors. No target contact."""
    by_id = {s["id"]: s for s in load_scenarios()}
    entries = read_trace(path); results = []
    for e in entries:
        sc = by_id.get(e["scenario_id"])
        if sc is None:
            results.append({"id": e["scenario_id"], "passed": None, "note": "scenario not in current battery"}); continue
        passed, reasons = check(sc, normalize_response(e["response"]))
        results.append({"id": sc["id"], "category": sc["category"], "severity": sc["severity"],
                        "name": sc["name"], "owasp_asi": sc.get("owasp_asi"), "passed": passed, "reasons": reasons})
    scored = [x for x in results if x.get("passed") is not None]
    total = sum(WEIGHTS[x["severity"]] for x in scored) or 1
    earned = sum(WEIGHTS[x["severity"]] for x in scored if x["passed"])
    score = round(100*earned/total, 1)
    cats = {}
    for x in scored:
        c = cats.setdefault(x["category"], {"passed": 0, "total": 0})
        c["total"] += 1; c["passed"] += int(x["passed"])
    for c in cats:
        sub = [x for x in scored if x["category"] == c]
        t = sum(WEIGHTS[x["severity"]] for x in sub) or 1
        e = sum(WEIGHTS[x["severity"]] for x in sub if x["passed"])
        cats[c] = {"score": round(100*e/t, 1), "passed": cats[c]["passed"], "total": cats[c]["total"]}
    from .scenarios import BATTERY_VERSION
    from .spec import specification_block
    return {"target": "replay:" + str(path), "score": score, "grade": grade_for(score),
            "total": len(scored), "passed": sum(x["passed"] for x in scored),
            "categories": cats, "results": results, "tool": "agent-ordeal", "version": "replay",
            "battery_version": BATTERY_VERSION,
            "specification": specification_block(score, BATTERY_VERSION, None)}
