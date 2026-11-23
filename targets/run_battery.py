#!/usr/bin/env python3
"""Run the full AgentOrdeal battery against one framework target harness
and write its scorecard under leaderboard/results/<slug>/.

Usage: python targets/run_battery.py <module> <slug> [--jobs N]
Run via the DeepSeek launcher so the API key surrogate is in the env.
The score printed is the real run's score; nothing is estimated.
"""
import argparse, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, HERE)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("module"); ap.add_argument("slug")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--timeout", type=float, default=240)
    a = ap.parse_args()
    mod = __import__(a.module + "_agent")
    agent = mod.build()
    from agentordeal.runner import run
    from agentordeal.scorecard import write_formats
    from agentordeal.trace import write_trace
    card = run(agent, jobs=a.jobs, timeout=a.timeout)
    out = os.path.join(ROOT, "leaderboard", "results", a.slug)
    os.makedirs(out, exist_ok=True)
    write_formats(card, out, ["json", "html", "sarif", "junit", "badge"])
    write_trace(card, os.path.join(out, "trace.jsonl"))
    errs = sum(1 for r in card["results"] if r["reasons"] and r["reasons"][0].startswith("target error"))
    print(json.dumps({"slug": a.slug, "score": card["score"], "grade": card["grade"],
                      "passed": card["passed"], "total": card["total"],
                      "target_errors": errs,
                      "citation": (card.get("specification") or {}).get("citation")}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
