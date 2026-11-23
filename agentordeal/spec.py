"""The AgentOrdeal Specification identity, as implemented by this runner.

The benchmark is defined by the AgentOrdeal Specification (separate
repository: agentordeal-spec). This runner is its reference
implementation. The specification version and the battery version are
different things and are versioned separately:

- SPEC_VERSION: the version of the specification this runner implements
  (task definition, metric, detector semantics, citation format).
- BATTERY_VERSION (agentordeal.scenarios): the version of the scenario
  battery that produced a score.

Every scorecard carries both, plus the citation string a paper, README,
or leaderboard should use to report the score:

    AgentOrdeal-1.0 / battery=1.2.0 / seed=42 / score=91.3

A score reported without its battery version and seed is not a
reproducible AgentOrdeal result.
"""

SPEC_VERSION = "1.0"
SPEC_NAME = "AgentOrdeal Specification"


def citation_string(score, battery_version, seed=None, spec_version=None):
    """The canonical citation for one score.

    Format: AgentOrdeal-<spec> / battery=<battery> / seed=<seed> / score=<score>
    seed is rendered as 'none' when the run was unseeded.
    """
    seed_s = "none" if seed is None else str(seed)
    return (f"AgentOrdeal-{spec_version or SPEC_VERSION} / "
            f"battery={battery_version} / seed={seed_s} / score={float(score):.1f}")


def specification_block(score, battery_version, seed=None):
    """The `specification` field embedded in every scorecard."""
    return {"name": SPEC_NAME,
            "spec_version": SPEC_VERSION,
            "battery_version": battery_version,
            "seed": seed,
            "citation": citation_string(score, battery_version, seed)}
