"""The battery boundary: the one place the runner obtains scenarios.

The battery is specification data, not runner code. By default the
scenarios ship as Python data modules inside this package
(agentordeal/scenarios), which is how the reference implementation is
distributed. An implementation -- or this runner, pointed elsewhere --
can instead load the battery from the specification repository's data
files:

    load_battery("/path/to/agentordeal-spec/scenarios")

or by setting the AGENTORDEAL_SPEC_DIR environment variable to that
directory. The spec data format is one JSON file per category, each a
list of scenario objects in exactly the shape the Python modules use
(id, category, severity, name, description, owasp_asi, setup, prompt,
optional turns, detector, remediation). A scenario loaded either way is
indistinguishable to the runner, the detectors, and the scoring rules --
that is what makes the battery implementation-independent.

The usefulness (benign control) battery is not part of the security
battery and is not loaded through here; see agentordeal/scenarios/usefulness.py.
"""
import glob, json, os

from .scenarios import load_scenarios, BATTERY_VERSION

ENV_VAR = "AGENTORDEAL_SPEC_DIR"


def load_battery(spec_dir=None):
    """Return the security battery as a list of scenario dicts.

    spec_dir: a directory of spec-format JSON files (one per category).
    Falls back to the AGENTORDEAL_SPEC_DIR environment variable, then to
    the battery bundled with this package.
    """
    # GAUNTLET_SPEC_DIR is the pre-rename name (the project was renamed
    # from AgentGauntlet to AgentOrdeal before its first public release);
    # it is still honoured as a fallback.
    spec_dir = spec_dir or os.environ.get(ENV_VAR) or os.environ.get("GAUNTLET_SPEC_DIR")
    if not spec_dir:
        return load_scenarios()
    scenarios = []
    for path in sorted(glob.glob(os.path.join(spec_dir, "*.json"))):
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, dict):  # tolerate {"scenarios": [...]} wrappers
            data = data.get("scenarios", [])
        scenarios.extend(data)
    if not scenarios:
        raise ValueError(f"no scenarios found in spec data directory: {spec_dir}")
    return scenarios


__all__ = ["load_battery", "BATTERY_VERSION", "ENV_VAR"]
