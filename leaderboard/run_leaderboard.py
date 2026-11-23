#!/usr/bin/env python3
"""Regenerate the leaderboard from real scorecard outputs.

Reads targets.json (same directory by default). For every entry with a
non-null "target", runs the full Ordeal battery against that target,
writes the scorecards under <out>/results/<slug>/, and rebuilds
leaderboard.json + index.html from those scorecards. Entries with no
target, or whose target cannot run in this environment (for example an
llm: target with no API key in the environment), stay "unscored".
Scores are never estimated, copied by hand, or carried over from a
previous run: an entry is scored only by a run in this invocation.

Usage:
  python leaderboard/run_leaderboard.py [--config targets.json]
      [--out-dir DIR] [--only SLUG] [--jobs N]

Nothing here publishes anything; it only writes local files.
"""
import argparse, html, json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agentordeal.runner import run as agentordeal_run
from agentordeal.scorecard import write_formats
from agentordeal.trace import write_trace
from agentordeal import __version__

def slugify(name):
    return "".join(c if c.isalnum() else "-" for c in name.lower()).strip("-")

def render_html(data):
    rows = []
    for e in data["entries"]:
        if e["status"] == "scored":
            rows.append(f"<tr><td>{html.escape(e['name'])}</td><td>scored</td>"
                        f"<td>{e['score']}</td><td>{e['grade']}</td>"
                        f"<td><code>{html.escape(e.get('citation') or '-')}</code></td>"
                        f"<td>{html.escape(str(e.get('version') or '-'))}</td>"
                        f"<td>{html.escape(e.get('run_date') or '-')}</td>"
                        f"<td>{html.escape(e.get('note') or '')}</td></tr>")
        else:
            rows.append(f"<tr><td>{html.escape(e['name'])}</td><td>unscored</td>"
                        f"<td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>"
                        f"<td>{html.escape(e.get('note') or 'Not yet scored -- see methodology.')}</td></tr>")
    return ("<!doctype html><html><head><meta charset='utf-8'><title>AgentOrdeal Benchmark Results</title>"
            "<style>body{font-family:system-ui,sans-serif;max-width:1000px;margin:2rem auto;padding:0 1rem}"
            "table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:6px;text-align:left}</style>"
            "</head><body><h1>AgentOrdeal Benchmark Results</h1>"
            "<p><strong>A reproducible benchmark for autonomous agent security.</strong> "
            "This page is the public record of benchmark results produced under the AgentOrdeal "
            "Specification (see the agentordeal-spec repository). Every scored entry carries its full "
            "specification citation string -- specification version, battery version, seed, score -- so "
            "any result can be reproduced or disputed exactly.</p>"
            f"<p>Generated {html.escape(data.get('generated') or '')} by "
            f"<code>leaderboard/run_leaderboard.py</code> (agent-ordeal {html.escape(data.get('tool_version') or '')}). "
            "Scored entries come only from a pinned-version run of the battery in this repo; "
            "unscored entries have not been run. Critical findings follow the maintainer rerun window in "
            "<code>docs/METHODOLOGY.md</code> before publication. Source data: <code>leaderboard.json</code>.</p>"
            "<table><tr><th>Project</th><th>Status</th><th>Score</th><th>Grade</th><th>Citation</th><th>Target version</th>"
            f"<th>Run date</th><th>Note</th></tr>{''.join(rows)}</table></body></html>")

def build_leaderboard(config_path, out_dir, only=None, jobs=1):
    cfg = json.load(open(config_path))
    os.makedirs(out_dir, exist_ok=True)
    entries, report = [], {"scored": [], "unscored": [], "skipped": []}
    run_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for ent in cfg["entries"]:
        slug = ent.get("slug") or slugify(ent["name"])
        base = {"name": ent["name"], "url": ent.get("url"), "slug": slug,
                "status": "unscored", "score": None, "grade": None, "citation": None,
                "version": ent.get("version"), "note": ent.get("note") or
                "Placeholder -- not yet scored. Scores are published only after a pinned-version run and the maintainer rerun window in docs/METHODOLOGY.md."}
        target = ent.get("target")
        if not target or (only and slug != only):
            entries.append(base); report["unscored"].append(slug); continue
        try:
            card = agentordeal_run(target, jobs=jobs)
        except Exception as e:
            base["note"] = f"Not scored in the last pipeline run: target could not run ({type(e).__name__})."
            entries.append(base); report["skipped"].append({"slug": slug, "reason": str(e)[:200]}); continue
        rdir = os.path.join(out_dir, "results", slug)
        os.makedirs(rdir, exist_ok=True)
        write_formats(card, rdir, ["json", "html", "sarif", "junit", "badge"])
        write_trace(card, os.path.join(rdir, "trace.jsonl"))
        base.update({"status": "scored", "score": card["score"], "grade": card["grade"],
                     "citation": (card.get("specification") or {}).get("citation"),
                     "version": ent.get("version") or getattr(card, "target_version", None) or card.get("target"),
                     "target": target, "tool_version": __version__, "run_date": run_date,
                     "scorecard": f"results/{slug}/scorecard.json",
                     "note": ent.get("note") or f"Pinned run of agent-ordeal {__version__} against {target}."})
        entries.append(base); report["scored"].append(slug)
    scored = sorted([e for e in entries if e["status"] == "scored"], key=lambda e: -e["score"])
    from agentordeal.spec import SPEC_VERSION
    from agentordeal.scenarios import BATTERY_VERSION
    data = {"benchmark": "AgentOrdeal", "spec_version": SPEC_VERSION, "battery_version": BATTERY_VERSION,
            "methodology": "docs/METHODOLOGY.md", "tool_version": __version__,
            "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "note": "Scored entries come only from runs of leaderboard/run_leaderboard.py in this repo. Unscored entries have not been run; no score has been fabricated or estimated for any project.",
            "entries": scored + [e for e in entries if e["status"] != "scored"]}
    with open(os.path.join(out_dir, "leaderboard.json"), "w") as f:
        json.dump(data, f, indent=2)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(render_html(data))
    report["out_dir"] = out_dir
    return data, report

def export_scores(data, out_dir, export_path):
    """Write leaderboard data in the agentordeal-leaderboard repo's
    scores.json format to export_path: the same top-level and entry
    fields as leaderboard.json, plus a per-entry battery_version and,
    for scored entries, the per-category breakdown ("categories")
    read from that entry's scorecard.json under out_dir."""
    import copy
    out = copy.deepcopy(data)
    for e in out["entries"]:
        e["battery_version"] = data.get("battery_version")
        if e.get("status") == "scored" and e.get("scorecard"):
            card_path = os.path.join(out_dir, e["scorecard"])
            if os.path.exists(card_path):
                with open(card_path) as f:
                    card = json.load(f)
                e["categories"] = card.get("categories", {})
    parent = os.path.dirname(os.path.abspath(export_path))
    os.makedirs(parent, exist_ok=True)
    with open(export_path, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    return export_path

def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    p = argparse.ArgumentParser(description="Run the Ordeal battery against configured targets and regenerate the leaderboard")
    p.add_argument("--config", default=os.path.join(here, "targets.json"))
    p.add_argument("--out-dir", default=here)
    p.add_argument("--only", default=None, help="only run the entry with this slug")
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("--export", default=None, metavar="PATH",
                   help="also write the leaderboard data in the agentordeal-leaderboard scores.json format to PATH")
    a = p.parse_args(argv)
    data, report = build_leaderboard(a.config, a.out_dir, only=a.only, jobs=a.jobs)
    if a.export:
        export_scores(data, a.out_dir, a.export)
        report["export"] = a.export
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
