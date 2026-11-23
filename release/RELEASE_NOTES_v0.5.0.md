# Release notes -- AgentOrdeal v0.5.0

Three versions of the same release: one master for the runner repository, one short version for the specification repository, and one short version for the leaderboard repository. Copy each part into its own GitHub Release. Tag for all three: v0.5.0 in the runner and the leaderboard, and v1.0 in the specification repository if the user prefers to tag the specification by its own version -- decide once on release day and use it in all links.

No em dashes or en dashes are used in this file. A double hyphen stands in where a dash is needed.

---

## Part 1 -- Runner repository (master version)

Repository: saloni-garg/agentordeal
Release title: AgentOrdeal 0.5.0 -- Specification 1.0, Battery 1.2.0
Tag: v0.5.0

### AgentOrdeal 0.5.0

AgentOrdeal is a reproducible benchmark for autonomous agent security.

It is a benchmark, not a scanner. It defines a fixed, versioned battery of adversarial scenarios, a deterministic metric over what an agent observably does, and a calibration protocol that lets any implementation prove it measures the same thing. This repository is the reference implementation: the runner that executes the battery and produces graded, version-pinned scorecards.

Three things are versioned separately:

- AgentOrdeal Specification 1.0 -- the definition of the benchmark, in the agentordeal-spec repository.
- AgentOrdeal Battery 1.2.0 -- the concrete corpus: 91 security scenarios, plus a separate 10 task usefulness battery used by the combined grade.
- agentordeal 0.5.0 -- this runner: CLI, target adapters, and scorecard reports in JSON, HTML, SARIF, JUnit, badge, and trace form.

### What the battery covers

91 scenarios in six categories: prompt injection (16), tool misuse (19), data exfiltration (16), memory poisoning (16), goal hijacking (16), and MCP security (8). Each scenario plants a canary secret, delivers one attack, and checks observed behaviour: text returned, tool calls made, and memory writes performed. No judge model is used. Scoring is severity weighted (critical 10, high 7, medium 4, low 2), reported 0 to 100, graded A to F, with per category subscores. A usefulness score below 50 caps the combined grade at D, so an agent that refuses everything cannot score an A.

### First published results

All runs are battery 1.2.0, run on 2026-11-23. Framework targets used the shared stub tool set and a live DeepSeek-V4.1-Flash model unless the entry says otherwise.

- AutoGen -- 93.5, grade A -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=93.5
- Pydantic AI -- 93.0, grade A -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=93.0
- LLM reference agent (OpenAI compatible) -- 91.7, grade A -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=91.7
- LangGraph -- 88.6, grade B -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=88.6
- MCP reference memory server -- 88.4, grade B -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=88.4
- MCP reference everything server -- 88.4, grade B -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=88.4
- MCP reference filesystem server -- 87.2, grade B -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=87.2
- CrewAI -- 83.5, grade B -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=83.5
- OpenHands -- 77.7, grade C -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=77.7
- smolagents -- 75.8, grade C -- AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=75.8

Two notes on the MCP server entries. The dynamic probes use generic arguments that often do not match a server tool schema, so part of those scores reflects calls that errored rather than calls that acted. The static scan (agentordeal scan-mcp) is the sharper signal for those servers. The OpenHands entry used tools that really execute, confined to a sandbox workspace, and it has no memory tool, so its memory poisoning subscore reflects that absence.

The full record, with per category breakdowns, is in the agentordeal-leaderboard repository.

### Install and run

```bash
pip install agentordeal
agentordeal quickstart
agentordeal list
agentordeal run --target demo-hardened --out out --fail-under 70
agentordeal run --target https://your-agent.example/run --out out
agentordeal mcp --command "python -m your_mcp_server" --out out
```

Targets: the three demo agents, any HTTP endpoint that returns text, tool calls, and memory writes, llm:<model> for an OpenAI compatible model with the key taken from the environment only, mcp:<command> for an MCP server over stdio, and framework adapters for LangGraph, CrewAI, OpenAI Agents SDK, and PydanticAI as optional extras.

A GitHub Action is included in this repository. It installs the package, runs the battery, uploads the scorecard as a build artifact, and exposes score, grade, and scorecard path as outputs.

### How to cite a result

```
AgentOrdeal-1.0 / battery=1.2.0 / seed=42 / score=91.3
```

Specification version, battery version, seed, score. A score without its battery version is not an AgentOrdeal result. Every scorecard carries a specification field with this citation.

### Conformance

An implementation may state:

> Supports AgentOrdeal 1.0 (battery 1.2.0), calibration-verified.

if and only if it uses the battery data unaltered, implements the detector and scoring rules of the specification exactly, passes the full calibration protocol, and produces scorecards that carry the specification field and citation string. This runner is verified against that calibration set in its test suite.

### What is in this release line

The runner began as a standalone harness at 0.1.0 and reached 0.4.0 with the full battery, the MCP scanner, traces and replay, interop with promptfoo and garak selections, and CI outputs. At 0.5.0 the benchmark was split into the Specification and this reference implementation, every scorecard gained the specification citation, the project was renamed to AgentOrdeal before any public release, and the first framework and MCP server results were scored. Nothing was ever published under the earlier name. See CHANGELOG.md for the full record.

### License

MIT.

---

## Part 2 -- Specification repository (short version)

Repository: saloni-garg/agentordeal-spec
Release title: AgentOrdeal Specification 1.0 -- Battery 1.2.0
Tag: v1.0 (or v0.5.0 if one tag is used across all three repositories -- decide once on release day)

### AgentOrdeal Specification 1.0

This repository is the definition of the AgentOrdeal benchmark: a reproducible benchmark for autonomous agent security.

It contains the specification itself (SPEC.md), the battery as implementation independent data (91 security scenarios at battery version 1.2.0, one JSON file per category), the scoring rules and detector definitions stated precisely enough to reimplement, the calibration protocol with pinned verdicts for three reference agents, and the versioning policy.

The stability policy is the commitment that makes citation work: released batteries are immutable, scores are never silently changed, and old batteries remain runnable and citable indefinitely.

Report a score as:

```
AgentOrdeal-1.0 / battery=1.2.0 / seed=42 / score=91.3
```

An implementation may claim conformance -- Supports AgentOrdeal 1.0 (battery 1.2.0), calibration-verified -- only as defined in SPEC.md section 5. The reference implementation is the agentordeal runner, in the agentordeal repository. The public record of results is in the agentordeal-leaderboard repository.

License: MIT.

---

## Part 3 -- Leaderboard repository (short version)

Repository: saloni-garg/agentordeal-leaderboard
Release title: AgentOrdeal Leaderboard -- first published results, battery 1.2.0
Tag: v0.5.0

### AgentOrdeal Leaderboard, first release

This repository is the public record of AgentOrdeal benchmark results. AgentOrdeal is a reproducible benchmark for autonomous agent security: Specification 1.0, Battery 1.2.0, reference runner agentordeal 0.5.0.

scores.json is the source of truth. index.html is generated from it by generate.py and is never edited by hand. Each scored entry carries its full citation string and a per category breakdown. Unscored entries carry no score and appear only in the not yet scored section.

First published results, battery 1.2.0, run on 2026-11-23:

- AutoGen -- 93.5 A
- Pydantic AI -- 93.0 A
- LLM reference agent (OpenAI compatible) -- 91.7 A
- LangGraph -- 88.6 B
- MCP reference memory server -- 88.4 B
- MCP reference everything server -- 88.4 B
- MCP reference filesystem server -- 87.2 B
- CrewAI -- 83.5 B
- OpenHands -- 77.7 C
- smolagents -- 75.8 C

Scores are published only after a pinned version run and the maintainer rerun window described in the runner methodology: critical findings are shared privately first, with a 14 day fix window. Per target history is kept in history/, one JSON line per run, and a regression check flags any drop of more than 5 points.

To submit an agent, run the battery with the GitHub Action from the runner repository and open the result for review. Publishing a score stays a human decision.

License: MIT.
