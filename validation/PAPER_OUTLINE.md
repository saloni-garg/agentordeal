# Paper outline -- AgentOrdeal: a benchmark for agent safety

Working title: **AgentOrdeal: A Versioned, Deterministic Benchmark
for the Safety of Autonomous Agents**

## 1. The question

Do we have a measurement for whether an autonomous agent is safe that
is (a) about the agent system -- its tool calls, memory, and trusted
content -- rather than the base model's text, (b) deterministic and
reproducible enough to cite the way systems benchmarks are cited, and
(c) predictive of the failures that have actually happened in the
field?

## 2. The artifact

- The AgentOrdeal Specification 1.0: task definition, battery,
  severity-weighted deterministic metric, combined grade with a
  usefulness gate, citation format, conformance by calibration.
- Battery 1.2.0: 91 scenarios, six categories, OWASP ASI mapping,
  canary-based detectors over observed behaviour (text, tool calls,
  memory writes). No LLM judge anywhere in the pipeline.
- The reference implementation, plus the conformance protocol that
  lets independent implementations prove equivalence.

## 3. Method

1. **Battery construction.** Scenario classes derived from the OWASP
   Agentic Top 10 and from the documented incident record (section 4),
   not invented in the abstract.
2. **Calibration.** Three deterministic reference agents with pinned
   verdicts on every scenario; any conforming implementation must
   reproduce them exactly.
3. **Incident validation.** A dataset of documented real-world
   agent-security incidents (validation/incidents.json), each mapped
   to the scenarios exercising the same failure, replayed against the
   reference agents (validation/replay.py). Pre-registered rule: the
   hit rate is computed over verified, fully covered incidents only;
   partially covered incidents become proposed scenarios, never
   silent denominator edits.
4. **Live targets.** The leaderboard pipeline run against real,
   runnable agents and MCP servers, reported with full citation
   strings; targets that cannot run stay unscored.

## 4. Results (table shapes)

- Table 1: battery composition by category x severity, ASI coverage.
- Table 2: calibration -- reference agents' scores and the verdict
  agreement a conforming implementation must achieve (100%).
- Table 3: incident validation -- per-incident hit/miss against the
  mapped scenarios (current scaffold result: 12 of 12 verified covered
  incidents caught, 100.0%, against rule-based reference agents; the
  paper must re-run this against LLM-backed agents before claiming
  anything stronger -- see threats).
- Table 4: live-target results with citation strings, battery pinned.

## 5. Threats to validity (written before the results, kept)

- **Reference-agent circularity.** The rule-based vulnerable agent and
  the battery were designed by the same author; a 100% hit rate
  against it is close to a tautology and proves reachability of the
  scenarios, not field validity. The load-bearing version of the
  experiment uses LLM-backed agents the author does not control.
- **Mapping judgement.** Incident-to-scenario mapping is the author's;
  an independent rater should re-map blind and disagreements reported.
- **Selection bias.** Documented incidents are a convenience sample of
  what researchers published, skewed to 2023-2025, English-language,
  and toward products with public disclosure cultures.
- **Historical targets.** The products in the incidents have changed
  or been patched; the study validates the benchmark against failure
  *classes*, and claims nothing about any product's current state.
- **Deterministic detectors.** Substring/tool-name rules can be
  gamed by a target that knows the battery, and can miss novel
  encodings; the versioning policy (immutable batteries, public
  changelogs) makes gaming visible but does not prevent it.
- **Usefulness gate calibration.** The combined-grade caps (50/80)
  are chosen, not derived; sensitivity to those thresholds should be
  reported.

## 6. Adoption and citation reporting

Report, factually and with dates: independent implementations and
their conformance status; papers and benchmarks that report
AgentOrdeal scores or reuse the battery; leaderboard submissions by
third-party maintainers; CI integrations. Each claim sourced (a link,
a release, a proceedings page) -- adoption is reported the same way
scores are: pinned, dated, and reproducible, or not reported.

## 7. Related work positioning

garak (model scanning), promptfoo (prompt/output evaluation), PyRIT
(red-team campaigns), AgentDojo and OSWorld-style agent benchmarks:
AgentOrdeal's claim is narrower and different -- a *standard
measurement* for agent safety with a stability policy, where those
systems are tools or task benchmarks. The paper should say plainly
that a scanner implementing the specification is a contribution to
the benchmark, not a competitor to it.
