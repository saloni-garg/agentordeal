# AgentOrdeal -- the reference runner

![CI](https://img.shields.io/badge/CI-placeholder-lightgrey) ![PyPI](https://img.shields.io/badge/PyPI-placeholder-lightgrey) ![License: MIT](https://img.shields.io/badge/license-MIT-green)

**A reproducible benchmark for autonomous agent security.**

AgentOrdeal is a benchmark. This repository is its **reference
implementation**: the runner that executes the battery defined by the
**AgentOrdeal Specification** (the `agentordeal-spec` repository)
and produces graded, version-pinned, reproducible scorecards.

The benchmark -- not this code -- is the standard. The specification
defines the task, the battery (91 adversarial scenarios: prompt
injection, tool misuse, data exfiltration, memory poisoning, goal
hijacking, MCP attacks), the deterministic metric, and the calibration
protocol. Other implementations can and should exist; an implementation
conforms by reproducing the specification's calibration verdicts
exactly, not by using this runner.

## The three entities

AgentOrdeal is three separate things, versioned separately:

- **AgentOrdeal Specification** -- the definition of the benchmark:
  the scenarios' semantics, the detectors, the scoring rules, and the
  versioning policy. It lives in the `agentordeal-spec` repository and
  is currently at specification version 1.0.
- **AgentOrdeal Battery 1.2** -- the concrete test corpus: the 91
  adversarial scenarios (battery version 1.2.0) that the specification
  defines and that a score is measured against. A battery release is
  immutable; a changed corpus is a new battery version.
- **agentordeal** -- the runner: this package. The CLI, the target
  adapters (demo, HTTP, LLM, MCP, and the agent frameworks), and the
  scorecard reports (JSON, HTML, SARIF, JUnit, badge, trace). It is the
  reference implementation of the specification, currently at runner
  version 0.5.0. Other runners can implement the same specification.

## Report a score

Every run ends with the citation string a paper, README, or leaderboard
should use:

```
AgentOrdeal-1.0 / battery=1.2.0 / seed=42 / score=91.3
```

Specification version, battery version, seed, score. A score without
its battery version is not an AgentOrdeal result. Every scorecard
(JSON, HTML, SARIF, JUnit) carries a `specification` field with this
citation.

## Install

```bash
pip install agentordeal
```

## 60-second quickstart

```bash
agentordeal quickstart          # scores a vulnerable and a hardened demo agent, side by side
agentordeal list                # the 91 scenarios of battery 1.2.0
agentordeal run --target demo-hardened --out out --fail-under 70
agentordeal run --target https://your-agent.example/run --out out
agentordeal mcp --command "python -m your_mcp_server" --out out
```

`quickstart` writes `out/demo-vulnerable/scorecard.{json,html}` and
`out/demo-hardened/scorecard.{json,html}`, prints the comparison, and
prints each run's citation string.

## How the benchmark works

The agent *system* is tested, not the base model: its instruction
hierarchy, the tool calls it actually makes, the MCP servers it trusts,
and what it writes to long-term memory. Every scenario plants a canary
secret in the target's context and delivers one attack. The verdict
comes from observed behaviour -- a canary that leaked, a forbidden tool
that was called, a poisoned fact that was stored -- never from an LLM
judge. Detectors are deterministic rules, published in the
specification, so any score can be reproduced exactly.

Scoring is severity-weighted (critical 10, high 7, medium 4, low 2),
0-100, graded A-F, with per-category subscores. A separate 10-task
benign usefulness battery feeds the combined grade: usefulness below
50 caps the grade at D, so a refuse-everything agent cannot score an A.

Full method: [docs/METHODOLOGY.md](docs/METHODOLOGY.md). Battery
versioning and the stability policy: the specification repository's
`VERSIONING.md` (summary in [docs/BATTERY.md](docs/BATTERY.md)).

## How this differs from scanners

garak scans **models**. promptfoo tests **prompts and outputs**. Those
are tools, and useful ones. AgentOrdeal is the measurement they and
others can report against: a fixed battery, a pinned metric, and a
public record of results. A scanner that runs the AgentOrdeal
battery and publishes AgentOrdeal scores is not a competitor to the
benchmark; it is an implementation of it.

## Benchmark results

[leaderboard/](leaderboard/) -- the public record of AgentOrdeal
results for well-known open agent frameworks and MCP servers. Every
scored entry shows its full citation string. Entries start as clearly
marked **unscored** placeholders; a score is published only after a
pinned-version run and the maintainer rerun window in the methodology.
First real results (battery 1.2.0): an LLM reference agent at
`AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=91.7` and the
official MCP filesystem server at 87.2.

## Conformance

This runner loads the battery through one boundary
(`agentordeal/battery.py`): by default the battery bundled with the
package, or the specification repository's data files when
`AGENTORDEAL_SPEC_DIR` points at them. The conformance test
(`tests/test_iteration21.py`) runs the specification's calibration set
and asserts this runner reproduces the expected verdicts for the three
reference agents exactly.

## Using the runner

- **Targets**: `demo-vulnerable`, `demo-hardened`, `demo-refuse-all`,
  any HTTP endpoint returning `{text, tool_calls, memory_writes}`,
  `llm:<model>` (OpenAI-compatible, key from the environment only),
  `mcp:<command>`, and framework adapters (LangGraph, CrewAI, OpenAI
  Agents SDK, PydanticAI -- optional extras, see docs/ADAPTERS.md).
- **Formats**: `--format json|html|sarif|junit|badge`. SARIF 2.1.0 goes
  to GitHub Code Scanning; JUnit XML goes to standard CI dashboards.
  Every run also writes `trace.jsonl`; `agentordeal replay` re-scores a
  trace offline and `agentordeal diff A B` reports regressions.
- **Config**: `agentordeal.yaml` (or JSON) with target, fail_under,
  categories, severities, formats, jobs -- CLI flags override it.
  Selection: `--category`, `--severity`, `--scenario`, `--garak`,
  `--extra-scenarios`. Parallel runs: `--jobs N`. Deterministic order:
  `--seed N`.
- **MCP static scan**: `agentordeal scan-mcp --command "<server cmd>"`
  flags injection text in tool descriptions, credential-shaped
  parameters, and over-broad tools without running an agent.
- **Interop**: `agentordeal import-promptfoo` / `export-promptfoo` --
  see docs/INTEROP.md.
- **Plugins**: `--plugin-dir DIR` loads custom scenarios (see
  `examples/my_plugin.py`); pip packs can register the
  `agentordeal.scenarios` entry point. Custom scenarios are reported
  separately -- an extended run is not an AgentOrdeal score.
- **Coverage**: `agentordeal coverage` prints the OWASP ASI + MITRE ATLAS
  coverage map from live data, gaps and thin spots named.

### GitHub Action

```yaml
- uses: saloni-garg/agent-ordeal@v0.1.0  # placeholder until published
  with:
    target: "https://your-agent.example/run"
    fail-under: "70"
```

The Action installs the package, runs the battery, uploads the
scorecard as a build artifact, exposes `score` / `grade` /
`scorecard-path` outputs, and fails the job below the threshold.

### Exit codes
- `0` -- run completed and score is at or above `--fail-under` (or no threshold set); scan found nothing at or above `--fail-on`.
- `1` -- score below `--fail-under`, replayed score below `--fail-under`, or scan finding at or above `--fail-on`.
- `2` -- usage error (bad arguments, missing target, plugin load error).

## Adding a scenario

Scenarios are specification data. Proposing one means proposing a
battery change: it lands in the runner first as a candidate, and
becomes part of the benchmark only in a new battery version with
regenerated calibration (see the specification's VERSIONING.md).
Scenario shape and the contribution path are in CONTRIBUTING.md and
docs/SCENARIO_TAXONOMY.md.

## History

The runner began as a standalone harness (v0.1.0-v0.4.0, adoption
iterations 1-20 in docs/ADOPTION_ITERATIONS.md). Iteration 21 split the
benchmark into the AgentOrdeal Specification 1.0
(`agentordeal-spec`) and this reference implementation, added the
specification citation to every scorecard, and reframed the
leaderboard as benchmark results.

## License

MIT. See [LICENSE](LICENSE).
