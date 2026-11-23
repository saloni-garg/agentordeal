"""Scorecard diffing: regressions and fixes between two runs."""

def diff_cards(a, b):
    """Compare scorecard A (baseline) to scorecard B (candidate)."""
    ra = {r["id"]: r for r in a["results"]}
    rb = {r["id"]: r for r in b["results"]}
    regressions, fixes = [], []
    for sid in sorted(set(ra) & set(rb)):
        if ra[sid]["passed"] and not rb[sid]["passed"]:
            regressions.append({"id": sid, "category": rb[sid]["category"],
                                "severity": rb[sid]["severity"], "name": rb[sid]["name"],
                                "reasons": rb[sid].get("reasons") or []})
        elif not ra[sid]["passed"] and rb[sid]["passed"]:
            fixes.append({"id": sid, "category": rb[sid]["category"],
                          "severity": rb[sid]["severity"], "name": rb[sid]["name"]})
    cats = {}
    for c in sorted(set(a.get("categories") or {}) | set(b.get("categories") or {})):
        sa = (a.get("categories") or {}).get(c, {}).get("score")
        sb = (b.get("categories") or {}).get(c, {}).get("score")
        cats[c] = {"a": sa, "b": sb,
                   "delta": None if (sa is None or sb is None) else round(sb - sa, 1)}
    return {"target_a": a.get("target"), "target_b": b.get("target"),
            "score_a": a.get("score"), "score_b": b.get("score"),
            "score_delta": round(b.get("score", 0) - a.get("score", 0), 1),
            "grade_a": a.get("grade"), "grade_b": b.get("grade"),
            "battery_a": a.get("battery_version") or (a.get("metadata") or {}).get("battery_version"),
            "battery_b": b.get("battery_version") or (b.get("metadata") or {}).get("battery_version"),
            "categories": cats,
            "regressions": regressions, "fixes": fixes,
            "added": sorted(set(rb) - set(ra)), "removed": sorted(set(ra) - set(rb))}

def format_diff(d):
    lines = [f"Score: {d['score_a']} ({d['grade_a']}) -> {d['score_b']} ({d['grade_b']}) "
             f"({d['score_delta']:+})",
             f"Targets: {d['target_a']} -> {d['target_b']}",
             f"Battery: {d['battery_a']} -> {d['battery_b']}"]
    if d["battery_a"] != d["battery_b"]:
        lines.append("WARNING: battery versions differ; scores are not directly comparable (docs/BATTERY.md).")
    lines.append(f"Regressions (pass -> fail): {len(d['regressions'])}")
    for r in d["regressions"]:
        lines.append(f"  REGRESSED {r['id']} [{r['severity']}] {r['name']}: {'; '.join(r['reasons']) or '-'}")
    lines.append(f"Fixes (fail -> pass): {len(d['fixes'])}")
    for r in d["fixes"]:
        lines.append(f"  FIXED {r['id']} [{r['severity']}] {r['name']}")
    if d["added"]: lines.append(f"Added scenarios: {', '.join(d['added'])}")
    if d["removed"]: lines.append(f"Removed scenarios: {', '.join(d['removed'])}")
    lines.append("Categories:")
    for c, v in d["categories"].items():
        lines.append(f"  {c}: {v['a']} -> {v['b']} ({v['delta']:+})" if v["delta"] is not None
                     else f"  {c}: {v['a']} -> {v['b']}")
    return "\n".join(lines)
