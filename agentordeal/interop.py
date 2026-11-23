"""Interop with promptfoo and garak (see docs/INTEROP.md).

promptfoo import: deterministic assertions become Ordeal detectors.
LLM-judged assertions (llm-rubric and friends) have no deterministic
equivalent and are reported as unconverted, never silently dropped.
garak mapping: probe families map to Ordeal categories; garak probes
are families of attacks, not single tests, so the mapping is by
category, with dotted sub-probes resolving to their family.
promptfoo export: a Ordeal scorecard in promptfoo's results-JSON
shape (version 3 envelope).
"""
import json, re
from datetime import datetime, timezone

# ---------------------------------------------------------------- promptfoo in
def _load_config(path):
    text = open(path).read()
    if path.endswith(".json"):
        return json.loads(text)
    # Full YAML when PyYAML is installed (optional extra:
    # pip install "agent-ordeal[promptfoo]") -- anchors, merge keys,
    # complex nesting and multi-line strings all parse. Without it, the
    # stdlib subset parser handles the common promptfoo shapes and the
    # importer reports anything it cannot convert, by name.
    try:
        import yaml
        return yaml.safe_load(text)
    except ImportError:
        pass
    from .miniyaml import load
    return load(text)

def _substitute(template, vars_):
    out = template
    for k, v in (vars_ or {}).items():
        out = out.replace("{{%s}}" % k, str(v)).replace("{{ %s }}" % k, str(v))
    return out

_REGEX_CHARS = set(".^$*+?()[]{}|\\")

def import_promptfoo(path):
    """Returns (scenarios, unconverted). Each unconverted entry names the
    test index, assertion type, and why it was not converted."""
    cfg = _load_config(path) or {}
    prompts = cfg.get("prompts") or ["{{input}}"]
    template = prompts[0] if isinstance(prompts, list) else str(prompts)
    if isinstance(template, dict):  # promptfoo file:// / labelled prompt entries
        template = template.get("raw") or template.get("label") or "{{input}}"
    default_asserts = ((cfg.get("defaultTest") or {}).get("assert")) or []
    scenarios, unconverted = [], []
    for idx, test in enumerate(cfg.get("tests") or [], start=1):
        if isinstance(test, str):
            unconverted.append({"test": idx, "type": "file-reference",
                                "reason": "external test file reference cannot be inlined"})
            continue
        vars_ = test.get("vars") or {}
        if len(vars_) == 1 and "{{" not in template:
            prompt = str(next(iter(vars_.values())))
        elif not vars_:
            prompt = template
        else:
            prompt = _substitute(template, vars_)
            if prompt == template and len(vars_) == 1:
                prompt = str(next(iter(vars_.values())))
        forbidden = []
        for a in list(default_asserts) + list(test.get("assert") or []):
            t = (a or {}).get("type", "")
            v = (a or {}).get("value")
            if t in ("not-contains", "not-contain-all", "not-contains-any"):
                vals = v if isinstance(v, list) else [v]
                forbidden.extend(str(x) for x in vals if x is not None)
            elif t in ("not-regex", "not-matches"):
                if v is not None and not (set(str(v)) & _REGEX_CHARS):
                    forbidden.append(str(v))
                else:
                    unconverted.append({"test": idx, "type": t,
                                        "reason": "regular-expression assertion has no literal equivalent; convert it to a canary string manually"})
            elif t in ("contains", "icontains"):
                unconverted.append({"test": idx, "type": t,
                                    "reason": "positive-content assertion is a usefulness expectation, not a security detector; see the usefulness battery"})
            elif t:
                if "rubric" in t or t.startswith("llm-") or t in ("factuality", "model-graded-closedqa"):
                    reason = ("model-graded assertion: Ordeal verdicts are deterministic by design, so this "
                              "cannot convert 1:1. To keep the check, re-express it as a canary/forbidden-string "
                              "detector, or implement it as a plugin detector (docs: plugins) and reference it "
                              "from a plugin scenario.")
                elif t in ("cost", "latency", "perplexity"):
                    reason = ("performance assertion: Ordeal scores security behaviour only; keep this in "
                              "promptfoo or your CI metrics, it is out of scope for the battery by design.")
                else:
                    reason = "provider-specific assertion has no deterministic Ordeal equivalent; see docs/INTEROP.md for the per-type guidance table"
                unconverted.append({"test": idx, "type": t, "reason": reason})
        scenarios.append({
            "id": f"IMP-{idx:02d}", "category": "prompt_injection", "severity": "medium",
            "name": test.get("description") or f"Imported promptfoo test {idx}",
            "description": f"Imported from promptfoo config {path}.",
            "owasp_asi": "ASI01", "prompt": prompt, "payload": prompt, "setup": {},
            "detector": {"forbidden_text": forbidden, "forbidden_tools": [],
                         "forbidden_arg_contains": [], "forbidden_memory_contains": []},
            "remediation": "See docs/INTEROP.md."})
    return scenarios, unconverted

# ---------------------------------------------------------------- garak map
GARAK_MAP = {
    "promptinject": ["prompt_injection"],
    "dan": ["prompt_injection"],
    "encoding": ["prompt_injection", "data_exfiltration"],
    "leakreplay": ["data_exfiltration"],
    "leakage": ["data_exfiltration"],
    "knownbadsignatures": ["tool_misuse"],
    "malwaregen": ["tool_misuse"],
    "xss": ["tool_misuse"],
    "continuation": ["goal_hijacking"],
    "agent_breaker": ["tool_misuse", "goal_hijacking", "mcp_security"],
    "atkgen": ["prompt_injection"],
    "misleading": ["goal_hijacking"],
    "topic": ["goal_hijacking"],
}

def garak_selection(names, scenarios=None):
    """Map garak probe names to Ordeal scenario ids.
    Returns (ids, unknown_names). Dotted sub-probes resolve to the family."""
    from .scenarios import load_scenarios
    scenarios = scenarios if scenarios is not None else load_scenarios()
    cats, unknown = set(), []
    for n in names:
        fam = n.split(".")[0].strip().lower()
        if fam in GARAK_MAP: cats.update(GARAK_MAP[fam])
        else: unknown.append(n)
    return [s["id"] for s in scenarios if s["category"] in cats], unknown

# ---------------------------------------------------------------- promptfoo out
def export_promptfoo(card):
    rows = []
    for r in card["results"]:
        trace = r.get("trace") or {}
        resp = (trace.get("response") or {}).get("text", "")
        prompt = trace.get("prompt", "")
        reason = "; ".join(r.get("reasons") or []) or "passed"
        rows.append({
            "prompt": {"raw": prompt, "label": r["id"]},
            "response": {"output": resp},
            "success": bool(r["passed"]),
            "score": 1.0 if r["passed"] else 0.0,
            "gradingResult": {
                "pass": bool(r["passed"]), "score": 1.0 if r["passed"] else 0.0,
                "reason": reason,
                "componentResults": [{
                    "pass": bool(r["passed"]), "score": 1.0 if r["passed"] else 0.0,
                    "reason": reason,
                    "assertion": {"type": "agentordeal-scenario", "value": r["id"],
                                  "metric": r["category"]}}]},
            "testCase": {"description": r["name"],
                         "vars": {"scenario_id": r["id"], "category": r["category"],
                                  "severity": r["severity"]}},
            "provider": {"id": f"agentordeal:{card.get('target')}"}})
    failures = sum(1 for x in rows if not x["success"])
    return {"evalId": f"agentordeal-{card.get('target')}",
            "results": {"version": 3,
                        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        "results": rows,
                        "stats": {"successes": len(rows) - failures, "failures": failures,
                                  "tokenUsage": {"total": 0, "prompt": 0, "completion": 0}}},
            "config": {"description": "Exported from an AgentOrdeal scorecard (docs/INTEROP.md)"},
            "shareableUrl": None,
            "agentordeal": {"score": card.get("score"), "grade": card.get("grade"),
                         "target": card.get("target")}}
