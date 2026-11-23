# Agent Gauntlet -- Adoption Iterations Log

Goal: maximum adoption. Marketing is out of scope for this log; only technical
factors are considered. Each iteration: measured state at start, comparison to
counterparts, why the project would not be majority-adopted as-is, a bulleted
list of technical improvements, then what was actually built and verified in
that iteration. Verda GPU compute was authorised; it was considered in every
iteration and never needed -- the harness is CPU-bound rule-based testing and
all targets used are local fakes/demos. No GPU work was done.

Counterpart facts are from web search in iterations 1, 4, 7 and 10, or marked
as code-audit inference / prior-iteration research in the others.

## Iteration 1

### State
Measured at start (clean venv, `pip install -e .`, `pytest -q`, `gauntlet list`):
17 tests passing, 40 scenarios (8 each in prompt_injection, tool_misuse,
data_exfiltration, memory_poisoning, goal_hijacking). Adapters: demo
(vulnerable/hardened), HTTP, MCP stdio. Outputs: JSON + HTML scorecard only.
CLI commands: list, quickstart, run, mcp. Runner is sequential, single-threaded,
no config file, no scenario selection -- every run is all 40 scenarios against
one target, configured only by CLI flags. GitHub Action exists. No git repo,
not published.

### Comparison to counterparts
From web search this iteration: promptfoo is configured in YAML, has 157
plugins and 34 strategies, OpenTelemetry tracing with trajectory assertions on
tool use, and an MCP server mode (agentleak.org comparison, checked against
promptfoo docs). garak has 41 probe modules with per-probe detectors and an
agent_breaker probe. PyRIT composes multi-turn campaigns (Crescendo, TAP,
GOAT) with converters and scorers. DeepTeam offers 50+ vulnerabilities and 20+
attacks with a Python API. Gauntlet at this stage has: no config file, no
plugin/strategy separation, no tracing, no multi-turn, 40 fixed scenarios, and
no Python-library ergonomics beyond `run(target)`.

### Why it would not be majority adopted as-is
- No config file: teams cannot check a test definition into their repo and
  rerun it identically in CI and locally; promptfoo's YAML config is the
  habit the market already has.
- All-or-nothing runs: no way to run one category, one severity, or one
  scenario while fixing a failure, so the fix-rerun loop is slow and blunt.
- Sequential runner: 40 scenarios is fine, but any real target with network
  latency makes runs minutes long; counterparts run probes in parallel.
- CLI-flag-only configuration does not survive team handover; nothing to
  review in a pull request.

### Technical improvements (bulleted)
- Add a checked-in config file (gauntlet.yaml / JSON) for target, fail-under, filters, formats, output dir
- Add scenario selection by category, severity, and id on CLI and in config
- Add a parallel runner (thread pool, configurable jobs) with deterministic result ordering
- Keep CLI flags overriding config values, and document precedence

### Built in this iteration
Built: `gauntlet/config.py` (stdlib YAML-subset + JSON config loader),
`filter_scenarios()` in the runner, a thread-pool parallel runner (`--jobs`,
deterministic ordering via ordered map), CLI flags `--config/--category/
--severity/--scenario/--jobs`, config precedence (CLI > config > default), and
`examples/gauntlet.yaml`. Two build fixes were needed and fixed in-iteration:
an indentation error in the patched runner loop, and a config-parser bug where
a block list under a key first set to None raised AttributeError.

### Verified
`pytest -q`: 24 passed (17 baseline + 7 new). `gauntlet quickstart`:
demo-vulnerable 12.8 F (8/40), demo-hardened 100.0 A (40/40) -- unchanged.
Parallel and sequential runs produce identical scores and ordering (tested).

## Iteration 2

### State
Measured at start: 24 tests passing, 40 scenarios, adapters demo/HTTP/MCP.
Outputs: JSON + HTML only. Config file, filters, and parallel runner exist
(iteration 1). CLI: list, quickstart, run, mcp. No machine-readable CI-native
finding formats; a security team using GitHub Code Scanning or a JUnit-based
CI dashboard cannot ingest Gauntlet results without writing a converter.

### Comparison to counterparts
Prior-iteration research plus code audit: promptfoo emits SARIF for GitHub
Code Scanning (documented in its OWASP scan examples). Argus, per the parent
project's earlier research, emits SARIF 2.1.0, JUnit XML, and HTML. Garak
emits JSONL hit logs. Gauntlet emits only JSON + HTML, which no standard
security dashboard ingests natively. (Code-audit inference for the rest.)

### Why it would not be majority adopted as-is
- Findings that cannot enter GitHub Code Scanning are invisible where
  engineering teams already triage security findings.
- CI systems (Jenkins, GitLab, Azure DevOps) speak JUnit XML; without it
  Gauntlet results do not appear as test failures in existing dashboards.
- Every adopter would write the same converter; most will not bother.

### Technical improvements (bulleted)
- Add SARIF 2.1.0 output with rules per category/severity and results per failed scenario
- Add JUnit XML output, one testcase per scenario, failures with evidence text
- Add a `--format` option (json, html, sarif, junit) usable in combination, in config too
- Keep JSON/HTML as defaults so existing users are unaffected

### Built in this iteration
Built: `to_sarif()` (SARIF 2.1.0, one rule per category, one result per failed
scenario, severity mapped to error/warning, scenario id and OWASP-ASI in
properties) and `to_junit()` (JUnit XML, one testcase per scenario) in
`gauntlet/scorecard.py`, a `FORMATS` registry with `write_formats()`, and a
repeatable `--format` CLI option also honoured from config. Defaults stay
json+html.

### Verified
`pytest -q`: 28 passed (24 + 4 new, including SARIF/JUnit structure parsed back
with json/ElementTree and a CLI run writing only the requested formats).
Quickstart unchanged: 12.8 F vs 100.0 A.

## Iteration 3

### State
Measured at start: 28 tests passing, 40 scenarios, 4 output formats
(JSON, HTML, SARIF, JUnit), config + filters + parallel runner. No badge:
a project that runs Gauntlet in CI has no visible, linkable artefact of its
score in its README, so the scorecard produces no network effect and no
reason for a second project to adopt it.

### Comparison to counterparts
Code audit + prior research: promptfoo and garak both benefit from README
badges and shareable report links in their ecosystems; shields-style badges
are the standard distribution mechanism for CI tools (inference from common
CI practice, not a searched claim). No counterpart in the searched set owns
an agent-security grade badge specifically -- this is Gauntlet's intended
differentiator, and it did not exist yet.

### Why it would not be majority adopted as-is
- No badge means no passive discovery: nobody encounters Gauntlet by reading
  another project's README.
- A score that cannot be displayed cannot become a status symbol or a
  competitive pressure between projects, which is the leaderboard mechanism.
- Maintainers get no reputational return for running the tool, so they do
  not run it publicly.

### Technical improvements (bulleted)
- Generate a self-contained SVG grade badge (score + letter grade, colour by grade) from any scorecard
- Add a `gauntlet badge` command that runs a target or reads a scorecard JSON and emits badge.svg plus a markdown snippet
- Support per-category badge data in the SVG title for accessibility
- Document badge embedding in the README

### Built in this iteration
Built: `to_badge_svg()` (self-contained SVG, colour by grade, per-category
scores in the `<title>`), `badge_markdown()`, a `badge` entry in the FORMATS
registry (so `--format badge` also works in runs), and a `gauntlet badge`
command accepting `--target` or an existing `--scorecard` JSON.

### Verified
`pytest -q`: 33 passed (28 + 5 new). `gauntlet badge --target demo-hardened`
prints the markdown snippet and writes a valid SVG. Quickstart scores
unchanged (verified in the full-suite run).

## Iteration 4

### State
Measured at start: 33 tests passing, 40 scenarios, 5 output formats including
badge, config/filters/parallel runner. Adapters are still only demo, HTTP,
and MCP. A real user must hand-write the glue between Gauntlet's
(prompt, context) protocol and their framework's agent object -- the single
largest piece of work between `pip install` and a first scorecard.

### Comparison to counterparts
Web search this iteration (see below in this section's research note):
framework-native integration is the norm. AASTF intercepts LangGraph at
event level and lists CrewAI / OpenAI Agents adapters; promptfoo ships
providers for the major frameworks; DeepTeam is a Python API used inside the
target's own codebase. Gauntlet has no framework adapter at all.
Research note: searched AASTF / promptfoo / DeepTeam framework adapter
support on 2026-11-22; AASTF documents full LangGraph interception with
CrewAI and OpenAI Agents experimental, promptfoo documents YAML-configured
providers and strategies.

### Why it would not be majority adopted as-is
- Every framework community (LangGraph, CrewAI, OpenAI Agents SDK,
  PydanticAI) needs its own 20-line shim written from scratch; most users
  stop there.
- Without named adapters, Gauntlet cannot appear in those frameworks' docs,
  examples, or community answers -- where adoption decisions are made.
- Hand-rolled glue differs per user, so results are not comparable across
  projects, undermining the leaderboard.

### Technical improvements (bulleted)
- Ship optional framework adapters (LangGraph, OpenAI Agents SDK, CrewAI, PydanticAI) behind extras, importing lazily and erroring clearly when absent
- Make adapters accept the framework object (or a fake with the same surface) so they are unit-testable without the frameworks installed
- Register the adapters in resolve_target via an `adapter:` target prefix
- Document each adapter with a minimal usage snippet

### Built in this iteration
Built: `gauntlet/adapters/frameworks.py` with LangGraph, OpenAI Agents SDK,
CrewAI, and PydanticAI adapters. Each wraps an already-constructed agent
object, translates results (last message / final_output / raw / output, plus
tool calls) into the Gauntlet protocol, and imports its framework lazily --
constructing one with no agent raises an ImportError naming the pip extra.
Extras added to pyproject (`agent-gauntlet[langgraph]` etc.), usage in
`docs/ADAPTERS.md`, tests use fakes so the suite stays green with none of the
frameworks installed. One fix in-iteration: CrewAI dict results needed `raw`
in the text-extraction keys.

### Verified
`pytest -q`: 39 passed (33 + 6 new). Quickstart unchanged: 12.8 F vs 100.0 A.

## Iteration 5

### State
Measured at start: 39 tests passing, 40 scenarios, 4 framework adapters plus
demo/HTTP/MCP, 5 output formats. Scenario coverage is the thinnest part of
the project: 40 single-turn, plain-text attacks. No multi-turn escalation,
no encoded payloads, no document/RAG indirect injection beyond one tool-result
case, and nothing MCP-specific despite MCP being the headline surface.

### Comparison to counterparts
Prior research: Argus ships 261 probes including hostile MCP servers and
poisoned tool descriptions; AASTF ships 130+ scenarios; PyRIT's signature
attacks are multi-turn (Crescendo, TAP). Gauntlet's 40 plain single-turn
scenarios are roughly a sixth of Argus's count and miss the attack shapes
(multi-turn, encoded, MCP-native) that the field currently talks about.
(Code-audit inference for Gauntlet's side; counts from prior research.)

### Why it would not be majority adopted as-is
- A battery a maintainer can pass by handling 40 obvious prompts proves
  little; security teams will not gate releases on it.
- MCP servers are the stated wedge, yet no scenario tests poisoned tool
  descriptions, tool rug-pulls, or look-alike tools.
- No encoded or multi-turn attacks means the battery misses the bypasses
  that appear first in real incident write-ups.

### Technical improvements (bulleted)
- Expand 40 to at least 80 scenarios, keeping per-category balance
- Add an MCP-specific category (poisoned descriptions, rug-pull, look-alike tools, credential-fishing parameters)
- Add multi-turn scenarios (runner sends turns in sequence, detector judges the final state, aggregating tool calls and memory across turns)
- Add encoded (base64/rot13-style) and document/RAG indirect-injection payloads

### Built in this iteration
Built: 48 new scenarios in `gauntlet/scenarios/expanded.py` -- 8 more per
original category (PI-09..16, TM-09..16, DE-09..16, MP-09..16, GH-09..16)
plus a new sixth category `mcp_security` (MCP-01..08: poisoned tool
description, rug-pull tool change, look-alike tool, credential-fishing
parameters, hostile tool result, over-broad tool, description-embedded
exfiltration URL, tool-list injection). New shapes include multi-turn
crescendo (turns list; the runner now sends turns in sequence and aggregates
tool calls and memory writes across turns before judging the final state),
base64-encoded payloads, and document/RAG indirect injection. Total is now
88 scenarios. Two earlier-iteration tests hard-coded the old totals/score
(40, 12.8); both were updated to the new measured values (88, 11.5) --
recorded here rather than silently changed.

### Verified
`pytest -q`: 45 passed (39 + 6 new/updated). `gauntlet list`: Total: 88
scenarios. Quickstart: demo-vulnerable 11.5 F (passes 8 of 88 -- it passes
none of the new scenarios, as designed), demo-hardened 100.0 A (88/88).

## Iteration 6

### State
Measured at start: 45 tests passing, 88 scenarios in 6 categories, 4
framework adapters, 5 formats. The score is attack-only: an agent that
refuses every request, including legitimate ones, scores 100 and grade A.
The hardened demo is exactly that agent. AASTF already tracks this failure
mode (its REFUSAL_ECHO finding class, from iteration 4 research); Gauntlet
rewards it.

### Comparison to counterparts
AASTF treats refusal-echo as a distinct informational-risk finding rather
than a pass (searched, iteration 4). lm-eval-style harnesses pair capability
and safety measurements for the same reason (general knowledge, marked as
inference). Gauntlet's single security number is gameable by construction,
and any sophisticated adopter will notice within one run.

### Why it would not be majority adopted as-is
- A perfect score for a useless agent destroys the scorecard's credibility
  with exactly the engineers whose adoption matters.
- Teams cannot use the grade in a README badge if a refuse-everything bot
  earns the same badge as their working agent.
- The leaderboard would rank broken agents at the top.

### Technical improvements (bulleted)
- Add a benign usefulness battery: control tasks a working agent should complete (arithmetic, document Q&A, legitimate tool use, legitimate memory write, summarisation)
- Report security score, usefulness score, and a combined grade separately; never fold usefulness into the security score
- State the combined-grade rule in the methodology: low usefulness caps the combined grade regardless of security score
- Add a refuse-everything test agent to prove the cap works

### Built in this iteration
Built: `gauntlet/scenarios/usefulness.py` (10 benign control tasks with
expected text / tool / memory outcomes), a benign-task handler in the demo
agents, `run_usefulness()`, `combined_grade()` (security grade capped at D
below 50 usefulness, at B below 80), `run_full()`, a `--usefulness` CLI flag,
a `RefuseAllAgent` demo target, and the combined-grade rule written into
docs/METHODOLOGY.md. Security score formula unchanged. One fix in-iteration:
`demo-refuse-all` is now resolved in `resolve_target` like the other demos.

### Verified
`pytest -q`: 50 passed (45 + 5 new). Live CLI check: `gauntlet run --target
demo-refuse-all --usefulness` prints security 100.0 A, usefulness 0.0 (0/10),
combined grade D -- the gaming path is closed. Both real demos score
usefulness >= 80. Quickstart unchanged: 11.5 F vs 100.0 A.

## Iteration 7

### State
Measured at start: 50 tests passing, 88 security scenarios + 10 usefulness
controls, 4 framework adapters, combined grade. MCP support is dynamic only:
Gauntlet can attack an agent through an MCP server, but it cannot answer the
first question an MCP server author asks -- "is my server itself dangerous?"
-- without wiring up a full agent run.

### Comparison to counterparts
Web search this iteration (research note below): MCP scanning is a distinct,
crowded sub-category -- Tencent AI-Infra-Guard includes an MCP server
scanner, Agentic Radar and PowerPwn cover MCP servers, and dedicated MCP
scanners check tool descriptions statically. Gauntlet has no static MCP
analysis at all.
Research note: searched MCP server security scanners on 2026-11-22;
AI-Infra-Guard (Tencent, ~7.4k stars in the parent project's earlier sweep)
lists MCP scanning among its five scanners.

### Why it would not be majority adopted as-is
- MCP server authors -- the fastest-growing target audience -- get nothing
  from Gauntlet until they also have an agent to test.
- A static scan is the lowest-friction first run (no agent, no API key, one
  command); without it Gauntlet's first-run cost is higher than every MCP
  scanner's.
- Risky tool descriptions are visible statically; forcing a dynamic run to
  find them wastes the user's time and the project's credibility.

### Technical improvements (bulleted)
- Add `gauntlet scan-mcp --command ...`: list a server's tools and statically flag risky descriptions and parameters without running an agent
- Flag injection text in tool descriptions, instructions to hide actions from the user, credential-shaped parameters, and over-broad tool capabilities (shell, filesystem, network, payment)
- Emit findings as JSON with severity per finding, and a non-zero exit option for CI
- Make the scanner work on a plain tool list as a library function, testable without a server

### Built in this iteration
Built: `gauntlet/mcp_scan.py` -- `scan_tools()` (pure function over a tool
list: injection phrases in descriptions, "do not tell the user" concealment
language, URLs in descriptions, credential-shaped parameters, broad
capabilities inferred from tool names, generic executors, missing
descriptions; severities critical/high/medium/low with a summary count) and
`scan_server()` (lists tools over the existing stdio client), plus the
`gauntlet scan-mcp --command ... [--out FILE] [--fail-on SEVERITY]` command.

### Verified
`pytest -q`: 54 passed (50 + 4 new, including scan_server against a fake
stdio MCP server and the CLI exit code). Honest note: the bundled
`examples/mcp_server.py` returns 0 tools through the minimal stdio client --
a pre-existing adapter limitation recorded in iteration 10's list; the
scanner itself is verified against the fake server in the test suite.

## Iteration 8

### State
Measured at start: 54 tests passing, 88 + 10 scenarios, static MCP scanner,
5 formats. Runs are ephemeral: the scorecard keeps verdicts and reasons but
not the full record of what was sent and what the target did. A disputed
score cannot be re-checked without re-running the target, which may have
changed -- a direct problem for the leaderboard's rerun/dispute process.

### Comparison to counterparts
Prior research: garak's design centre is its JSONL attempt log (every probe
attempt is a unit of record); PyRIT keeps scored conversation history;
promptfoo writes run outputs that can be compared across versions.
Gauntlet keeps no replayable record. (From iteration 1-2 research.)

### Why it would not be majority adopted as-is
- No trace means no audit: a security team cannot attach evidence of what
  the agent actually did to a ticket or a review.
- Score disputes (certain, once a leaderboard names projects) cannot be
  settled from a record; they require trusting a re-run.
- Regression comparison across versions is manual; nothing can be replayed
  offline in CI without the live target.

### Technical improvements (bulleted)
- Record a JSONL trace for every run: scenario id, prompt/turns, context canary, response text, tool calls, memory writes, verdict
- Add `gauntlet replay TRACE.jsonl` that re-scores a recorded trace with the current detectors, without contacting the target
- Write trace.jsonl alongside every scorecard by default
- Keep trace entries self-contained so a trace from an older version still replays

### Built in this iteration
Built: every result now carries a self-contained trace entry (scenario id,
prompt, turns, full response, verdict); `gauntlet/trace.py` with
`write_trace()` / `read_trace()` / `replay()`; every CLI run and quickstart
writes `trace.jsonl` next to the scorecard; and a `gauntlet replay
TRACE.jsonl [--out DIR] [--fail-under N]` command that re-scores a trace
with the current detectors and never contacts the target. Replay of a trace
from a battery version whose scenarios no longer exist reports those entries
as unscored instead of failing.

### Verified
`pytest -q`: 58 passed (54 + 4 new). Replay reproduces the original score
exactly for both demo targets (tested), and the CLI replay honours
--fail-under.

## Iteration 9

### State
Measured at start: 58 tests passing, 88 + 10 scenarios, trace + replay,
static MCP scan. The battery is closed: a team with a domain-specific
failure (their own tool names, their own canary, a regulation-specific
case) cannot add a scenario without forking the package, so their most
relevant tests live outside Gauntlet and Gauntlet never becomes their
standard.

### Comparison to counterparts
Prior research: garak's probe/detector split and promptfoo's plugin system
are both extension points -- third parties publish probes/plugins without
touching the core repo. DeepTeam has CustomVulnerability. Gauntlet has no
extension point at all. (From iterations 1-2 research.)

### Why it would not be majority adopted as-is
- Closed batteries get forked or abandoned; open ones accumulate community
  scenarios, which is where counterpart counts like 261 come from.
- A security team cannot encode its internal incident as a regression
  scenario, which is the highest-retention use case for a test harness.
- Contributors have no path in, so the maintainer (one person) is the
  bottleneck for all coverage growth.

### Technical improvements (bulleted)
- Load custom scenarios from a user directory of Python files (SCENARIOS list) via `--plugin-dir` and config
- Support entry-point discovery (group `gauntlet.scenarios`) for pip-installed scenario packs
- Validate plugin scenarios against the required schema and fail with a named error, not a traceback
- Ship a documented ~30-line example plugin and test the whole path

### Built in this iteration
Built: `gauntlet/plugins.py` -- `load_plugin_dir()` (imports .py files,
validates every scenario against the required schema, raises PluginError
naming the file and problem, rejects duplicate ids), `load_entry_point_scenarios()`
for pip-installed packs under the `gauntlet.scenarios` entry-point group, and
`load_with_plugins()`. CLI `--plugin-dir` (also via config). Runner now
tolerates plugin categories outside the built-in remediation table.
`examples/my_plugin.py` is the documented ~30-line example.

### Verified
`pytest -q`: 64 passed (58 + 6 new, including a plugin scenario that the
vulnerable demo fails and the shipped example plugin loading). CLI check:
`gauntlet run --target demo-hardened --plugin-dir examples/ --scenario
ACME-01` runs exactly the plugin scenario, 1/1 passed.

## Iteration 10

### State
Measured at start: 64 tests passing, 88 security + 10 usefulness scenarios,
framework adapters, plugins, traces, MCP static scan, 6 formats counting the
badge. Remaining gaps are robustness and packaging: async targets raise or
hang, a flaky target fails a scenario permanently with no retry, there is no
timeout so one hung target stalls a CI job, no progress output on long runs,
exit codes are undocumented, package metadata is minimal, and the MCP stdio
client reads one line per request (the bundled example server returns 0
tools through it, noted in iteration 7).

### Comparison to counterparts
Web search this iteration (research note below): the mature tools all treat
this layer as table stakes -- promptfoo documents exit codes and CI
behaviour across six CI systems, garak runs probes with process-pool
parallelism and writes resumable logs, PyRIT campaigns are async. Gauntlet
at the start of this iteration has none of the async/retry/timeout layer.
Research note: searched promptfoo/garak/PyRIT CI and robustness behaviour on
2026-11-22; promptfoo documents 60+ providers and CI integrations for GitHub
Actions, GitLab, CircleCI, Jenkins, Azure and Bitbucket.

### Why it would not be majority adopted as-is
- Most real agents are async (LangGraph and the OpenAI Agents SDK both are);
  a sync-only harness excludes the majority of real targets.
- One hung or flaky target call failing an entire CI run teaches teams to
  remove the gate, not fix the agent.
- Undocumented exit codes and thin package metadata read as a hobby project
  to a platform team evaluating it for an organisation-wide rollout.

### Technical improvements (bulleted)
- Support async targets (coroutine invoke / async callables) in the runner
- Add per-scenario timeout and retries, recorded in the result when a retry was needed
- Add progress output (`--progress`) for long runs
- Document exit-code semantics (0 pass, 1 below fail-under / scan finding at fail-on level, 2 usage error) in the README
- Package polish: classifiers, extras, CHANGELOG, version bump to 0.2.0, README updated for all new commands and counts

### Built in this iteration
Built: async target support (coroutine callables and async `invoke` are
awaited via asyncio in `_invoke_once`), per-scenario `--timeout` (thread-based
per call) and `--retries` with the attempt count recorded on every result, a
target that keeps failing now scores a recorded failure ("target error: ...")
instead of crashing the run, `--progress` output, documented exit codes
(0/1/2) in the README, package classifiers and a Beta status, CHANGELOG.md,
version bump to 0.2.0, and a README section covering every 0.2.0 addition.
This iteration needed three honest fixes: the first patch's string
replacements missed the runner's current shape (patched by rewriting
`_run_one` and `_invoke` directly), an import inserted by script landed
mid-function (moved to the module top), and only then did the suite go green.

Correction to iteration 5's Verified note: it said the vulnerable demo
"passes 8 of 88". The 8 was its pass count on the original 40; its total
pass count on the 88 battery is 13. The score recorded there (11.5 F) was
and is correct.

### Verified (final, end of iteration 10)
- `pytest -q`: **71 passed, 0 failed** (17 at the start of iteration 1).
- `gauntlet quickstart`: demo-vulnerable **11.5 F, 13/88 passed**;
  demo-hardened **100.0 A, 88/88 passed**.
- `gauntlet list`: 88 scenarios (16 each in the original five categories,
  8 mcp_security), plus 10 usefulness controls reported separately.
- All formats in one run (`--format sarif --format junit --format badge
  --usefulness`): scorecard.sarif, scorecard-junit.xml, badge.svg and
  trace.jsonl written; usefulness and combined grade printed.
- `gauntlet replay trace.jsonl --fail-under 70` reproduces 11.5 F and
  exits 1, as documented.
- MCP paths verified in the suite against a fake stdio MCP server (dynamic
  adapter, static scan, CLI exit codes). Known remaining limitation, stated
  in iteration 7: the bundled examples/mcp_server.py returns 0 tools through
  the minimal one-line-per-request stdio client.
- Verda GPU compute: considered in all 10 iterations, never needed -- all
  targets are local and the detectors are rule-based CPU work.
- Log integrity: this file contains exactly 10 `## Iteration` sections,
  1 through 10, each with State, Comparison, Why-not-adopted, Improvements,
  Built, and Verified subsections.

## Iteration 11

### State
Measured at start (venv /tmp/gv, `pytest -q`, `gauntlet list`): 71 tests
passing, 88 security scenarios + 10 usefulness controls, version 0.2.0.
CLI commands: list, quickstart, run, mcp, badge, scan-mcp, replay. Adapters:
demo (vulnerable/hardened/refuse-all), HTTP, MCP stdio, and framework shims
(LangGraph, OpenAI Agents SDK, CrewAI, PydanticAI) as optional extras.
Outputs: JSON, HTML, SARIF, JUnit, SVG badge, trace.jsonl. The leaderboard
is still 10 named frameworks, every one `unscored`, and there is no code
path that can change that: no LLM-backed target exists, no leaderboard
runner exists, and `leaderboard.json` / `index.html` are hand-maintained
files. No API key is present in this VM's environment (checked:
no OPENAI_API_KEY / ANTHROPIC_API_KEY / GAUNTLET_LLM_API_KEY), and Docker
is not installed. Verda considered: not needed -- an LLM target is API
calls, not local GPU work.

### Comparison to counterparts
From web search this iteration: promptfoo runs any OpenAI-compatible
provider string (`openai:<model>`, custom API providers), runs evals
concurrently, and its results carry stats that CI tooling reads directly
(promptfoo docs/Jenkins integration; Testkube's parser post notes every
major harness -- promptfoo, DeepEval, lm-eval -- ships its own results
file, and the recurring failure is results not tied to a pinned model and
prompt version). lm-eval-harness's whole adoption story is a reproducible
leaderboard: pinned tasks, pinned model revisions, published commands.
Gauntlet at this stage cannot score anything a user did not write an
adapter for, and its leaderboard is a promise, not a pipeline.

### Why it would not be majority adopted as-is
- The leaderboard -- the project's stated differentiator -- has no
  pipeline behind it. A hand-edited JSON file cannot produce a single
  defensible score, so the public scorecard does not exist in practice.
- No LLM-backed target: a user with a real agent built on a chat model
  must first write an HTTP wrapper before Gauntlet can touch it. Every
  counterpart accepts a model/endpoint string directly.
- No version pinning in leaderboard entries: even a manual run could not
  record which target version, model and battery produced a score.
- Scores are not regenerable: nothing turns scorecard outputs back into
  the leaderboard, so any published number would drift from the artifacts.

### Technical improvements (bulleted)
- OpenAI-compatible LLM reference agent adapter: system prompt and canary
  taken from scenario context, key read only from the environment, model
  output parsed for text plus structured tool_calls / memory_writes.
- `llm:<model>` target resolution in the runner, configured by
  GAUNTLET_LLM_BASE_URL / GAUNTLET_LLM_MODEL / GAUNTLET_LLM_API_KEY
  (OPENAI_API_KEY accepted), so the full battery runs against a real
  model endpoint with no wrapper code.
- `leaderboard/run_leaderboard.py`: reads `leaderboard/targets.json`,
  runs the battery per configured target, writes per-target scorecards,
  and regenerates `leaderboard.json` + `index.html` from the scorecard
  outputs only. Entries with no configured target, or whose target cannot
  run (e.g. no API key), stay `unscored` -- never estimated.
- Version pinning per entry: target spec, declared target version, tool
  version and run date recorded with every scored entry.
- Tests against a local fake OpenAI-compatible HTTP server (the only
  honest option in this VM: no live key is available), covering adapter
  parsing, missing-key failure, and leaderboard regeneration.


### Built in this iteration
- `gauntlet/adapters/llm.py`: `OpenAICompatibleAgent` -- builds an agent
  from a raw OpenAI-compatible chat model. System prompt (with planted
  canary) comes from scenario context; the model is told which tools it
  has and to report tool calls / memory writes as JSON; plain text,
  structured JSON, and native `message.tool_calls` replies are all
  parsed. Key read only from GAUNTLET_LLM_API_KEY / OPENAI_API_KEY;
  missing key raises `LLMConfigError` naming the env vars. Base URL and
  model from GAUNTLET_LLM_BASE_URL / GAUNTLET_LLM_MODEL.
- Runner target resolution: `llm:<model>` and `openai:<model>` now run
  the full battery against a model endpoint with no wrapper code.
- `leaderboard/run_leaderboard.py` + `leaderboard/targets.json` (the 10
  existing frameworks with `target: null`, plus an `llm:` reference
  entry): runs each configured target, writes scorecards (JSON, HTML,
  SARIF, JUnit, badge, trace) under `results/<slug>/`, and regenerates
  `leaderboard.json` + `index.html` from those scorecards only, recording
  target spec, declared version, tool version and run date per scored
  entry. Unconfigured or unrunnable entries stay unscored.
- `tests/test_iteration11.py`: 6 tests against an in-process fake
  OpenAI-compatible server (canary leak, structured tool-call parsing,
  missing-key failure, target resolution, leaderboard regeneration with
  scored/unscored separation, full battery against the fake model).

### Verified
- New tests: 6 passed. Full suite: **77 passed** (was 71).
- Quickstart unchanged: vulnerable 11.5 F (13/88), hardened 100.0 A (88/88).
- End-to-end against a standalone fake OpenAI-compatible server in /tmp
  (a scripted stand-in model that leaks its canary when asked, dummy
  local key, nothing real): `gauntlet run --target llm:fake-model`
  scored **60.6 D, 57/88**; `run_leaderboard.py` against a temp config
  scored that fake reference entry 60.6 D and left LangGraph unscored.
- HONEST LIMIT: no live LLM endpoint was verified -- this VM has no API
  key for any provider, so the pipeline is verified against a local fake
  OpenAI-compatible server only. The first real leaderboard score still
  requires a real key and a real run.
- The real `leaderboard/leaderboard.json` was checked after all runs:
  still 10 entries, all unscored. No fake score was written to it.


## Iteration 12

### State
Measured at start: 77 tests passing, 88 scenarios + 10 usefulness
controls, version 0.2.0, plus iteration 11's LLM adapter and leaderboard
pipeline. Distribution state, from code audit: the package has only ever
been installed editable (`pip install -e .`) in a dev venv. No wheel or
sdist has ever been built, so it is unknown whether a non-editable
install even contains the scenario data and CLI. No Dockerfile. The
GitHub Action has no branding, no declared outputs (a workflow cannot
read the score or grade from it), and installs the package by name from
PyPI -- which cannot work before a first release exists. No
CONTRIBUTING.md, SECURITY.md, issue templates, or pre-commit config.
Docker is not installed in this VM (`docker: command not found`), so a
container build cannot be run here. Verda considered: not needed.

### Comparison to counterparts
Code-audit comparison (no new web research this iteration; based on
iterations 1-11 research): promptfoo ships as an npm package, a Docker
image, and a GitHub Action whose outputs workflows consume; garak ships
on PyPI with a documented install and a container story; both have
contributor documentation and security policies visible on their repos.
Gauntlet has an editable-install dev loop and nothing else: every
distribution channel a majority of users would actually use -- pip from
a built artifact, Docker, a marketplace-grade Action -- is either
unverified or missing.

### Why it would not be majority adopted as-is
- An unverified packaging path is a broken packaging path: if the wheel
  misses files, the first `pip install` a user tries fails or silently
  runs an empty battery, and they never come back.
- No Docker image: enterprise and CI users who will not install Python
  packages on runners have no way to run the harness at all.
- The Action exposes no outputs, so it cannot be used as a real CI gate
  (comment the grade on a PR, fail on regression) without shell scraping.
- No contributor or security surface: a security tool without a
  SECURITY.md disclosure path and issue templates fails the first
  review by any security team evaluating it.

### Technical improvements (bulleted)
- Build sdist + wheel and verify a clean-venv install from the wheel
  (not editable) passes quickstart and lists all 88 scenarios.
- Dockerfile (slim Python, installs the package, `gauntlet` entrypoint)
  plus .dockerignore; build it where Docker exists, validate statically
  and record the limitation where it does not.
- Action polish: marketplace branding, documented inputs (including
  output formats), and declared outputs (score, grade, scorecard path)
  written from the produced scorecard.json.
- Contributor tooling: CONTRIBUTING.md, SECURITY.md, issue templates
  (bug report, feature request, scenario proposal), pre-commit config.
- MANIFEST.in so the sdist carries docs, leaderboard tooling and the
  Action definition, not just the package.


### Built in this iteration
- `Dockerfile` (python:3.12-slim, installs the package, `gauntlet`
  entrypoint, OCI labels) + `.dockerignore`.
- `action.yml` rewritten: marketplace branding (shield/red), documented
  inputs (target incl. `llm:<model>`, fail-under, out, formats, version
  with a pre-PyPI fallback to installing from the action checkout), and
  declared outputs -- score, grade, scorecard-path -- written to
  `$GITHUB_OUTPUT` from the produced scorecard.json, with the fail-under
  exit code preserved after outputs are written.
- `CONTRIBUTING.md` (stdlib-only rule, scenario/adapter guides,
  calibration and battery-version rules), `SECURITY.md` (private
  disclosure path, 14-day critical window pointer), issue templates
  (bug report, feature request, scenario proposal), `.pre-commit-config.yaml`.
- `MANIFEST.in`: sdist now carries docs, leaderboard tooling, examples
  and the Action definition.
- `tests/test_iteration12.py`: 5 tests (Dockerfile shape, Action
  branding/outputs, contributor/security surface, manifest, version
  consistency between pyproject and `gauntlet.__version__`).

### Verified
- New tests: 5 passed. Full suite: **82 passed** (was 77).
- Quickstart unchanged: vulnerable 11.5 F, hardened 100.0 A.
- Wheel + sdist built with `python -m build` (agent_gauntlet-0.2.0,
  32 files in the wheel). Clean venv `/tmp/gwheel` installed **from the
  wheel only** (not editable): `gauntlet list` shows 88 scenarios and
  quickstart reproduces 11.5 F / 100.0 A exactly.
- sdist contents checked: docs, `leaderboard/run_leaderboard.py` and
  `action.yml` are included.
- Docker: `docker` is NOT installed in this VM, so no image build was
  possible here. The Dockerfile passed a static instruction-level
  validation, and the exact steps it runs (pip install of the package,
  `gauntlet` entrypoint) are the same steps verified via the wheel
  install. Recorded as a limitation, not a pass: the image build itself
  remains unverified until run on a machine with Docker.


## Iteration 13

### State
Measured at start: 82 tests passing, 88 scenarios + 10 usefulness
controls, version 0.2.0, wheel verified from a clean venv, leaderboard
pipeline in place. Interop state, from code audit: zero. A promptfoo
user with an existing red-team config, or a garak user with a probe
list, has no way to bring any of that work into Gauntlet -- every test
must be rewritten by hand in Gauntlet's scenario format, and Gauntlet
results cannot be fed back into the reporting tools those teams already
use. Verda considered: not needed.

### Comparison to counterparts
From web search this iteration: promptfoo configs are YAML with
`prompts`, `providers`, and `tests:` entries carrying `vars:` and
`assert:` lists -- `not-contains` / `not-matches` for leak checks and
`llm-rubric` for judged checks (multiple real-world configs reviewed,
including MCP red-team examples using exactly this shape). Its results
JSON is a versioned envelope (`results.results[]` with per-row
`success`, `score`, `gradingResult.componentResults`, plus
`results.stats.successes/failures`) that CI tooling already parses.
garak is invoked by probe family name -- `promptinject`, `dan`,
`encoding`, `leakreplay`, `malwaregen`, `knownbadsignatures`,
`continuation`, `xss` -- with dotted sub-probes
(`promptinject.HijackHateHumans`). Neither tool imports the other's
formats; the migration cost is paid entirely by the user, which is
exactly the gap an importer can close.

### Why it would not be majority adopted as-is
- Switching cost is total: an existing promptfoo red-team suite or a
  garak probe habit represents real invested work, and a tool that
  demands it be thrown away loses to the incumbent by default.
- No export path means Gauntlet results cannot enter the dashboards
  and CI reporting a team already has, so Gauntlet stays a side tool
  run once, not a gate run always.
- garak users think in probe families; without a name mapping, even
  the scenario selection conversation ("run the injection family")
  cannot happen.

### Technical improvements (bulleted)
- promptfoo importer: read promptfoo-style config (YAML or JSON),
  substitute `vars` into the prompt template, and convert deterministic
  assertions (`not-contains`, `not-contain-all`, `not-regex` as literal
  where possible) into Gauntlet scenario detectors. Non-deterministic
  assertions (`llm-rubric`, model-graded) are reported as unconverted
  with a reason, never silently dropped.
- Imported scenarios are runnable: `gauntlet import-promptfoo` writes a
  scenario JSON file and `gauntlet run --extra-scenarios` merges it
  into a run.
- garak probe-name mapping: known probe families (and dotted
  sub-probes) map to Gauntlet categories/scenario selections;
  `gauntlet list --garak a,b` and `gauntlet run --garak a,b`; unknown
  names are reported, not ignored.
- promptfoo-compatible export: `gauntlet export-promptfoo` turns a
  Gauntlet scorecard into promptfoo's results-JSON shape (version 3
  envelope, per-row success/score/gradingResult, stats).
- docs/INTEROP.md: the migration path, what converts, what does not,
  and why (LLM-judged assertions have no deterministic equivalent).


### Built in this iteration
- `gauntlet/miniyaml.py`: a small stdlib YAML-subset parser (block maps
  and sequences, flow maps/lists, quoted scalars) covering the shape
  promptfoo configs actually use; anything outside the subset raises
  rather than guessing. JSON configs are read natively.
- `gauntlet/interop.py`:
  - `import_promptfoo`: substitutes `vars` into the prompt template,
    merges `defaultTest` assertions, converts `not-contains` /
    `not-contain-all` / literal `not-regex` into `forbidden_text`
    detectors. `llm-rubric`, real regexes, and positive `contains`
    assertions are returned as named unconverted items with reasons.
  - `garak_selection` + `GARAK_MAP`: 13 probe families mapped to
    Gauntlet categories, dotted sub-probes resolve to their family,
    unknown names reported.
  - `export_promptfoo`: scorecard -> promptfoo results-JSON (version 3
    envelope, per-row success/score/gradingResult.componentResults,
    stats), with the Gauntlet score/grade under a `gauntlet` key.
- CLI: `gauntlet import-promptfoo FILE --out`, `gauntlet export-promptfoo
  SCORECARD`, `gauntlet list --garak a,b`, `gauntlet run --garak a,b`,
  and `gauntlet run --extra-scenarios FILE` to run imported scenarios.
- `docs/INTEROP.md` (conversion table, garak mapping table, what does
  not convert and why) and `examples/promptfooconfig.yaml`.
- `tests/test_iteration13.py`: 6 tests (YAML + JSON import, detector
  conversion, unconverted reporting, imported scenarios discriminating
  vulnerable vs hardened, garak mapping incl. unknown names, export
  shape, CLI round trip).

### Verified
- New tests: 6 passed. Full suite: **88 passed** (was 82).
- Quickstart unchanged: vulnerable 11.5 F, hardened 100.0 A.
- CLI smoke: `list --garak promptinject,leakreplay` selects exactly 32
  scenarios; importing the example config yields 3 scenarios and prints
  the 2 unconverted assertions with reasons; a run with
  `--extra-scenarios` + `--scenario IMP-01` against demo-hardened
  passes 1/1.
- Recorded scope decision: full YAML is impractical and unnecessary in
  a stdlib-only core, so the importer supports the documented subset
  and fails loudly outside it -- the alternative (a PyYAML dependency)
  would break the zero-dependency install that iterations 1-12
  established. garak probes are attack families, so the mapping is by
  category, not a false 1:1 probe-to-scenario claim.


## Iteration 14

### State
Measured at start: 88 tests passing, 88 scenarios + 10 usefulness
controls, version 0.2.0. Coverage state, measured from the scenario
data: OWASP ASI codes present are ASI01 (19 scenarios), ASI02 (18),
ASI03 (4), ASI04 (8), ASI05 (1), ASI06 (16), ASI07 (5), ASI08 (8),
ASI09 (3), ASI10 (6) -- all ten codes have at least one scenario, but
ASI05 has exactly one and ASI09 three, and none of this is visible
anywhere: there is no coverage command, no machine-readable coverage
map, and no MITRE ATLAS mapping at all. There is also no battery
version: a scorecard says tool version 0.2.0 but cannot say which
battery produced the score, and there is no calibration set -- if a
detector or demo agent changes behaviour tomorrow, no test would catch
a silent score change on the reference agents. Verda considered: not
needed.

### Comparison to counterparts
Code-audit comparison (no new web research this iteration; based on
iterations 1-13 research): garak and AASTF both publish their framework
mappings (OWASP / MITRE ATLAS) as part of the product, and lm-eval's
credibility rests on versioned tasks whose expected results are pinned.
Gauntlet's methodology doc *claims* OWASP ASI alignment, but a user
cannot ask the tool "what do you cover, and where are you thin?" and
get an answer from data -- the claim is unverifiable marketing copy
until the coverage map is machine-readable and the demo-agent verdicts
are pinned as a calibration set.

### Why it would not be majority adopted as-is
- Security teams buy framework coverage they can audit: an unmapped
  battery cannot be put in front of a compliance review, and thin spots
  (ASI05: one scenario) are invisible until an auditor finds them.
- Without a battery version, two scores from different months are
  silently incomparable; the first time a score changes because the
  battery changed, every published score loses credibility.
- Without a calibration set, score disputes are arguments. With one,
  they are a diff: rerun the three reference agents and compare against
  pinned expected verdicts, mechanically.

### Technical improvements (bulleted)
- `gauntlet coverage` command + `gauntlet/coverage.py`: per-framework
  coverage from the live scenario data -- OWASP ASI01-ASI10 with
  counts and scenario ids, MITRE ATLAS techniques per category, gaps
  (zero coverage) and thin spots (<3 scenarios) named in text and JSON.
- ATLAS mapping per category, with the honest caveat recorded where
  ATLAS has no exact technique (memory poisoning maps to the nearest
  analogues and is flagged as such).
- Battery versioning: `BATTERY_VERSION` in the scenario package,
  stamped into every scorecard, with battery release rules and a
  battery changelog in docs/BATTERY.md (scenario or detector changes
  bump the battery; scores compare only within a battery version).
- Calibration set: expected verdicts for demo-vulnerable,
  demo-hardened and demo-refuse-all across all 88 scenarios, plus the
  usefulness battery, generated from real runs into
  `tests/fixtures/calibration.json`, regenerated by
  `python -m gauntlet.calibration --write`, and asserted exactly in
  tests -- any silent behaviour change fails the suite.
- docs/COVERAGE.md: the human-readable coverage summary with the
  measured counts and named thin spots.


### Built in this iteration
- `gauntlet/coverage.py` + `gauntlet coverage [--format text|json]`:
  coverage computed from live scenario data -- all ten OWASP ASI codes
  with counts, scenario ids and status; MITRE ATLAS techniques per
  category (also stamped onto every scenario result in a scorecard);
  gaps and thin spots named. Measured result at battery 1.1.0: no ASI
  gaps; thin = ASI05 (1 scenario), with ASI09 (3) and ASI03 (4) next.
  Memory-poisoning and MCP ATLAS mappings are flagged "analogue" in
  the data, not passed off as exact.
- Battery versioning: `BATTERY_VERSION = "1.1.0"` in
  `gauntlet/scenarios/__init__.py`, stamped into every scorecard as
  `battery_version` alongside the tool version (the runner now reads
  the tool version from `gauntlet.__version__` instead of a hard-coded
  string). Bump rules and the battery changelog are in docs/BATTERY.md.
- Calibration set: `gauntlet/calibration.py` generates expected
  verdicts for demo-vulnerable, demo-hardened and demo-refuse-all on
  all 88 scenarios plus the usefulness battery from real runs;
  pinned at `tests/fixtures/calibration.json` (vulnerable 11.5 F,
  hardened 100.0 A, refuse-all security 100.0 A with usefulness 0.0)
  and asserted exactly in tests.
- `docs/COVERAGE.md`: human-readable coverage summary with the
  measured ASI table and the thin spots named.
- `tests/test_iteration14.py`: 5 tests (coverage totals, ATLAS honesty
  flags, battery stamp, full calibration match, CLI coverage).

### Verified
- New tests: 5 passed. Full suite: **93 passed** (was 88).
- Quickstart unchanged: vulnerable 11.5 F, hardened 100.0 A -- the
  calibration file confirms these are the pinned expected values, not
  just today's output.
- `gauntlet coverage` prints the ASI table with ASI05 marked thin;
  `--format json` emits the same data machine-readably.
- The calibration test is a real gate: it re-runs all three reference
  agents and diffs every one of the 88 verdicts plus usefulness
  against the pinned file.


## Iteration 15

### State
Measured at start: 93 tests passing, 88 scenarios + 10 usefulness
controls, tool 0.2.0, battery 1.1.0, calibration pinned. Enterprise
state, from code audit: a scorecard records target, score, grade and
tool/battery versions, but no timestamp, no duration, no seed, and no
target version -- a run cannot be audited after the fact. There is no
way to compare two scorecards except by eye: no diff, so "did the new
prompt regress anything?" has no mechanical answer. The HTTP adapter
makes exactly one attempt per scenario and treats a transient 429 as a
target answer. Scenario order is fixed but undocumented as a
reproducibility property, and there is no documented flow for a team
to run the leaderboard pipeline on their own infrastructure.
Verda considered: not needed -- this is orchestration, not compute.

### Comparison to counterparts
From web search this iteration: the reproducibility bar has moved --
Bernstein's bench bundles make every score recomputable from embedded
run receipts with suite hashes and signed baselines, and its CI story
is a SARIF report plus a check-run delta against a baseline; multiple
current eval harnesses (AI Eval Runner, PromptPolygraph) ship run
stores where every run is tagged with dataset version and git SHA,
seeded comparison, and a regression diff as a first-class command.
The common thread in the harness literature: pin everything that can
change an answer (model, prompt, dataset version, scorer version,
seed) and record it per run, or the score is not evidence. Gauntlet
pins the battery (iteration 14) but not the run.

### Why it would not be majority adopted as-is
- No diff means no regression workflow, and regression gating is the
  main reason teams keep an eval tool in CI after the first run.
- No per-run metadata means scores cannot be audited, reproduced, or
  compared fairly -- an enterprise security review will ask "which
  target version, when, how long, what seed?" and get no answer.
- One-attempt HTTP calls make large batteries against rate-limited
  endpoints flaky; flaky security gates get disabled.
- No self-hosted leaderboard flow means the pipeline from iteration 11
  only runs on the maintainer's machine, which does not scale to
  community or company-internal leaderboards.

### Technical improvements (bulleted)
- `gauntlet diff A B`: score and grade delta, per-category deltas, and
  per-scenario regressions (pass->fail) and fixes (fail->pass), with
  `--fail-on-regression` for CI.
- Per-run metadata in every output format: target, target version,
  tool version, battery version, UTC timestamp, duration, seed and
  scenario count -- in JSON natively, in the HTML header, as SARIF run
  properties, and as JUnit properties.
- Deterministic seeding: `--seed` fixes scenario execution order via a
  seeded shuffle and is recorded in metadata, so a run is replayable
  in the same order.
- HTTP target rate-limit handling: retries with exponential backoff on
  429/5xx, honouring Retry-After (capped), configurable via constructor
  or GAUNTLET_HTTP_RETRIES / GAUNTLET_HTTP_BACKOFF.
- Self-hosted leaderboard flow: `examples/leaderboard-update.yml`, a
  scheduled GitHub Actions workflow that runs
  `leaderboard/run_leaderboard.py` and uploads the regenerated
  leaderboard as an artifact (it commits nothing), documented in
  docs/LEADERBOARD_OPS.md.
- Version bump to 0.3.0 with a CHANGELOG entry covering iterations
  11-15.


### Built in this iteration
- `gauntlet/diff.py` + `gauntlet diff A B [--fail-on-regression]`:
  score/grade delta, per-category deltas, per-scenario regressions and
  fixes, added/removed scenarios, and a warning when battery versions
  differ.
- Per-run metadata on every card: target, target version, tool
  version, battery version, UTC timestamp, duration, seed, scenario
  count, jobs. Present in JSON natively, in the HTML header, as SARIF
  run properties, and as JUnit properties.
- Deterministic seeding: `run(..., seed=N)` / `gauntlet run --seed N`
  shuffles scenario order with `random.Random(N)` -- same seed, same
  order, recorded in metadata.
- HTTP adapter rebuilt with backoff: 429/5xx and connection errors
  retry with exponential backoff, Retry-After honoured and capped;
  `GAUNTLET_HTTP_RETRIES` / `GAUNTLET_HTTP_BACKOFF` env configuration;
  non-transient errors still fail closed on the first attempt.
- `examples/leaderboard-update.yml` (scheduled + dispatch, artifact
  upload, commits nothing) and `docs/LEADERBOARD_OPS.md`.
- Version 0.3.0: pyproject, `gauntlet.__version__`, CHANGELOG, README
  section. One stale test from iteration 10 pinned the literal version
  "0.2.0"; it was updated to assert the invariant (package version ==
  scorecard version, now 0.3.0) and the change is recorded here rather
  than hidden. Calibration fixture regenerated at 0.3.0.
- `tests/test_iteration15.py`: 8 tests (diff both directions and
  identity, metadata in all four formats, seed determinism and order
  effect, 429-then-success backoff with attempt counting, non-transient
  failure, CLI diff exit codes, version/workflow presence).

### Verified
- New tests: 8 passed. Full suite: **101 passed** (was 93).
- Quickstart unchanged: vulnerable 11.5 F (13/88), hardened 100.0 A (88/88).
- CLI diff verified live: vulnerable -> hardened reports +88.5, 0
  regressions, 75 fixes; metadata on a seeded run shows seed 42,
  battery 1.1.0, tool 0.3.0, timestamp and duration.
- Wheel rebuilt at 0.3.0 and re-verified from a second clean venv
  (install from wheel only): 88 scenarios, quickstart scores and
  `gauntlet coverage` all reproduce.
- The real leaderboard is still 10 entries, all unscored: iterations
  11-15 built and verified every part of the scoring pipeline, and no
  score was published for any real project, because no live target was
  ever run. That remains the honest state, and the first real run is
  now a one-command operation for whoever holds an API key.

## Summary after iteration 15
Tool 0.3.0, battery 1.1.0: 88 security scenarios + 10 usefulness
controls, 101 tests passing, targets from demo/callable/HTTP/MCP/LLM
endpoint plus four framework adapters, outputs in JSON, HTML, SARIF,
JUnit and SVG badge with traces, replay, diff, coverage and metadata,
promptfoo/garak interop both directions, a leaderboard pipeline that
regenerates from real runs only, and packaging verified from a built
wheel. Every technical blocker named across iterations 1-15 has either
been built or is recorded above with its reason (Docker image build
unverified in this VM; first live LLM score awaiting a real API key).
What remains between this repo and majority adoption is no longer
technical: publishing, the first real leaderboard runs with maintainer
notification, and distribution work -- all explicitly out of scope for
this log, and none of it done.

## Postscript -- parent verification, 2026-11-22

Independent re-verification from a different working directory (/tmp) found 4 tests failing with FileNotFoundError: tests in iterations 11, 13, and 15 used repo-relative paths (examples/..., leaderboard/run_leaderboard.py) and only passed when pytest ran from the repo root. Fixed by anchoring those paths to the test file's location (pathlib.Path(__file__).parent.parent). After the fix: 101 passed from /tmp and 101 passed from the repo root.

## Iteration 16

### State
Measured at start: tool 0.3.0, battery 1.1.0, 88 security scenarios + 10 usefulness controls, 101 tests passing (repo root and /tmp), leaderboard 10 entries all unscored. Step 0 of this run extracted the adoption backlog (docs/ADOPTION_BACKLOG.md): 52 distinct items from the 15 Why-not sections plus the Step-0 code audit -- 44 FIXED, 5 PARTIAL (B10, B32, B37, B40, B44), 3 OPEN (B50, B51, B52). Verda considered: not needed for this iteration (local stdio work).

### Comparison to counterparts
Code audit (no new web research this iteration): every counterpart MCP client is built on the official MCP SDK, which matches responses to requests by id and tolerates notifications. Gauntlet's hand-rolled client read exactly one line per request, and its bundled "example server" was a print stub -- so the project's own MCP quickstart path could not work end to end, a defect no counterpart ships.

### Why it would not be majority adopted as-is
Remaining backlog at start of this iteration: B10, B32, B37, B40, B44 (partial), B50, B51, B52 (open). This iteration's slice:
- B50: the bundled MCP example is not a server, and the stdio client desynchronises on any server that emits notifications -- the first MCP run a new user tries can return zero tools and an empty battery.
- B52 (part): there is no one-command demo; the first-run story is a README paragraph, not a command.

### Technical improvements (bulleted)
- Replace the example stub with a real minimal MCP stdio server (initialize / tools/list / tools/call, two tools)
- Fix the client: read until the response with the matching id, skip notifications, answer server-initiated requests with method-not-found
- Send common argument aliases (text/note) so strict-schema tools accept probe calls
- Add a `gauntlet demo` one-command showcase and friendly CLI errors (exit 2 + hint) for unknown targets and missing files

### Built in this iteration
- examples/mcp_server.py rewritten as a real MCP server (echo, store_note); client request loop fixed in gauntlet/adapters/mcp.py; `gauntlet demo` added; main() wrapped so ValueError/FileNotFoundError print an error plus a hint and return 2; tests/test_iteration16.py (6 tests, incl. a noisy-server fixture that emits a notification before every response).

### Verified
- Bundled example: probe lists ['echo', 'store_note']; `gauntlet mcp` end-to-end run scores it 73.3 C (66/88 at battery 1.1.0); scan-mcp finds its 2 tools. Full suite: 107 passed. Backlog: B50 -> FIXED (pending the packaged-copy fix in iteration 20 for wheel installs), B52 -> PARTIAL.

## Iteration 17

### State
Measured at start: 107 tests passing, 91 CLI-listed lines (88 scenarios + header/total lines), coverage: ASI05 = 1 scenario (thin), all other ASI codes >= 3, gaps none. Remaining backlog: B10, B32, B37, B40, B44 (partial), B51, B52 (open/partial).

### Comparison to counterparts
Code audit against the iteration-14 coverage data: counterparts publish framework mappings with no single-scenario cells; ASI05 (Unexpected Code Execution) at 1 scenario was the one cell an auditor could dismiss, and `gauntlet coverage` itself flagged it.

### Why it would not be majority adopted as-is
- B44: a compliance reviewer sees a battery whose code-execution coverage is a single scenario; the tool's own coverage command calls it thin.

### Technical improvements (bulleted)
- Add at least 2 ASI05 scenarios (code from documents, unreviewed install scripts, spreadsheet formula evaluation)
- Bump the battery version (minor), regenerate the calibration set, and regenerate coverage/taxonomy docs from live data
- Update the tests that pinned the old battery size/score values to the new measured values, recording each change

### Built in this iteration
- gauntlet/scenarios/coverage_expansion.py: TM-17 (critical), TM-18, TM-19, all ASI05 tool_misuse with shell_exec/run_code detectors; battery 1.1.0 -> 1.2.0; calibration regenerated; docs/COVERAGE.md and docs/SCENARIO_TAXONOMY.md regenerated/appended; docs/BATTERY.md 1.2.0 entry; tests/test_iteration17.py. Fifteen older tests pinned battery-1.1.0 counts (88) or scores (vulnerable 11.5) and were updated to the measured battery-1.2.0 values (91 scenarios, vulnerable 12.3 F); one iteration-14 test pinned the thin spot itself and now asserts thin == [] and ASI05 == 4.

### Verified
- `gauntlet coverage`: ASI05 4 scenarios, gaps none, thin none; every ASI code >= 3. Full suite: 110 passed. Quickstart: vulnerable 12.3 F, hardened 100.0 A (91/91). Backlog: B44 -> FIXED.

## Iteration 18

### State
Measured at start: 110 tests passing, 91 scenarios, battery 1.2.0, leaderboard still 10 entries all unscored, real-target pipeline verified only against a local fake server (iteration 11). Remaining backlog: B10, B32, B37, B40 (partial), B51, B52 (open/partial).

### Comparison to counterparts
Web research was not repeated; the iteration-11/13 research stands: promptfoo and garak publish results against real models as a matter of routine. Gauntlet's leaderboard -- its differentiator -- still contained zero real runs, which is the single largest credibility gap in the project.

### Why it would not be majority adopted as-is
- B51/B32: no real target has ever been scored; every published number is a demo agent's.
- B10: with no real scores, the badge/leaderboard reputational loop cannot start.

### Technical improvements (bulleted)
- Score a real target: try (a) a live provider key already in the environment, then (b) Verda-hosted open weights, then (c) real local MCP servers -- in that order, recording which ran
- Support `mcp:` target strings in the runner so MCP servers are first-class leaderboard targets
- Add the real targets to leaderboard/targets.json and let the pipeline produce the scores; nothing hand-entered

### Built in this iteration
- `mcp:` prefix in runner.resolve_target. Leaderboard pipeline run (jobs=6) against live targets. Option (a) Anthropic: a key exists through the registered connector and lists models, but message calls return a billing error (credit balance too low), so it could not run -- recorded, not worked around. Option (a) via DeepSeek (registered connector, OpenAI-compatible): the credential surrogate was fetched in memory by a /tmp launcher and passed to the adapter through its documented environment variables; never printed or written to any file. Option (b) Verda: not used -- no Verda CLI or credential exists in this VM, and option (a) succeeded. Option (c): the official MCP filesystem server installed from npm and run locally.

### Verified
- REAL SCORES, produced by leaderboard/run_leaderboard.py on 2026-11-23, battery 1.2.0, scorecards under leaderboard/results/:
  - LLM reference agent (OpenAI-compatible) on the live DeepSeek API, model deepseek-flash (DeepSeek-V4.1-Flash): **91.7, grade A, 84/91**.
  - MCP reference filesystem server (@modelcontextprotocol/server-filesystem@2.4.0, npm), dynamic battery via the stdio adapter: **87.2, grade B, 82/91**; `gauntlet scan-mcp` on the same server: 16 tools, 11 findings.
- Honest caveat: the filesystem server's dynamic score is high partly because the probe's generic arguments do not match its tool schemas, so most calls error instead of acting; for this server the static scan is the sharper signal. Stated in the leaderboard entry note and the backlog.
- leaderboard.json after the run: 12 entries, 2 scored, 10 unscored. Full suite still 110 passed at the end of this iteration (pipeline run does not change code paths under test). Backlog: B51, B32, B10 -> FIXED.

## Iteration 19

### State
Measured at start: 110 tests passing, 91 scenarios, 2 real leaderboard scores. Remaining backlog: B37 (Docker, partial), B40 (promptfoo subset, partial), B52 (partial: demo exists, README not yet followed from a clean wheel).

### Comparison to counterparts
Code audit: promptfoo itself parses full YAML (it is a Node tool with a real YAML parser); Gauntlet's stdlib subset parser was the only importer among counterparts that could silently meet a config it could not read. On Docker: counterparts ship images; Gauntlet's Dockerfile had never produced a running container anywhere.

### Why it would not be majority adopted as-is
- B40: a promptfoo user whose config uses anchors or merge keys hits the subset parser's limits on the first migration step.
- B37: an unverified Dockerfile is a promise, not an image.

### Technical improvements (bulleted)
- Use PyYAML when installed (optional extra), keeping the subset parser as the zero-dependency fallback
- Give each unconvertible assertion type its own actionable explanation
- Verify the Dockerfile's exact steps daemon-free (clean copy, pip install, entrypoint) in a checked-in script, and record precisely what remains unverified

### Built in this iteration
- gauntlet/interop.py: _load_config prefers yaml.safe_load, falls back to miniyaml; per-type unconverted reasons (model-graded -> canary or plugin-detector path; performance -> out of scope by design; provider-specific -> INTEROP.md table). pyproject extra: promptfoo = [PyYAML>=6]. scripts/verify_docker_equivalent.sh performs the Dockerfile's steps (copy the same files, pip install --no-cache-dir equivalent, run the gauntlet entrypoint: --help, list, quickstart) in a clean temp dir + venv. docs/INTEROP.md updated. tests/test_iteration19.py (3 tests, including an anchored/merge-key promptfoo config parsed through PyYAML). Docker attempts recorded: no docker, podman, buildah, or nerdctl binary exists in this VM and none can be installed without root.

### Verified
- verify_docker_equivalent.sh: "Total: 91 scenarios", quickstart comparison printed, DOCKER-EQUIVALENT OK. Full suite: 113 passed. Backlog: B40 -> FIXED (model-graded assertions remain unconvertible by design, now with exact guidance); B37 -> PARTIAL with the blocker stated (base image + daemon behaviour need a machine with Docker).

## Iteration 20

### State
Measured at start: tool 0.3.0, battery 1.2.0, 113 tests passing, 91 scenarios, leaderboard 12 entries / 2 scored with real runs. Remaining backlog: B37 PARTIAL (external blocker), B52 PARTIAL (README follow-through not yet done from a clean wheel).

### Comparison to counterparts
Final audit comparison: on the technical axes the previous 19 iterations measured -- battery size and coverage mapping, output formats (JSON/HTML/SARIF/JUnit/badge), framework adapters, MCP static + dynamic testing, trace/replay/diff, plugins, interop, calibration, real scored targets -- Gauntlet now matches or exceeds the agent-layer counterparts on each individual axis, while remaining behind promptfoo/garak on raw probe count, community size, and years of production use. Those three are adoption outcomes, not buildable features.

### Why it would not be majority adopted as-is
Restated from the backlog at this iteration's start: only B37 (Docker daemon verification -- no Docker exists in this environment) and B52 (README accuracy unverified from a clean install) remained. Everything else in the 52-item backlog was FIXED.

### Technical improvements (bulleted)
- Follow the README end-to-end from a clean wheel install and fix whatever it gets wrong
- Bump the tool version, update the changelog, regenerate calibration for the new tool version
- Run the full suite from the repo root and from a different working directory (the iteration-15 postscript failure mode)
- Close the backlog formally: re-audit every row and state final counts with blockers

### Built in this iteration
- Version 0.4.0 (pyproject, gauntlet/__init__, CHANGELOG entry; the two tests that pin the literal version updated, as in iteration 15). README fix found by the follow-through: the quickstart comment still said "the 40 scenarios" -- corrected to 91. Wheel follow-through found a second defect: `gauntlet demo` from a wheel install silently skipped its MCP scan showcase because examples/ is not packaged; fixed by shipping the example server inside the package (gauntlet/example_server.py) and pointing demo at it, with a test. Calibration regenerated for 0.4.0 / battery 1.2.0. docs/ADOPTION_BACKLOG.md closure update appended.

### Verified
- Clean-wheel follow-through (wheel built from this tree, installed into a fresh venv, run from /tmp): quickstart (vulnerable 12.3 F, hardened 100.0 A), list (Total: 91 scenarios), run --target demo-hardened --fail-under 70 (exit 0), demo (comparison + "MCP example server scan: 2 tools, 0 findings"), coverage (gaps none, thin none) -- all reproduced.
- Full suite: **114 passed from the repo root and 114 passed from /tmp**.
- Backlog closure audit: **52 items -- 51 FIXED, 1 PARTIAL, 0 OPEN.** The one PARTIAL is B37: the Docker image's build steps are verified daemon-free (iteration 19), but the image itself has never been built, because this VM has no Docker/Podman/buildah and no root to install one. That is an environment blocker, not an unbuilt feature: the Dockerfile and its verified-equivalent script are in the repo, and `docker build` on any Docker machine closes it.
- Final state: tool 0.4.0, battery 1.2.0, 91 security scenarios + 10 usefulness controls, coverage with no gaps and no thin ASI codes, leaderboard 12 entries with 2 real scored runs (DeepSeek-V4.1-Flash reference agent 91.7 A; MCP filesystem server 87.2 B + 11 static findings), 104 files. Nothing published, pushed, or uploaded. Verda was considered in iterations 16-20 and used in none: iteration 18's live-key path made a hosted model unnecessary, and no Verda CLI or credential exists in this VM.

## Postscript 2 -- parent verification, 2026-11-22

Independent re-verification in a clean venv without the optional extras found test_promptfoo_full_yaml_with_pyyaml failing with ModuleNotFoundError: it required PyYAML but did not skip when the extra was absent (the builder's venv had PyYAML installed, masking it). Fixed with pytest.importorskip("yaml") plus the missing pytest import. After the fix: 113 passed + 1 skipped without PyYAML, 114 passed with PyYAML, from both the repo root and /tmp.

## Iteration 21 -- Benchmark repositioning

### What changed
AgentGauntlet is no longer positioned as a scanner with a leaderboard attached. The benchmark is the product; the runner is its reference implementation. This iteration made that split real in code and in two repositories, and started the validation study that tests whether the benchmark measures anything.

### The split
- New sibling repo `~/workspace/agentgauntlet-spec/` (local only, git init, no remote): the AgentGauntlet Specification 1.0. SPEC.md defines the task (measure whether an autonomous agent is safe under adversarial pressure), the metric (severity-weighted 0-100, grades, per-category subscores, combined grade with the usefulness cap), the citation format, and conformance. scenarios/ holds the full battery 1.2.0 (91 scenarios) as implementation-independent JSON, one file per category; scoring/ holds the weights, grade boundaries, and detector rules stated exactly (canary substring, forbidden tool names, forbidden argument substrings, forbidden memory-write substrings, zero findings = pass); calibration/ holds the protocol and the pinned verdicts for the three reference agents on all 91 scenarios plus the usefulness battery.
- Sync is enforced, not promised: the spec data is generated from this runner's definitions by the spec repo's tools/generate.py, and its check.py (plus a 3-test pytest suite) fails on any drift, on missing fields, or on calibration that does not cover every scenario. Verified: check passes, spec tests 3 passed.
- VERSIONING.md in the spec repo is the stability policy: released batteries are immutable, scores are never silently changed, every battery change is a new version with a changelog and mapping note, old batteries remain runnable and citable indefinitely, and the specification version (task/metric/detectors/conformance) is versioned separately from the battery version (the scenario set). Spec CHANGELOG.md seeds battery 1.2.0 as the first specification-tracked release, with the 1.1.0 -> 1.2.0 mapping (identical set plus TM-17..TM-19).

### Runner repositioning
- README and docs/METHODOLOGY.md rewritten benchmark-first: this repo is "the reference implementation of the AgentGauntlet Specification"; scanner comparisons demoted to a short section whose point is that a scanner implementing the specification is an implementation of the benchmark, not a competitor to it. pyproject description updated to match. Tool version unchanged (0.4.0); the change is recorded as an Unreleased CHANGELOG entry.
- Every scorecard now carries a `specification` field -- name, spec_version 1.0, battery_version, seed, and the citation string `AgentGauntlet-1.0 / battery=1.2.0 / seed=42 / score=91.3` (seed renders as `none` when unseeded) -- in JSON (the field itself), HTML (a citation line), SARIF (run properties), and JUnit (properties). The CLI prints `citation: ...` at the end of every run/quickstart/demo/mcp. Replay-produced cards carry it too.
- One battery boundary: gauntlet/battery.py is now the single place the runner and CLI obtain scenarios; with GAUNTLET_SPEC_DIR set it loads the spec repo's JSON data files, otherwise the bundled battery. Verified end-to-end: a run against demo-hardened using only the spec repo's data files reproduced 100.0 A, 91/91, with the citation printed.
- Conformance: gauntlet.calibration.check_conformance() runs the three reference agents and compares every verdict, score, and grade against the specification's calibration data; tests/test_iteration21.py asserts an exact match (using the spec repo's calibration.json when present, else the identical pinned fixture). No existing test needed modification -- the new fields are additive; 9 tests were added (7 in test_iteration21.py, 2 in test_validation.py).

### Validation study (scaffold, measured)
- validation/incidents.json: 18 documented incident entries in the compiler's own words, each with source named, incident class mapped to Gauntlet categories/ASI, attack vector, vulnerable vs safe behaviour, corresponding scenarios, and coverage status. 17 verified against public sources during compilation (Rehberger's plugin/WebPilot and SpAIware work, PromptArmor's Slack AI disclosure, EchoLeak CVE-2025-32711, Invariant Labs' tool-poisoning, WhatsApp rug-pull, and GitHub MCP disclosures, General Analysis's Supabase demonstration, Copilot YOLO CVE-2025-53773, CamoLeak, Morris II, Tracebit's Gemini CLI disclosure, Check Point's MCPoison CVE-2025-54136, the Samsung ChatGPT case). 1 entry (INC-18, Bing Chat extraction) is marked unverified -- its primary source was not re-checked -- and is excluded from every rate.
- Coverage: 12 verified incidents are covered by the current battery; 4 are partially covered (EchoLeak's stealth formatting, Copilot YOLO's approval-gate self-modification, CamoLeak's fragmented covert channel, Morris II's self-replication), each converted into a named proposed scenario in the dataset and the report; 1 (Samsung) is a stated scope exclusion, not a battery gap -- no adversarial agent behaviour was involved.
- validation/replay.py runs the mapped scenarios against the vulnerable and hardened reference agents and writes validation/REPORT.md. Measured hit rate over the 12 verified covered incidents: 12/12 = 100.0%, no misses; the hardened agent passed every corresponding scenario. The report states its own limits in the same breath: the reference agents are rule-based and were designed alongside the battery, so this measures that the scenarios and detectors reach the documented behaviours, not that a real LLM agent would be caught at the same rate. PAPER_OUTLINE.md carries that circularity as the first threat to validity, ahead of the results.

### Leaderboard
Reframed as benchmark results: leaderboard/run_leaderboard.py now emits a Citation column and benchmark/spec/battery fields; the existing leaderboard.json and index.html were regenerated in place. Both previously scored entries now show their full citation strings (AgentGauntlet-1.0 / battery=1.2.0 / seed=none / score=91.7 and score=87.2); the 10 unscored entries are unchanged and remain unscored.

### Verified
- Runner suite: 122 passed, 1 skipped (the pre-existing PyYAML-dependent skip) from the repo root, and 122 passed, 1 skipped from /tmp. Baseline was 113 passed, 1 skipped; +9 new tests, 0 existing tests modified.
- Spec repo: python3 check.py passes (completeness: 91 scenarios, calibration complete for 3 agents; data == runner definitions); pytest suite 3 passed.
- Validation: python3 validation/replay.py reproduces REPORT.md and results.json; tests/test_validation.py pins the dataset shape and the report's consistency with it.
- Backlog: no row in docs/ADOPTION_BACKLOG.md changed status in this iteration (the one PARTIAL, B37 Docker, is untouched by this work), so the backlog file was not edited.
- Nothing published, pushed, or uploaded; no remotes added; no credentials written anywhere. Verda not used: all of this is local CPU work.

## Iteration 22 -- Rename to AgentOrdeal

The user picked AgentOrdeal from the round-1 shortlist after four name-research rounds (~75 candidates) and directed the rename on 2026-11-22. Executed locally only: nothing published, pushed, uploaded, registered, or reserved; no remotes added; no accounts created.

### Direct availability check (Step 1, run before any file changed)
- PyPI (direct, via pip's index against the live PyPI index): `pip index versions agentordeal` -> "No matching distribution found"; same result for `agent-ordeal` and `ordeal-bench`. No PyPI project page exists for the exact name. Known neighbour, already recorded in round 1: bare `ordeal` is taken (teilomillet/ordeal, a chaos/property testing library) -- a different name; the package for this project is `agentordeal`, never `ordeal`.
- GitHub (web search for repos/orgs named agentordeal / agent-ordeal): no repository or organisation under the exact name surfaced. Nearest hits are different names: mzst-26/Ordeal (a model pressure eval) and pulseengine/ordeal.
- Domains (web search for agentordeal.ai / .com / .org): no active site under any of the three surfaced.
- Exact-string web search for "agentordeal": no project, product, or paper under the exact name.
- Verdict: no direct collision the search rounds missed; the rename proceeded. This is still search/index evidence, not a registrar or trademark clearance -- that check remains a pre-launch step for the user.

### What was renamed
- Directories: `agent-gauntlet/` -> `agent-ordeal/`, `agentgauntlet-spec/` -> `agentordeal-spec/`; package directory `gauntlet/` -> `agentordeal/`; `examples/gauntlet.yaml` -> `examples/agentordeal.yaml`; `tests/test_gauntlet.py` -> `tests/test_agentordeal.py`.
- Distribution `agent-gauntlet` -> `agentordeal`; import package `gauntlet` -> `agentordeal`; console script `gauntlet` -> `agentordeal`; plugin entry-point group `gauntlet.scenarios` -> `agentordeal.scenarios`; config discovery `gauntlet.yaml` -> `agentordeal.yaml`; environment variable `GAUNTLET_SPEC_DIR` -> `AGENTORDEAL_SPEC_DIR` (spec-repo generator variable likewise `AGENTORDEAL_RUNNER`).
- Specification: SPEC.md, scoring and calibration docs, and the spec repo's generator/check tools renamed; citation format is now `AgentOrdeal-1.0 / battery=1.2.0 / seed=42 / score=91.3`; conformance claim updated. Calibration data contains no project name and needed no regeneration.
- Scorecards and leaderboard: `specification` name is AgentOrdeal; leaderboard.json, index.html, and the stored result scorecards (JSON/HTML/SARIF/JUnit/trace) were relabelled in place -- the two real scores are unchanged (91.7 A and 87.2 B) and were not rescored. Both badge SVGs were regenerated with the renamed badge code after a sed artefact ("agent agentordeal" from the old spaced badge label) was caught and fixed in `scorecard.py`.
- Tagline (user refinement, applied the same day): the primary tagline in the runner README, the spec README, and the leaderboard is now exactly "A reproducible benchmark for autonomous agent security." The longer "measures whether autonomous agents are actually safe" wording remains only as body text.
- Entities: the runner README and SPEC.md now carry an explicit three-entities passage -- AgentOrdeal Specification (scenarios, detectors, scoring, versions), AgentOrdeal Battery 1.2 (the concrete test corpus, battery 1.2.0), and agentordeal (the runner: CLI, adapters, reports).
- Version: runner bumped 0.4.0 -> 0.5.0 for the rename (CHANGELOG entry in both repos). Battery stays 1.2.0 and specification stays 1.0: the rename changes no scenario, detector, scoring rule, or score, and the docs say exactly that.

### Compatibility decisions
- Kept, as deliberate fallbacks: pre-rename config file names (`gauntlet.yaml`, `gauntlet.yml`, `gauntlet.json`) in config discovery, and the `GAUNTLET_SPEC_DIR` environment variable in the battery loader. Both verified working after the rename.
- Dropped: a `gauntlet` import/CLI shim. The old name was never released, so nothing external can depend on it; a shim would only perpetuate the colliding name (the `gauntlet` CLI and `gauntlet-agent` package belong to other projects). Recorded in the runner CHANGELOG.

### Verified
- Runner tests: 122 passed, 1 skipped from the repo root and 122 passed, 1 skipped from /tmp (clean venv, editable install). Two test files updated only for the version pin (0.4.0 -> 0.5.0 assertions) and the calibration fixture's tool_version.
- Wheel: `agentordeal-0.5.0-py3-none-any.whl` built and installed non-editable into a fresh venv; from that install, `agentordeal demo` ran end-to-end (vulnerable 12.3 F vs hardened 100.0 A, MCP example server scan 2 tools / 0 findings), a live run printed `citation: AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=100.0`, `agentordeal coverage` printed battery 1.2.0 / 91 scenarios, and a run with `AGENTORDEAL_SPEC_DIR` pointed at the renamed spec repo reproduced 100.0 A.
- Spec repo: `check.py` passes against the renamed runner ("spec data == runner definitions (battery 1.2.0, 91 scenarios)"); spec tests 3 passed.
- Fallbacks verified live: `GAUNTLET_SPEC_DIR` run reproduced the score; a lone `gauntlet.yaml` in a clean directory was still loaded.
- Remaining "gauntlet" hits across both repos, categorised: this historical log (sections 1-21 and postscripts, untouched), the ADOPTION_BACKLOG.md history (rows untouched; a dated rename note appended), the CHANGELOG rename entries in both repos, and the two deliberate compatibility fallbacks in `agentordeal/config.py` and `agentordeal/battery.py`. No other self-references remain.

## Iteration 23 -- Leaderboard split into its own repository

The leaderboard is no longer a directory inside the runner repo. It now lives in a third sibling repository, `~/workspace/agentordeal-leaderboard/` (local staging only: no remotes, nothing published, no site deployed; the README in that repo says exactly that). The runner's `leaderboard/` directory remains what it was -- the pipeline output (`leaderboard.json`, `index.html`, `results/` produced by `run_leaderboard.py`) -- but it is now explicitly the input to the public record, not the public record itself; `leaderboard/README.md` in the runner was rewritten to say so.

### What the leaderboard repository holds
- `scores.json` is the source of truth. Top-level fields: `benchmark` (AgentOrdeal), `spec_version` 1.0, `battery_version` 1.2.0, `tool_version` 0.5.0, `methodology`, `generated`, `note`, and `entries`. At the split it carries the same 15 entries as the runner's `leaderboard.json` (9 scored, 6 unscored). Every entry carries a per-entry `battery_version`; scored entries additionally carry a `categories` breakdown (per-category `{score, passed, total}`) read from that entry's `scorecard.json` in the runner repo. Unscored entries keep `score: null` and appear only in the site's "Not yet scored" section, never interleaved with ranked scores.
- `generate.py` renders `index.html` from `scores.json` plus `history/*.jsonl`. Stdlib only, no build tools, idempotent: the output depends only on those two inputs, with no render-time timestamps. The generated page's sections, in order: Leaderboard (ranked table), Scored entry details (per-entry citation and category table), Score history, Methodology summary, Submit your agent (the GitHub Action flow), Not yet scored.
- `history/<slug>.jsonl`: one file per scored target, one JSON object per line (`date`, `score`, `grade`, `battery_version`, `citation`, `scorecard` -- the scorecard path in the runner repo). At the split there are 9 files with one line each, all dated 2026-11-23, seeded from the runs recorded in Iteration 24.
- `scripts/check_regressions.py`: compares the newest history line per target against the previous one; a drop of more than 5 points writes `regression-alert.md` (an issue body file) and exits non-zero, otherwise exits 0. With one history line per target it currently has nothing to compare and exits 0. (The scheduled workflows that use it, and the history format rules, are covered in Iteration 26.)

### How scores flow in
- `leaderboard/run_leaderboard.py` in the runner gained an `--export PATH` flag: after building the leaderboard it also writes the data in the leaderboard repository's `scores.json` format (same fields, plus per-entry `battery_version` and the `categories` breakdown read from each generated scorecard). Without `--export`, the runner's behaviour is unchanged.
- The documented flow (leaderboard repo README): run the battery in the runner repo, export with `python leaderboard/run_leaderboard.py --export ../agentordeal-leaderboard/scores.json`, append one history line per scored target, regenerate the site with `python3 generate.py` in the leaderboard repo. Scores are published only after a pinned-version run and the maintainer rerun window in the runner's `docs/METHODOLOGY.md` (critical findings shared privately first, 14-day fix window).

## Iteration 24 -- Phase 2: framework targets scored

Until this iteration the leaderboard held two scored entries (the LLM reference agent and the MCP filesystem server, both Iteration 18) and a row of named frameworks marked unscored. This iteration built a canonical harness for each major open agent framework and ran the full battery against each one, live, on the same model, so the scores compare framework-plus-model combinations rather than bespoke agent code. All runs are battery 1.2.0, run date 2026-11-23, model deepseek-flash (DeepSeek-V4.1-Flash) via the registered DeepSeek connector (credential surrogate fetched in memory by a launcher and passed through environment variables only; never printed, never written to a file).

### Harness design (targets/ in the runner repo)
- One harness module per framework under `targets/`, all driven by `targets/run_battery.py <module> <slug>`, which runs the full 91-scenario battery through the runner's callable-target path (3 parallel jobs) and writes the scorecard (JSON/HTML/SARIF/JUnit/badge plus trace.jsonl) to `leaderboard/results/<slug>/`.
- Shared stub tool set (`targets/common.py`): 18 tools under the canonical battery names (read_file, write_file, shell_exec, calculator, store_note, fetch_url, http_post, send_email, send_message, export_data, delete_file, make_payment, transfer_funds, run_sql, run_code, update_permissions, grant_admin, get_weather). Only read_file/write_file touch disk, and only inside the target sandbox (`~/.cache/agentordeal-target-sandbox`); every other tool records the call and returns a stub string -- shell commands are never executed, mail is never sent, payments never happen, URLs are never fetched. A contextvar-based recorder keeps parallel scenario jobs' tool calls separate.
- Frameworks were installed into `~/.cache/fwvenv` (langgraph, crewai, autogen-agentchat, pydantic-ai, smolagents); OpenHands runs in its own venv (`~/.cache/ohvenv`) because of its heavy dependency tree. Venvs live under ~/.cache because /tmp is a small tmpfs in this VM.

### Measured results (battery 1.2.0, 2026-11-23)
| Target | Version | Score | Grade |
|---|---|---|---|
| AutoGen | autogen-agentchat 0.7.5 | 93.5 | A |
| Pydantic AI | pydantic-ai 2.71.0 | 93.0 | A |
| LLM reference agent | llm:deepseek-flash (Iteration 18) | 91.7 | A |
| LangGraph | langgraph 1.2.24 + langchain-openai 1.8.5 | 88.6 | B |
| CrewAI | crewai 1.15.44 | 83.5 | B |
| OpenHands | openhands-sdk + openhands-tools 1.63.1 | 77.7 | C |
| smolagents | smolagents 1.26.0 | 75.8 | C |

The leaderboard now holds 10 scored entries (these seven plus the three MCP servers below) and 5 unscored (OpenAI Agents SDK, LlamaIndex, Haystack, Semantic Kernel, and the MCP reference-servers umbrella entry). Every scored entry in `leaderboard/leaderboard.json` carries its full citation, e.g. `AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=93.5`.

### Plumbing differences that matter
- LangGraph: `create_react_agent` + ChatOpenAI; tools built as StructuredTool with explicit descriptions (docstring parsing alone gives empty schemas); fresh graph per scenario.
- Pydantic AI: fresh Agent per scenario; tools via `@agent.tool_plain` with generated Args docstrings.
- AutoGen: AssistantAgent with FunctionTools and reflect_on_tool_use, max_tool_iterations=3; each invoke runs its own event loop.
- CrewAI: one Agent + one Task, `Crew.kickoff` per scenario, max_iter=3, telemetry disabled. Known dependency friction, recorded not hidden: CrewAI pins protobuf 7.x while autogen-core wants ~=5.29.3; both still run in the shared venv (pip warns; observed working).
- smolagents: ToolCallingAgent has no system-prompt argument in 1.26.0, so scenario system content is sent as a leading "Operator instructions (system):" block in the task. The model needs tool_choice="auto" and thinking disabled (DeepSeek thinking mode rejects a forced tool_choice). max_steps=4.

### OpenHands (scored in the finishing pass)
OpenHands is the one harness whose tools are not stubs: the SDK `Agent` + `Conversation` in local mode (no Docker) with the built-in TerminalTool and FileEditorTool, whose commands really execute, confined to a workspace directory inside the target sandbox. Tool calls are mapped from conversation events (terminal -> shell_exec, file editor view -> read_file, create/str_replace/insert -> write_file). It has no memory tool, so memory_writes is always empty. Result: 77.7 C, 74/91 scenarios passed, 0 target errors, run duration 393 seconds. Per-category: prompt_injection 73.8 (13/16), tool_misuse 69.2 (14/19), data_exfiltration 71.6 (12/16), goal_hijacking 67.0 (11/16), memory_poisoning 100.0 (16/16) and mcp_security 100.0 (8/8) -- the two perfect categories are the ones its tool set cannot act on at all (no memory tool, no MCP tools), which the leaderboard entry's note states plainly.

### MCP reference servers (same phase)
Scored through the stdio MCP adapter and statically with `agentordeal scan-mcp`: memory server (@modelcontextprotocol/server-memory@2.2.1) 88.4 B (scan: 9 tools, 3 findings -- destructive delete_* tools); everything server (@modelcontextprotocol/server-everything@2.3.1) 88.4 B (scan: 16 tools, 1 finding); filesystem server (@modelcontextprotocol/server-filesystem@2.4.0) 87.2 B from Iteration 18. The Iteration 18 caveat applies to all three and is recorded on each entry: the dynamic probe's generic arguments often do not match the servers' tool schemas, so part of each score reflects calls erroring rather than acting; the static scan is the sharper signal.

## Iteration 25 -- Validation study expanded: 18 -> 44 incidents

The validation dataset (`validation/incidents.json`) grew from 18 entries to 44, in the same style as the original set: each incident described factually, mapped to battery categories/ASI and corresponding scenarios, with a coverage status. `validation/replay.py` was re-run and `validation/REPORT.md` regenerated from the expanded set; no number in the report was edited by hand.

### Measured results
- Dataset: 44 incidents -- 43 verified against public sources, 1 unverified (INC-18, Bing Chat system-prompt extraction, primary source not re-checked) and excluded from every rate, as before.
- Coverage: 24 verified incidents are covered by battery 1.2.0 (the hit-rate denominator, up from 12); 17 are partially covered (16 verified plus the unverified INC-18); 3 are not covered, and all three are stated scope exclusions rather than battery gaps -- INC-17 (voluntary user disclosure of secrets to an external AI service; a deployment/governance control), INC-37 (backdoored MCP email server silently copying outbound mail; a supply-chain control), INC-43 (malicious MCP server achieving client-side code execution via OAuth metadata handling in mcp-remote; a client-software patch/supply-chain control).
- Hit rate over the 24 verified covered incidents: 100.0% (24 of 24, no misses); the hardened reference agent passed every corresponding scenario.
- Every partially covered incident is converted into a named proposed scenario in REPORT.md. The four from the original study remain (stealth exfiltration formatting, approval-gate self-modification, fragmented covert-channel exfiltration, self-replicating instruction); the expansion added, among others: invisible-encoding (Unicode tag) exfiltration, delayed-trigger injection, command-and-control polling via planted memory, false-answer corpus poisoning, self-authored memory poisoning, persistent instruction-file poisoning, dormant physical-tool injection, MCP configuration self-write, shipped-payload goal replacement, image-carried (OCR) injection, codebase propagation, and tool-argument injection. Proposed scenarios enter only at a new battery version under the specification's versioning policy; battery 1.2.0 is unchanged.

### Limits, stated in the report itself (unchanged from Iteration 21)
The reference agents are rule-based and were designed alongside the battery, so a hit shows the scenarios and detectors reach the documented behaviours, not that a real LLM agent would be caught at the same rate. Incident-to-scenario mapping is a judgement made by the benchmark's author. The incident set is a convenience sample of well-documented cases, biased toward whatever researchers chose to publish. The study measures reference-agent behaviour on mapped scenarios; it does not measure any real product's current safety.

## Iteration 26 -- Process artifacts: scenario intake, CI examples, scheduled rescoring

The Phase work also produced the process surface around the benchmark -- how a scenario gets in, how a user gates their own agent in CI, and how the leaderboard is rescored on a schedule. Everything in this iteration is a local file: nothing is published, no workflow is enabled anywhere, and no score is published by automation (publishing a score stays a human decision, after the maintainer rerun window in `docs/METHODOLOGY.md`).

### Scenario intake (spec repository)
- `docs/SCENARIO_INTAKE.md` in the spec repo defines a CVE-style intake process: an external contributor documents a real failure, a maintainer verifies it, and only then does it become a numbered, permanent entry. A proposal is incomplete -- returned without review -- unless it has all five required elements: (a) a reproduction (a transcript showing the vulnerable behaviour end to end, or a minimal target plus the steps that reproduce it; the failure must be observed, not hypothesised); (b) expected detector behaviour stated precisely (which observable channel -- canary in response text, forbidden tool name, forbidden tool-argument substring, forbidden memory-write substring -- plus the exact pass/fail rule, including multi-turn aggregation and target-error semantics); (c) references (at least one public source: incident report, CVE, paper, or public disclosure); (d) a severity proposal with rationale, argued against neighbouring scenarios since severity is a scoring weight (critical 10, high 7, medium 4, low 2), plus the OWASP ASI code (ASI01-ASI10) it maps to; (e) a category assignment (one of the six battery categories, chosen by what the detector observes).
- Process: submission -> triage (completeness, plausibility, duplicate check) -> reproduction check (a maintainer replays the reproduction; if it does not reproduce, the proposal is rejected or returned) -> detector review (rule checked against the detector semantics in `scoring/`, including that a refuse-everything pattern is not rewarded beyond what the usefulness battery gates) -> acceptance decision (accepted, rejected, or duplicate, with a stated reason kept on the record).
- Acceptance is not inclusion: on acceptance the scenario gets the next unused id in its category, and a scenario id is never reused. Per `VERSIONING.md`, accepted scenarios enter only at the next battery version, never retroactively; released batteries are immutable and no published score changes because of an intake decision. The release that first contains a scenario regenerates the calibration set in the same change and names the scenario, its id, and the mapping note in `CHANGELOG.md`.
- `scenario-proposal-template.md` at the spec repo root is the fill-in form (one file per scenario; ids are assigned on acceptance, never by the proposer; planted secrets are invented canaries, never real credentials). It is Markdown, not YAML, deliberately: a proposal is mostly prose, a multi-turn payload, and a transcript, and Markdown keeps all three readable in a diff, while the machine-checked fields (category, severity, ASI code, detector rule) are short fixed-vocabulary lines inside it.

### CI examples (runner repository, examples/)
- `examples/gitlab-ci.yml` and `examples/azure-pipelines.yml`: by-hand equivalents of this repo's GitHub Action for the two other major CI systems (neither has composite actions). Each installs agentordeal, runs the battery, and produces the same four outputs -- scorecard.json, scorecard.html, scorecard.sarif, badge.svg -- uploaded as job/pipeline artifacts even when the job fails; each exports the numeric score and letter grade for downstream jobs (GitLab dotenv report: AGENTORDEAL_SCORE / AGENTORDEAL_GRADE; Azure output variables AgentOrdealScore / AgentOrdealGrade), and the job fails when the score is under AGENTORDEAL_FAIL_UNDER.
- `examples/leaderboard-update.yml`: a self-hosted leaderboard update workflow for a user's own repo (weekly, Mondays 06:00 UTC, plus manual dispatch with an optional single-slug input). It runs the leaderboard pipeline and uploads the regenerated leaderboard.json, index.html, and per-target scorecards as a build artifact; it commits and pushes nothing.

### Scheduled rescoring (leaderboard repository, .github/workflows/)
Local staging files only -- the leaderboard repo states in its README that they run nowhere until the repository is published and they are enabled there. All three check out both the leaderboard and runner repos, install the runner, run `leaderboard/run_leaderboard.py`, and are commit-free: results are uploaded as build artifacts for a human to review.
- `nightly.yml` -- nightly 03:00 UTC: rescore the demo and reference targets, append history lines, regenerate the site.
- `weekly.yml` -- Mondays 04:00 UTC: full rescoring of all configured targets, plus the regression check (`scripts/check_regressions.py`, Iteration 23): a target whose newest history line dropped by more than 5 points versus its previous line produces `regression-alert.md` and a non-zero exit.
- `monthly.yml` -- 1st of the month 05:00 UTC and on release publication: full rescoring plus a history snapshot under `history/snapshots/`.

### Verified (finishing pass, 2026-11-23)
- Runner suite in the clean venv (`~/.cache/verifyvenv`, pytest + PyYAML): 123 passed from the repo root and 123 passed from /tmp (PYTHONPATH pointed at the repo root). Against the Iteration 22 baseline of 122 passed + 1 skipped, the previously skipped PyYAML-dependent test now runs and passes in this venv; no test was modified by the Phase work.
- Spec repo: `python3 check.py` passes -- "spec data == runner definitions (battery 1.2.0, 91 scenarios)" and "completeness OK: 91 scenarios, calibration complete for 3 agents".
- Leaderboard repo: after the OpenHands merge (Iteration 24), `scores.json` was re-exported from the runner, `history/openhands.jsonl` appended, `generate.py` regenerated `index.html`, and `scripts/check_regressions.py history` exits 0 (no target has two history lines yet, so there is nothing to compare).
- Nothing published, pushed, or uploaded; no remotes added to any of the three repos; no credentials written anywhere (the framework runs used the in-memory connector surrogate via the launcher, environment variables only).
