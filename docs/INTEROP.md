# Interop: migrating from promptfoo and garak

Ordeal does not ask you to throw away an existing red-team suite.
This page is the migration path in both directions.

## From promptfoo

```bash
agentordeal import-promptfoo promptfooconfig.yaml --out imported-scenarios.json
agentordeal run --target <your-target> --extra-scenarios imported-scenarios.json
```

The importer reads a promptfoo config in YAML (a stdlib subset parser;
JSON configs are read natively), substitutes each test's `vars` into
the first prompt template, and converts assertions:

| promptfoo assertion | Ordeal conversion |
|---|---|
| `not-contains`, `not-contain-all`, `not-contains-any` | `forbidden_text` detector on the response |
| `not-regex` / `not-matches` with a literal value | `forbidden_text` detector |
| `not-regex` / `not-matches` with a real regex | **unconverted** -- reported with a reason; rewrite it as a canary string |
| `contains` / `icontains` | **unconverted** -- a positive-content expectation; it belongs in the usefulness battery (`agentordeal run --usefulness`), not the security battery |
| `llm-rubric` and other model-graded assertions | **unconverted** -- Ordeal verdicts are deterministic by design; there is no LLM-judge equivalent |

Unconverted assertions are printed by name with the reason. Nothing is
silently dropped. Imported scenarios get ids `IMP-01`, `IMP-02`, ...,
category `prompt_injection`, severity `medium`; re-categorise and
re-weight them in the JSON file before a scored run if they matter.

## From garak

garak probes are families, not single tests, so the mapping is by
category. Dotted sub-probes resolve to their family
(`promptinject.HijackHateHumans` -> `promptinject`).

```bash
agentordeal list --garak promptinject,dan,encoding
agentordeal run --target <your-target> --garak promptinject,leakreplay
```

| garak probe | Ordeal categories |
|---|---|
| promptinject, dan, atkgen | prompt_injection |
| encoding | prompt_injection, data_exfiltration |
| leakreplay, leakage | data_exfiltration |
| knownbadsignatures, malwaregen, xss | tool_misuse |
| continuation, misleading, topic | goal_hijacking |
| agent_breaker | tool_misuse, goal_hijacking, mcp_security |

Unknown probe names are reported on stderr, never ignored. The full
mapping is `GARAK_MAP` in `agentordeal/interop.py`. Note the difference in
kind: garak probes a *model's* replies; the Ordeal scenarios they map
to test the *agent system* (tool calls, memory writes, canary leaks),
so a mapped run is a superset in surface, not a re-run of garak.

## Back to promptfoo

```bash
agentordeal export-promptfoo out/scorecard.json --out promptfoo-results.json
```

Produces promptfoo's results-JSON shape (version 3 envelope):
`results.results[]` rows with `success`, `score`, and
`gradingResult.componentResults` (one component per scenario, with the
detector's reasons), plus `results.stats.successes/failures`. CI
tooling that already parses promptfoo output can read it. The original
scorecard's score and grade ride along under the top-level `agentordeal`
key.

## Update (iteration 19): full YAML via optional extra

Installing `agentordeal[promptfoo]` adds PyYAML; the importer then parses full YAML (anchors, merge keys, complex nesting) and falls back to the stdlib subset parser without it. Unconverted assertions now carry per-type guidance (model-graded, performance, provider-specific) instead of one generic reason. The Docker image build steps are verified without a daemon by `scripts/verify_docker_equivalent.sh`; the base image and daemon behaviour remain unverified until a machine with Docker runs `docker build`.
