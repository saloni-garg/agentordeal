import json, html
def _citation_html(card):
    spec = card.get("specification") or {}
    cit = spec.get("citation")
    if not cit: return ""
    return f"<p class='citation'>Specification citation: <code>{html.escape(cit)}</code></p>"
def _meta_html(card):
    m = card.get("metadata") or {}
    if not m: return ""
    bits = [f"Specification {html.escape(str(m.get('spec_version')))}",
            f"Battery {html.escape(str(m.get('battery_version')))}",
            f"Tool {html.escape(str(m.get('tool_version')))}",
            f"Run {html.escape(str(m.get('timestamp')))}",
            f"Duration {m.get('duration_seconds')}s",
            f"Seed {m.get('seed')}",
            f"Target version {html.escape(str(m.get('target_version')))}"]
    return "<p class='meta'>" + " | ".join(bits) + "</p>"
def to_json(card, path=None):
    s=json.dumps(card, indent=2)
    if path: open(path,"w").write(s)
    return s
def to_html(card, path=None):
    rows="".join(f"<tr><td>{html.escape(r['id'])}</td><td>{html.escape(r['category'])}</td><td>{html.escape(r['severity'])}</td><td>{'PASS' if r['passed'] else 'FAIL'}</td><td>{html.escape(r['name'])}</td><td>{html.escape('; '.join(r['reasons']) or '-')}</td><td>{html.escape(r['remediation'])}</td></tr>" for r in card["results"] if not r["passed"]) or "<tr><td colspan=7>No failures.</td></tr>"
    bars="".join(f"<div>{html.escape(k)}: {v['score']}% <div class='bar'><span style='width:{v['score']}%'></span></div> ({v['passed']}/{v['total']})</div>" for k,v in card["categories"].items())
    doc=f"""<!doctype html><html><head><meta charset='utf-8'><title>AgentOrdeal Scorecard - {html.escape(str(card['target']))}</title><style>body{{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem}} .bar{{background:#ddd;height:12px}} .bar span{{display:block;background:#2563eb;height:12px}} table{{border-collapse:collapse;width:100%}} td,th{{border:1px solid #ccc;padding:6px;text-align:left}} .grade{{font-size:3rem;font-weight:700}}</style></head><body><h1>AgentOrdeal Scorecard</h1><p>Target: {html.escape(str(card['target']))}</p><p class='grade'>Grade {card['grade']} - {card['score']}/100</p><p>Passed {card['passed']}/{card['total']} scenarios (severity-weighted score).</p>{_citation_html(card)}{_meta_html(card)}<h2>Categories</h2>{bars}<h2>Failed scenarios</h2><table><tr><th>ID</th><th>Category</th><th>Severity</th><th>Result</th><th>Name</th><th>Evidence</th><th>Remediation</th></tr>{rows}</table></body></html>"""
    if path: open(path,"w").write(doc)
    return doc

import xml.etree.ElementTree as ET

def to_sarif(card, path=None):
    rules=[]; seen=set()
    for r in card["results"]:
        if r["category"] in seen: continue
        seen.add(r["category"])
        rules.append({"id": r["category"], "name": r["category"],
            "shortDescription": {"text": f"AgentOrdeal {r['category']} failure"},
            "fullDescription": {"text": r["remediation"]},
            "defaultConfiguration": {"level": "error"}})
    results=[]
    for r in card["results"]:
        if r["passed"]: continue
        level = "error" if r["severity"] in ("critical","high") else "warning"
        results.append({"ruleId": r["category"], "level": level,
            "message": {"text": f"{r['id']} {r['name']}: " + ("; ".join(r["reasons"]) or "detector failed")},
            "locations": [{"physicalLocation": {"artifactLocation": {"uri": "agentordeal/scenarios"},
                            "region": {"startLine": 1}}}],
            "properties": {"scenario_id": r["id"], "severity": r["severity"], "owasp_asi": r.get("owasp_asi")}})
    _m = card.get("metadata") or {}
    doc={"$schema":"https://json.schemastore.org/sarif-2.1.0.json","version":"2.1.0",
         "runs":[{"tool":{"driver":{"name":"agent-ordeal","version":_m.get("tool_version", card.get("version","0.1.0")),"rules":rules}},"results":results,
                   "properties":{"battery_version":_m.get("battery_version", card.get("battery_version")),
                                 "specification":card.get("specification"),
                                 "spec_version":_m.get("spec_version"),
                                 "citation":_m.get("citation") or (card.get("specification") or {}).get("citation"),
                                 "timestamp":_m.get("timestamp"),"seed":_m.get("seed"),
                                 "target":card.get("target"),"target_version":_m.get("target_version"),
                                 "duration_seconds":_m.get("duration_seconds")}}]}
    out=json.dumps(doc, indent=2)
    if path: open(path,"w").write(out)
    return out

def to_junit(card, path=None):
    ts=ET.Element("testsuite", {"name": f"agent-ordeal:{card['target']}", "tests": str(card["total"]),
                                "failures": str(card["total"]-card["passed"]), "errors": "0"})
    _m = card.get("metadata") or {}
    if _m or card.get("specification"):
        props = ET.SubElement(ts, "properties")
        for k in ("tool_version","battery_version","timestamp","duration_seconds","seed","target_version","spec_version","citation"):
            pv = _m.get(k)
            ET.SubElement(props, "property", {"name": f"agentordeal.{k}", "value": "" if pv is None else str(pv)})
        spec = card.get("specification")
        if spec:
            ET.SubElement(props, "property", {"name": "agentordeal.specification",
                                              "value": json.dumps(spec, sort_keys=True)})
    for r in card["results"]:
        tc=ET.SubElement(ts,"testcase", {"classname": r["category"], "name": f"{r['id']} {r['name']}"})
        if not r["passed"]:
            f=ET.SubElement(tc,"failure", {"message": r["name"], "type": r["severity"]})
            f.text="; ".join(r["reasons"]) or "detector failed"
    out=ET.tostring(ts, encoding="unicode", xml_declaration=True)
    if path: open(path,"w").write(out)
    return out

FORMATS = {"json": ("scorecard.json", to_json), "html": ("scorecard.html", to_html),
           "sarif": ("scorecard.sarif", to_sarif), "junit": ("scorecard-junit.xml", to_junit)}

def write_formats(card, out_dir, formats):
    import os
    os.makedirs(out_dir, exist_ok=True); written=[]
    for fmt in formats:
        fname, fn = FORMATS[fmt]
        fn(card, os.path.join(out_dir, fname)); written.append(fname)
    return written

GRADE_COLORS = {"A":"#2da44e","B":"#1f883d","C":"#bf8700","D":"#bc4c00","F":"#cf222e"}

def to_badge_svg(card, path=None):
    grade, score = card["grade"], card["score"]
    color = GRADE_COLORS.get(grade, "#57606a")
    label = "agentordeal"
    value = f"{grade} - {score}/100"
    lw, vw = 6.5*len(label)+12, 6.5*len(value)+12
    w = lw+vw
    cats = ", ".join(f"{k}: {v['score']}" for k, v in card.get("categories", {}).items())
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="20" role="img" '
           f'aria-label="{label}: {value}"><title>{label}: {value} ({cats})</title>'
           f'<rect width="{lw:.0f}" height="20" fill="#555"/><rect x="{lw:.0f}" width="{vw:.0f}" height="20" fill="{color}"/>'
           f'<text x="{lw/2:.0f}" y="14" fill="#fff" font-family="Verdana,sans-serif" font-size="11" text-anchor="middle">{label}</text>'
           f'<text x="{lw+vw/2:.0f}" y="14" fill="#fff" font-family="Verdana,sans-serif" font-size="11" text-anchor="middle">{value}</text></svg>')
    if path: open(path,"w").write(svg)
    return svg

def badge_markdown(card, link="leaderboard/"):
    return f"[![AgentOrdeal: {card['grade']} ({card['score']}/100)](badge.svg)]({link})"
FORMATS["badge"] = ("badge.svg", to_badge_svg)
