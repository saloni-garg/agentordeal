import argparse, json, os, sys
from .runner import run, filter_scenarios
from .config import load_config, get as cfg_get
from .scenarios import load_scenarios as _load
from .scorecard import to_json, to_html, write_formats
from .scenarios import load_scenarios

def _write(card, out, formats=("json","html")):
    os.makedirs(out, exist_ok=True)
    write_formats(card, out, list(formats))
    from .trace import write_trace
    write_trace(card, os.path.join(out, "trace.jsonl"))
    print(f"{card['target']}: grade {card['grade']} score {card['score']}/100 passed {card['passed']}/{card['total']}")
    spec = card.get("specification") or {}
    if spec.get("citation"): print(f"citation: {spec['citation']}")
    return card
def main(argv=None):
    try:
        return _main(argv)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        print("hint: targets are demo-vulnerable, demo-hardened, demo-refuse-all, "
              "http(s)://<agent endpoint>, or llm:<model>. See README quickstart.", file=sys.stderr)
        return 2
    except FileNotFoundError as e:
        print(f"error: file not found: {e.filename or e}", file=sys.stderr)
        print("hint: check the path, or run from the repo root; scorecards and traces are written under --out.", file=sys.stderr)
        return 2

def _main(argv=None):
    p=argparse.ArgumentParser(prog="agentordeal", description="Reference implementation of the AgentOrdeal Specification -- the benchmark that measures whether autonomous agents are actually safe")
    sub=p.add_subparsers(dest="cmd", required=True)
    lp=sub.add_parser("list"); lp.add_argument("--garak", default=None, help="comma-separated garak probe names; list only the scenarios they map to")
    ip=sub.add_parser("import-promptfoo"); ip.add_argument("file"); ip.add_argument("--out", default="imported-scenarios.json")
    ep=sub.add_parser("export-promptfoo"); ep.add_argument("scorecard"); ep.add_argument("--out", default=None)
    cp=sub.add_parser("coverage"); cp.add_argument("--format", choices=["text","json"], default="text")
    dp=sub.add_parser("diff"); dp.add_argument("a"); dp.add_argument("b"); dp.add_argument("--fail-on-regression", action="store_true")
    rp=sub.add_parser("replay"); rp.add_argument("trace"); rp.add_argument("--out", default=None); rp.add_argument("--fail-under", type=float, default=None)
    sm=sub.add_parser("scan-mcp"); sm.add_argument("--command", required=True); sm.add_argument("--out", default=None); sm.add_argument("--fail-on", choices=["critical","high","medium","low"], default=None)
    b=sub.add_parser("badge"); b.add_argument("--target", default=None); b.add_argument("--scorecard", default=None); b.add_argument("--out", default="badge.svg")
    q=sub.add_parser("quickstart"); q.add_argument("--out", default="out")
    dm=sub.add_parser("demo"); dm.add_argument("--out", default="out")
    r=sub.add_parser("run"); r.add_argument("--target", default=None); r.add_argument("--out", default=None); r.add_argument("--fail-under", type=float, default=None)
    r.add_argument("--config", default=None); r.add_argument("--category", action="append", default=None); r.add_argument("--severity", action="append", default=None); r.add_argument("--scenario", action="append", default=None); r.add_argument("--jobs", type=int, default=None); r.add_argument("--format", action="append", default=None, dest="formats"); r.add_argument("--usefulness", action="store_true"); r.add_argument("--plugin-dir", default=None); r.add_argument("--timeout", type=float, default=None); r.add_argument("--retries", type=int, default=0); r.add_argument("--progress", action="store_true")
    r.add_argument("--garak", default=None, help="comma-separated garak probe names; run only the scenarios they map to")
    r.add_argument("--extra-scenarios", default=None, help="JSON file of extra scenarios (e.g. from import-promptfoo) merged into the run")
    r.add_argument("--seed", type=int, default=None, help="deterministic seed recorded in run metadata; also fixes scenario order")
    m=sub.add_parser("mcp"); m.add_argument("--command", required=True); m.add_argument("--out", default="out"); m.add_argument("--fail-under", type=float, default=None)
    a=p.parse_args(argv)
    if a.cmd=="import-promptfoo":
        from .interop import import_promptfoo
        scs, unc = import_promptfoo(a.file)
        json.dump(scs, open(a.out,"w"), indent=2)
        print(f"imported {len(scs)} scenarios -> {a.out}")
        for u in unc: print(f"unconverted: test {u['test']} ({u['type']}): {u['reason']}")
        return 0
    if a.cmd=="export-promptfoo":
        from .interop import export_promptfoo
        card=json.load(open(a.scorecard))
        out=json.dumps(export_promptfoo(card), indent=2)
        if a.out: open(a.out,"w").write(out); print(f"promptfoo results -> {a.out}")
        else: print(out)
        return 0
    if a.cmd=="coverage":
        from .coverage import coverage_report, format_text
        rep=coverage_report()
        print(json.dumps(rep, indent=2) if a.format=="json" else format_text(rep))
        return 0
    if a.cmd=="diff":
        from .diff import diff_cards, format_diff
        d=diff_cards(json.load(open(a.a)), json.load(open(a.b)))
        print(format_diff(d))
        return 1 if (a.fail_on_regression and d["regressions"]) else 0
    if a.cmd=="replay":
        from .trace import replay as _replay
        card=_replay(a.trace)
        print(f"replay: grade {card['grade']} score {card['score']}/100 passed {card['passed']}/{card['total']}")
        if a.out:
            os.makedirs(a.out, exist_ok=True); to_json(card, os.path.join(a.out,"scorecard.json"))
        return 1 if (a.fail_under is not None and card["score"] < a.fail_under) else 0
    if a.cmd=="scan-mcp":
        from .mcp_scan import scan_server
        result=scan_server(a.command)
        print(json.dumps(result, indent=2))
        if a.out: open(a.out,"w").write(json.dumps(result, indent=2))
        if a.fail_on:
            rank={"critical":0,"high":1,"medium":2,"low":3}
            if any(rank[f["severity"]] <= rank[a.fail_on] for f in result["findings"]): return 1
        return 0
    if a.cmd=="badge":
        from .scorecard import to_badge_svg, badge_markdown
        if a.scorecard: card=json.load(open(a.scorecard))
        elif a.target: card=run(a.target)
        else: p.error("badge requires --target or --scorecard")
        to_badge_svg(card, a.out)
        print(badge_markdown(card)); print(f"Badge written to {a.out}")
        return 0
    if a.cmd=="list":
        from .battery import load_battery
        scs=load_battery()
        if a.garak:
            from .interop import garak_selection
            ids, unknown = garak_selection([x for x in a.garak.split(",") if x.strip()], scs)
            scs=[s for s in scs if s["id"] in set(ids)]
            for u in unknown: print(f"unknown garak probe: {u}", file=sys.stderr)
        for s in scs: print(f"{s['id']}\t{s['category']}\t{s['severity']}\t{s['owasp_asi']}\t{s['name']}")
        print(f"Total: {len(scs)} scenarios"); return 0
    if a.cmd=="demo":
        # One command, no key, no target: the full story in under a minute.
        v=_write(run("demo-vulnerable"), os.path.join(a.out,"demo-vulnerable"))
        h=_write(run("demo-hardened"), os.path.join(a.out,"demo-hardened"))
        print(f"Comparison: vulnerable {v['score']} ({v['grade']}) vs hardened {h['score']} ({h['grade']})")
        ex=os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_server.py")
        if os.path.exists(ex):
            from .mcp_scan import scan_server
            res=scan_server(f"{sys.executable} {ex}")
            print(f"MCP example server scan: {len(res.get('tool_names',[]))} tools, {len(res.get('findings',[]))} findings")
        print(f"Demo scorecards written to {a.out}/ -- open demo-hardened/scorecard.html for the full report.")
        print("Next: agentordeal run --target http://localhost:8000/agent --out out   |   agentordeal mcp --command \"<your MCP server>\"")
        return 0
    if a.cmd=="quickstart":
        v=_write(run("demo-vulnerable"), os.path.join(a.out,"demo-vulnerable"))
        h=_write(run("demo-hardened"), os.path.join(a.out,"demo-hardened"))
        print(f"Comparison: vulnerable {v['score']} ({v['grade']}) vs hardened {h['score']} ({h['grade']})")
        print(f"Scorecards written to {a.out}/"); return 0
    if a.cmd=="run":
        cfg=load_config(a.config)
        target=a.target or cfg_get(cfg,"target")
        if not target: p.error("run requires --target or target in config")
        out=a.out or cfg_get(cfg,"out","output_dir", default="out")
        fail_under=a.fail_under if a.fail_under is not None else cfg_get(cfg,"fail_under","fail-under")
        cats=a.category or cfg_get(cfg,"categories","category")
        sevs=a.severity or cfg_get(cfg,"severities","severity")
        ids=a.scenario or cfg_get(cfg,"ids","scenario","scenarios")
        jobs=a.jobs or cfg_get(cfg,"jobs", default=1)
        if a.plugin_dir or cfg_get(cfg,"plugin_dir"):
            from .plugins import load_with_plugins
            all_scs=load_with_plugins(a.plugin_dir or cfg_get(cfg,"plugin_dir"))
        else:
            from .battery import load_battery
            all_scs=load_battery()
        if a.extra_scenarios:
            all_scs = list(all_scs) + json.load(open(a.extra_scenarios))
        if a.garak:
            from .interop import garak_selection
            gids, unknown = garak_selection([x for x in a.garak.split(",") if x.strip()], all_scs)
            for u in unknown: print(f"unknown garak probe: {u}", file=sys.stderr)
            ids = gids if not ids else [i for i in ids if i in set(gids)]
        scs=filter_scenarios(all_scs, cats, sevs, ids)
        fmts=a.formats or cfg_get(cfg,"formats", default=["json","html"])
        if isinstance(fmts,str): fmts=[fmts]
        if a.usefulness:
            from .runner import run_full
            card = run_full(target, scenarios=scs, jobs=int(jobs), timeout=a.timeout, retries=a.retries, seed=a.seed); _write(card, out, fmts)
            print(f"usefulness: {card['usefulness']['score']}/100 ({card['usefulness']['passed']}/{card['usefulness']['total']}) combined grade {card['combined_grade']}")
        else:
            prog=(lambda sc: print(f"  ... {sc['id']}", file=sys.stderr)) if a.progress else None
            card=_write(run(target, scenarios=scs, jobs=int(jobs), timeout=a.timeout, retries=a.retries, progress=prog, seed=a.seed), out, fmts)
        return 1 if (fail_under is not None and card["score"] < float(fail_under)) else 0
    if a.cmd=="mcp":
        from .adapters.mcp import MCPAdapter
        ad=MCPAdapter(a.command)
        try: print("Tools:", [t.get("name") for t in ad.probe()])
        except Exception as e: print(f"MCP probe: {e}")
        card=_write(run(ad), a.out)
        return 1 if (a.fail_under is not None and card["score"] < a.fail_under) else 0
    return 0
if __name__=="__main__": raise SystemExit(main())
