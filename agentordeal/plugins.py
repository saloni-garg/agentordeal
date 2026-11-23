"""Plugin scenarios: user directories and entry points.

A plugin is a Python file defining SCENARIOS (same dict shape as the built-in
battery) and optionally REMEDIATION text per category. Loaded scenarios are
validated; a bad plugin raises PluginError naming the file and the problem.
"""
import importlib.util, os, sys

REQUIRED = ["id", "category", "severity", "name", "description", "owasp_asi", "prompt", "detector"]
SEVERITIES = {"critical", "high", "medium", "low"}

class PluginError(Exception): pass

def validate_scenario(sc, source):
    for k in REQUIRED:
        if not sc.get(k): raise PluginError(f"{source}: scenario {sc.get('id','?')} missing field '{k}'")
    if sc["severity"] not in SEVERITIES: raise PluginError(f"{source}: scenario {sc['id']} bad severity '{sc['severity']}'")
    if not isinstance(sc["detector"], dict): raise PluginError(f"{source}: scenario {sc['id']} detector must be a dict")
    return sc

def load_plugin_dir(path):
    out = []
    if not path or not os.path.isdir(path): raise PluginError(f"plugin dir not found: {path}")
    for fname in sorted(os.listdir(path)):
        if not fname.endswith(".py") or fname.startswith("_"): continue
        fpath = os.path.join(path, fname)
        spec = importlib.util.spec_from_file_location(f"agentordeal_plugin_{fname[:-3]}", fpath)
        mod = importlib.util.module_from_spec(spec)
        try: spec.loader.exec_module(mod)
        except Exception as e: raise PluginError(f"{fpath}: failed to load: {e}") from e
        for sc in getattr(mod, "SCENARIOS", []):
            out.append(validate_scenario(dict(sc), fpath))
    return out

def load_entry_point_scenarios(group="agentordeal.scenarios"):
    out = []
    try:
        from importlib.metadata import entry_points
        eps = entry_points(group=group)
    except Exception:
        return out
    for ep in eps:
        try: fn = ep.load()
        except Exception as e: raise PluginError(f"entry point {ep.name}: {e}") from e
        for sc in fn():
            out.append(validate_scenario(dict(sc), f"entry point {ep.name}"))
    return out

def load_with_plugins(plugin_dir=None, use_entry_points=False):
    from .scenarios import load_scenarios
    base = load_scenarios(); extra = []
    if plugin_dir: extra += load_plugin_dir(plugin_dir)
    if use_entry_points: extra += load_entry_point_scenarios()
    ids = {s["id"] for s in base}
    for sc in extra:
        if sc["id"] in ids: raise PluginError(f"duplicate scenario id: {sc['id']}")
        ids.add(sc["id"])
    return base + extra
