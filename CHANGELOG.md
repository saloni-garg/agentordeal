# Changelog

## 0.5.0 -- renamed to AgentOrdeal (iteration 22)

- The project was renamed from **AgentGauntlet** to **AgentOrdeal**
  before its first public release. Nothing was ever published under
  the old name.
- Renamed: distribution `agent-gauntlet` -> `agentordeal`, import
  package `gauntlet` -> `agentordeal`, CLI `gauntlet` -> `agentordeal`,
  repository directories `agent-gauntlet` -> `agent-ordeal` and
  `agentgauntlet-spec` -> `agentordeal-spec`, config file
  `gauntlet.yaml` -> `agentordeal.yaml`, environment variable
  `GAUNTLET_SPEC_DIR` -> `AGENTORDEAL_SPEC_DIR`, plugin entry-point
  group `gauntlet.scenarios` -> `agentordeal.scenarios`.
- The battery is unchanged: battery 1.2.0, 91 scenarios, specification
  1.0. Every score is unchanged; existing scorecards and leaderboard
  entries were relabelled, not rescored. Citation format is now
  `AgentOrdeal-1.0 / battery=1.2.0 / seed=42 / score=91.3`.
- Compatibility: the pre-rename config file names (`gauntlet.yaml`,
  `gauntlet.yml`, `gauntlet.json`) and the `GAUNTLET_SPEC_DIR`
  environment variable are still honoured as fallbacks. There is no
  `gauntlet` import or CLI shim: the old name was never released, so
  nothing external can depend on it.

## Unreleased -- benchmark repositioning (iteration 21)

- The benchmark is split into the **AgentOrdeal Specification 1.0**
  (new sibling repo `agentordeal-spec`: SPEC.md, battery as data,
  scoring/detector rules, calibration protocol, stability policy) and
  this runner, now framed as the specification's reference
  implementation. No battery change: still battery 1.2.0, 91 scenarios.
- Every scorecard gains a `specification` field (spec version, battery
  version, seed, citation string, e.g.
  `AgentOrdeal-1.0 / battery=1.2.0 / seed=42 / score=91.3`) in JSON,
  HTML, SARIF, and JUnit; the CLI prints the citation at the end of a
  run.
- The runner loads the battery through one boundary
  (`agentordeal/battery.py`), optionally from the spec repo's data files
  (`AGENTORDEAL_SPEC_DIR`). New conformance test asserts the runner
  reproduces the specification's calibration verdicts exactly
  (`agentordeal.calibration.check_conformance`).
- Leaderboard reframed as benchmark results; scored entries carry
  their full citation string.
- New: `validation/` -- a documented-incident dataset and replay that
  measures how much of the documented incident record the battery
  catches (see validation/REPORT.md).

## 0.4.0 -- 2026-11-22
Adoption iterations 16-20 (see docs/ADOPTION_ITERATIONS.md), driven by the
backlog in docs/ADOPTION_BACKLOG.md:
- Real MCP example server (examples/mcp_server.py) and a fixed stdio MCP
  client (id-matched responses, notification-tolerant); `mcp:` targets in
  the runner; `agentordeal demo` one-command showcase; friendly CLI errors
  (exit 2 with a hint) for unknown targets and missing files
- Battery 1.2.0: +3 ASI05 scenarios (TM-17..TM-19); no ASI code below 3
  scenarios; calibration regenerated
- First real leaderboard scores from live runs: LLM reference agent on
  DeepSeek-V4.1-Flash (91.7 A) and the official MCP filesystem server
  (87.2 B dynamic; 11 static-scan findings)
- promptfoo importer: full YAML via the optional PyYAML extra, per-type
  unconverted guidance; Docker build steps verified daemon-free via
  scripts/verify_docker_equivalent.sh

## 0.3.0 -- 2026-11-22
Adoption iterations 11-15 (see docs/ADOPTION_ITERATIONS.md):
- LLM reference agent (`llm:<model>` targets, OpenAI-compatible, key from
  environment only) and leaderboard/run_leaderboard.py regenerating the
  leaderboard from real scorecard outputs with version pinning
- Packaging: wheel/sdist built and verified from a clean venv, Dockerfile,
  Action branding + score/grade/scorecard-path outputs, CONTRIBUTING.md,
  SECURITY.md, issue templates, pre-commit config, MANIFEST.in
- Interop: promptfoo config import (deterministic assertions only,
  unconverted reported), garak probe-name selection, promptfoo results
  export; docs/INTEROP.md
- Coverage: `agentordeal coverage` (OWASP ASI + MITRE ATLAS, gaps/thin
  spots named), battery versioning (battery 1.1.0, docs/BATTERY.md),
  calibration set for the three reference agents asserted in tests
- Scale: `agentordeal diff` with per-scenario regressions/fixes, per-run
  metadata (target version, timestamp, duration, seed) in JSON/HTML/
  SARIF/JUnit, deterministic `--seed`, HTTP 429/5xx backoff with
  Retry-After, self-hosted leaderboard workflow example

## 0.2.0 -- 2026-11-22
Adoption iterations 1-10 (see docs/ADOPTION_ITERATIONS.md):
- Config file (agentordeal.yaml/JSON), scenario filters, parallel runner
- SARIF 2.1.0 and JUnit XML outputs; `--format` selection
- SVG grade badge and `agentordeal badge`
- Framework adapters: LangGraph, OpenAI Agents SDK, CrewAI, PydanticAI (optional extras)
- Battery expanded 40 -> 88 scenarios, new mcp_security category, multi-turn and encoded payloads
- Benign usefulness battery (10 controls), combined grade with refusal cap
- `agentordeal scan-mcp` static MCP server scanner
- JSONL traces on every run; `agentordeal replay` re-scores a trace offline
- Plugin scenarios from a directory or entry points; example plugin
- Async target support, per-scenario timeout and retries, `--progress`

## 0.1.0 -- 2026-11-22
Initial v1: 40 scenarios in 5 categories, demo/HTTP/MCP adapters, JSON + HTML
scorecard, GitHub Action, leaderboard scaffold.
