"""Machine-readable coverage map: OWASP ASI + MITRE ATLAS.

Computed from the live scenario data every time -- never a hand-kept
table. ATLAS has no technique for agent memory poisoning or for MCP
tool-description attacks; those categories map to the nearest ATLAS
analogues and are flagged "analogue" so nobody over-claims the mapping.
"""
from .scenarios import load_scenarios, BATTERY_VERSION

ASI_NAMES = {
    "ASI01": "Agent Goal Hijack",
    "ASI02": "Tool Misuse and Exploitation",
    "ASI03": "Identity and Privilege Abuse",
    "ASI04": "Agentic Supply Chain Vulnerabilities",
    "ASI05": "Unexpected Code Execution",
    "ASI06": "Memory and Context Poisoning",
    "ASI07": "Insecure Inter-Agent Communication",
    "ASI08": "Cascading Failures",
    "ASI09": "Human-Agent Trust Exploitation",
    "ASI10": "Rogue Agents",
}

# technique id -> (name, exact|analogue)
ATLAS = {
    "AML.T0051.000": ("LLM Prompt Injection: Direct", "exact"),
    "AML.T0051.001": ("LLM Prompt Injection: Indirect", "exact"),
    "AML.T0054": ("LLM Jailbreak", "exact"),
    "AML.T0056": ("LLM Meta Prompt Extraction", "exact"),
    "AML.T0057": ("LLM Data Leakage", "exact"),
    "AML.T0053": ("LLM Plugin Compromise", "exact"),
    "AML.T0024": ("Exfiltration via Cyber Means", "exact"),
    "AML.T0048": ("External Harms", "exact"),
    "AML.T0010": ("AI Supply Chain Compromise", "analogue"),
    "AML.T0020": ("Poison Training Data", "analogue"),
}

ATLAS_BY_CATEGORY = {
    "prompt_injection": ["AML.T0051.000", "AML.T0051.001", "AML.T0054", "AML.T0056"],
    "tool_misuse": ["AML.T0053", "AML.T0048"],
    "data_exfiltration": ["AML.T0057", "AML.T0024", "AML.T0056"],
    "memory_poisoning": ["AML.T0020", "AML.T0010"],
    "goal_hijacking": ["AML.T0051.000", "AML.T0054"],
    "mcp_security": ["AML.T0010", "AML.T0053"],
}

THIN_THRESHOLD = 3

def coverage_report(scenarios=None):
    scenarios = scenarios if scenarios is not None else load_scenarios()
    asi = {}
    for code, name in ASI_NAMES.items():
        ids = [s["id"] for s in scenarios if s.get("owasp_asi") == code]
        asi[code] = {"name": name, "count": len(ids), "scenario_ids": ids,
                     "status": "gap" if not ids else "thin" if len(ids) < THIN_THRESHOLD else "covered"}
    atlas = {}
    for s in scenarios:
        for tid in ATLAS_BY_CATEGORY.get(s["category"], []):
            e = atlas.setdefault(tid, {"name": ATLAS[tid][0], "mapping": ATLAS[tid][1],
                                       "count": 0, "scenario_ids": []})
            e["count"] += 1; e["scenario_ids"].append(s["id"])
    cats = {}
    for s in scenarios:
        cats[s["category"]] = cats.get(s["category"], 0) + 1
    return {"battery_version": BATTERY_VERSION, "total_scenarios": len(scenarios),
            "categories": cats,
            "owasp_asi": asi,
            "mitre_atlas": atlas,
            "gaps": [c for c, v in asi.items() if v["status"] == "gap"],
            "thin": [c for c, v in asi.items() if v["status"] == "thin"]}

def format_text(rep):
    lines = [f"AgentOrdeal coverage -- battery {rep['battery_version']}, "
             f"{rep['total_scenarios']} scenarios",
             "", "OWASP Agentic Top 10 (ASI):"]
    for code, v in rep["owasp_asi"].items():
        lines.append(f"  {code} {v['name']}: {v['count']} scenarios [{v['status']}]")
    lines += ["", "MITRE ATLAS:"]
    for tid, v in sorted(rep["mitre_atlas"].items()):
        lines.append(f"  {tid} {v['name']} ({v['mapping']} mapping): {v['count']} scenarios")
    lines += ["", f"Gaps (no scenarios): {', '.join(rep['gaps']) or 'none'}",
              f"Thin (<{THIN_THRESHOLD} scenarios): {', '.join(rep['thin']) or 'none'}"]
    return "\n".join(lines)
