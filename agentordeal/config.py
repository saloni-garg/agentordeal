"""Config file support: agentordeal.yaml (small YAML subset) or JSON.

Stdlib only. The YAML subset supports flat keys and inline or block lists:
    target: demo-hardened
    fail_under: 70
    categories: [prompt_injection, tool_misuse]
    severities:
      - critical
      - high
    formats: [json, html]
    jobs: 4
"""
import json, os

def _parse_scalar(v):
    v = v.strip()
    if v in ("true","True"): return True
    if v in ("false","False"): return False
    try: return int(v)
    except ValueError: pass
    try: return float(v)
    except ValueError: pass
    return v.strip("'\" ")

def _parse_value(v):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [_parse_scalar(x) for x in inner.split(",") if x.strip()] if inner else []
    return _parse_scalar(v)

def load_config(path=None):
    """Load config from an explicit path, or ./agentordeal.yaml|yml|json if present."""
    # gauntlet.* names are the pre-rename config files (the project was
    # renamed from AgentGauntlet to AgentOrdeal before its first public
    # release); they are still read as fallbacks.
    candidates = [path] if path else ["agentordeal.yaml","agentordeal.yml","agentordeal.json",
                                      "gauntlet.yaml","gauntlet.yml","gauntlet.json"]
    for c in candidates:
        if c and os.path.exists(c):
            text = open(c).read()
            if c.endswith(".json"):
                return json.loads(text)
            cfg, key = {}, None
            for line in text.splitlines():
                if not line.strip() or line.strip().startswith("#"): continue
                if line.startswith((" ","\t")) and key and line.strip().startswith("- "):
                    if not isinstance(cfg.get(key), list): cfg[key] = []
                    cfg[key].append(_parse_scalar(line.strip()[2:]))
                    continue
                if ":" in line:
                    k, v = line.split(":", 1); key = k.strip()
                    cfg[key] = _parse_value(v) if v.strip() else None
            return cfg
    return {}

def get(cfg, *names, default=None):
    for n in names:
        if cfg.get(n) is not None: return cfg[n]
    return default
