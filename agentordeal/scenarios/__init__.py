import importlib
# Battery version (docs/BATTERY.md): bump the minor when scenarios or
# detectors change, the major when scenarios are removed or renumbered.
# Scores are comparable only within the same battery version.
BATTERY_VERSION = "1.2.0"
CATEGORIES = ["prompt_injection","tool_misuse","data_exfiltration","memory_poisoning","goal_hijacking","mcp_security"]
def load_scenarios():
    out=[]
    for c in CATEGORIES:
        if c == "mcp_security": continue
        mod=importlib.import_module(f".{c}", __package__)
        out.extend(mod.SCENARIOS)
    out.extend(importlib.import_module(".expanded", __package__).SCENARIOS)
    out.extend(importlib.import_module(".mcp_security", __package__).SCENARIOS)
    out.extend(importlib.import_module(".coverage_expansion", __package__).SCENARIOS)
    return out
__all__=["load_scenarios","CATEGORIES","BATTERY_VERSION"]
