# Battery versioning

> Since iteration 21 the battery is a **specification artifact**: the
> canonical battery data lives in the `agentordeal-spec` repository
> (`scenarios/*.json`, generated from this runner's definitions by that
> repo's `tools/generate.py`), and the stability policy -- released
> batteries are immutable, scores are never silently changed, old
> batteries remain runnable and citable indefinitely -- is that repo's
> VERSIONING.md. This runner loads the battery through
> `agentordeal/battery.py`, from the spec data files when
> `AGENTORDEAL_SPEC_DIR` is set, else from the bundled copy. The bump
> rules below remain the working summary.

The battery -- the scenario set plus the detectors -- is versioned
separately from the tool. Every scorecard carries both:

- `version`: the agent-ordeal tool version.
- `battery_version`: the battery that produced the score.

**Scores are comparable only within the same battery version.** A score
change across battery versions may mean the battery changed, not the
target.

## Bump rules

- **Minor** (1.1.0 -> 1.2.0): scenarios added, detectors added or
  widened, payloads added.
- **Major** (1.x -> 2.0.0): scenarios removed or renumbered, detector
  semantics changed so a previously-passing behaviour can fail (or
  vice versa) for a reason other than a widened detector, scoring
  weights changed.
- Any battery change must regenerate the calibration set
  (`python -m agentordeal.calibration --write`) in the same commit.

## Battery changelog

### 1.2.0 -- shipped with tool 0.4.0
91 security scenarios: +3 Unexpected Code Execution scenarios (TM-17..TM-19, coverage_expansion) closing the ASI05 thin spot (1 -> 4 scenarios). No ASI code is below 3 scenarios. Calibration regenerated in the same change.

### 1.1.0 -- shipped with tool 0.2.0
88 security scenarios (16 each in prompt_injection, tool_misuse,
data_exfiltration, memory_poisoning, goal_hijacking; 8 in the new
mcp_security category), including multi-turn crescendo and encoded /
document-carried payloads, plus the separate 10-scenario usefulness
battery (unversioned with the security battery; reported separately).

### 1.0.0 -- shipped with tool 0.1.0
40 scenarios, 8 per category across the original five categories.
