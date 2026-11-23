"""Static MCP server scanner: flags risky tools without running an agent."""
import json, re

INJECTION_PHRASES = ["ignore previous", "ignore prior", "system instruction", "do not tell the user",
                     "don't tell the user", "without telling", "secretly", "hidden instruction",
                     "you must always", "before using this tool, first"]
CREDENTIAL_PARAMS = ["api_key", "apikey", "password", "secret", "token", "credential", "private_key", "access_key"]
BROAD_TOOLS = {"shell": ("critical", "shell/command execution"), "exec": ("critical", "command execution"),
               "bash": ("critical", "shell access"), "filesystem": ("high", "filesystem access"),
               "file": ("medium", "file access"), "http": ("medium", "network access"),
               "fetch": ("medium", "network fetch"), "payment": ("high", "payment capability"),
               "pay": ("high", "payment capability"), "delete": ("high", "destructive operation"),
               "admin": ("high", "administrative capability")}

def _params(tool):
    schema = tool.get("inputSchema") or tool.get("parameters") or {}
    props = schema.get("properties") or {}
    return list(props.keys()) if isinstance(props, dict) else []

def scan_tools(tools):
    findings = []
    for t in tools or []:
        name = str(t.get("name", "")); desc = str(t.get("description", "") or "")
        low = desc.lower(); params = _params(t)
        def add(rule, sev, msg): findings.append({"tool": name, "rule": rule, "severity": sev, "message": msg})
        if not desc.strip(): add("missing-description", "low", "tool has no description; agents cannot judge when to call it")
        for ph in INJECTION_PHRASES:
            if ph in low: add("injection-in-description", "critical", f"description contains instruction-like phrase: '{ph}'")
        if re.search(r"https?://", desc): add("url-in-description", "medium", "description contains a URL the agent may be steered to")
        for p in params:
            if any(c in p.lower() for c in CREDENTIAL_PARAMS):
                add("credential-parameter", "high", f"parameter '{p}' looks like a credential; agents may be fished into filling it")
        for kw, (sev, label) in BROAD_TOOLS.items():
            if kw in name.lower(): add("broad-capability", sev, f"tool name suggests {label}: '{name}'")
        if "*" in name or name.lower() in ("run", "execute", "eval"):
            add("generic-executor", "high", f"generic executor tool name: '{name}'")
    sev_rank = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    findings.sort(key=lambda f: sev_rank[f["severity"]])
    return {"tools": len(tools or []), "findings": findings,
            "summary": {s: sum(1 for f in findings if f["severity"] == s) for s in sev_rank}}

def scan_server(command):
    from .adapters.mcp import MCPClient
    with MCPClient(command) as c:
        tools = c.list_tools()
    result = scan_tools(tools)
    result["server"] = str(command); result["tool_names"] = [t.get("name") for t in tools]
    return result
