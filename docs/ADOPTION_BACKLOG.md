# Adoption backlog -- extracted from ADOPTION_ITERATIONS.md iterations 1-15

Step 0 of the iterations 16-20 run (2026-11-22). Every distinct item in the 15
"Why it would not be majority adopted as-is" sections, audited against the
current code (not the log's claims), plus three items from the Step-0 code
audit itself. Statuses are updated at the end of each iteration 16-20 with
the verifying test or command.

| ID | Source | Item | Status at audit | Evidence / verification |
|---|---|---|---|---|
| B01 | It.1 | No config file to check into a repo and rerun identically | FIXED | It.1: gauntlet/config.py + --config; tests/test_iteration1.py |
| B02 | It.1 | All-or-nothing runs: no category/severity/scenario selection | FIXED | It.1: filter_scenarios + --category/--severity/--scenario; test_iteration1 |
| B03 | It.1 | Sequential runner too slow for network targets | FIXED | It.1: --jobs parallel runner; test_iteration1 |
| B04 | It.1 | CLI-flag-only config does not survive team handover | FIXED | It.1: gauntlet.yaml/JSON config, CLI-over-config precedence; test_iteration1 |
| B05 | It.2 | Findings cannot enter GitHub Code Scanning (no SARIF) | FIXED | It.2: SARIF 2.1.0 output; test_iteration2 |
| B06 | It.2 | CI systems speak JUnit XML; results invisible in dashboards | FIXED | It.2: JUnit XML output; test_iteration2 |
| B07 | It.2 | Every adopter would have to write the same format converter | FIXED | It.2: repeatable --format json/html/sarif/junit; test_iteration2 |
| B08 | It.3 | No badge: no passive discovery from other projects' READMEs | FIXED | It.3: SVG badge + gauntlet badge; test_iteration3 |
| B09 | It.3 | A score that cannot be displayed cannot become a status symbol | FIXED | It.3: badge_markdown snippet; test_iteration3 |
| B10 | It.3 | Maintainers get no reputational return for running the tool | PARTIAL | Badge exists; reputational loop needs a leaderboard with real scores -- see B32/B51 |
| B11 | It.4 | Each framework community must hand-write its own shim | FIXED | It.4: adapters/frameworks.py, 4 optional extras; test_iteration4 |
| B12 | It.4 | No named adapters: invisible in framework docs/examples | FIXED | It.4: docs/ADAPTERS.md + named extras; test_iteration4 |
| B13 | It.4 | Hand-rolled glue makes results incomparable across projects | FIXED | It.4: one target protocol, base.normalize_response; test_iteration4 |
| B14 | It.5 | 40 obvious prompts prove little; battery too easy to pass | FIXED | It.5: battery expanded to 88; test_iteration5 |
| B15 | It.5 | No MCP-specific scenarios (poisoned descriptions, rug-pulls, look-alikes) | FIXED | It.5: mcp_security MCP-01..08; test_iteration5 |
| B16 | It.5 | No encoded or multi-turn attacks | FIXED | It.5: base64/document payloads + turns in runner; test_iteration5 |
| B17 | It.6 | Refuse-everything agent earns a perfect score | FIXED | It.6: usefulness battery + combined_grade cap; refuse-all = combined D |
| B18 | It.6 | README badge meaningless if a broken bot earns the same badge | FIXED | It.6: combined grade rule in METHODOLOGY; test_iteration6 |
| B19 | It.6 | Leaderboard would rank broken agents at the top | FIXED | It.6: run_full records usefulness + combined_grade; test_iteration6 |
| B20 | It.7 | MCP server authors get nothing until they also have an agent | FIXED | It.7: gauntlet scan-mcp; test_iteration7 |
| B21 | It.7 | No low-friction first run (no agent, no key, one command) | FIXED | It.7: scan-mcp needs only a server command; test_iteration7 |
| B22 | It.7 | Risky tool descriptions forced a dynamic run to find | FIXED | It.7: static checks in gauntlet/mcp_scan.py; test_iteration7 |
| B23 | It.8 | No trace: no audit evidence of what the agent did | FIXED | It.8: trace.jsonl on every run; test_iteration8 |
| B24 | It.8 | Score disputes cannot be settled from a record | FIXED | It.8: gauntlet replay reproduces scores offline; test_iteration8 |
| B25 | It.8 | Regression comparison across versions is manual | FIXED | It.8 replay + It.15 diff; test_iteration8/15 |
| B26 | It.9 | Closed battery gets forked/abandoned; no community scenarios | FIXED | It.9: plugin system --plugin-dir + entry points; test_iteration9 |
| B27 | It.9 | Security teams cannot encode an internal incident as a scenario | FIXED | It.9: plugin schema + examples/my_plugin.py; test_iteration9 |
| B28 | It.9 | No contributor path in; single maintainer is the bottleneck | FIXED | It.9 plugins + It.12 CONTRIBUTING/templates; test_iteration9 |
| B29 | It.10 | Sync-only harness excludes async agents | FIXED | It.10: coroutine targets via asyncio; test_iteration10 |
| B30 | It.10 | One hung/flaky call fails the whole CI run | FIXED | It.10: --timeout/--retries, failures recorded; test_iteration10 |
| B31 | It.10 | Undocumented exit codes and thin metadata read as a hobby project | FIXED | It.10: exit codes 0/1/2 documented, classifiers, CHANGELOG; test_iteration10 |
| B32 | It.11 | Leaderboard has no pipeline; hand-edited JSON, no defensible score | PARTIAL | It.11: run_leaderboard.py regenerates from scorecards only -- but no entry ever scored by a real run; see B51 |
| B33 | It.11 | No LLM-backed target; users must write an HTTP wrapper first | FIXED | It.11: adapters/llm.py llm:<model>, key from env; test_iteration11 (fake server) |
| B34 | It.11 | No version pinning in leaderboard entries | FIXED | It.11: target spec, pinned version, tool version, run date recorded; test_iteration11 |
| B35 | It.11 | Scores not regenerable from artifacts | FIXED | It.11: pipeline rebuilds leaderboard.json/index.html from scorecards; test_iteration11 |
| B36 | It.12 | Unverified packaging path may silently run an empty battery | FIXED | It.12/15: wheel clean-venv install reproduces 88 scenarios + quickstart; test_iteration12 |
| B37 | It.12 | No Docker image for enterprise/CI users | PARTIAL | It.12: Dockerfile written, statically validated; image build never run (no docker in VM) |
| B38 | It.12 | Action exposes no outputs; cannot gate PRs without shell scraping | FIXED | It.12: action.yml score/grade/scorecard-path outputs; test_iteration12 |
| B39 | It.12 | No SECURITY.md / issue templates; fails security-team review | FIXED | It.12: SECURITY.md, CONTRIBUTING.md, 3 issue templates, pre-commit |
| B40 | It.13 | Switching cost is total: promptfoo/garak work must be thrown away | PARTIAL | It.13: importer covers a stdlib YAML subset; full YAML and judged assertions reported unconverted; test_iteration13 |
| B41 | It.13 | No export path into existing dashboards/reporting | FIXED | It.13: export-promptfoo v3 results JSON; test_iteration13 |
| B42 | It.13 | No garak probe-family name mapping | FIXED | It.13: 13-family mapping, dotted sub-probes, unknowns reported; test_iteration13 |
| B43 | It.14 | Unmapped battery cannot face compliance review; thin spots invisible | PARTIAL | It.14: coverage maps ASI+ATLAS live, but ASI05 = 1 scenario (thin) at audit time |
| B44 | It.14 | No battery version: scores from different months incomparable | FIXED | It.14: BATTERY_VERSION 1.1.0 on every scorecard; docs/BATTERY.md |
| B45 | It.14 | No calibration set: score disputes are arguments, not diffs | FIXED | It.14: calibration.py + fixtures/calibration.json asserted exactly; test_iteration14 |
| B46 | It.15 | No diff: no regression workflow for CI gating | FIXED | It.15: gauntlet diff + --fail-on-regression; test_iteration15 |
| B47 | It.15 | No per-run metadata: scores cannot be audited or reproduced | FIXED | It.15: metadata in JSON/HTML/SARIF/JUnit; test_iteration15 |
| B48 | It.15 | One-attempt HTTP calls flaky against rate-limited endpoints | FIXED | It.15: 429/5xx backoff with Retry-After; test_iteration15 |
| B49 | It.15 | Leaderboard pipeline only runs on the maintainer's machine | FIXED | It.15: examples/leaderboard-update.yml + docs/LEADERBOARD_OPS.md |
| B50 | audit | Bundled examples/mcp_server.py is a print stub, not a server; the stdio MCP client returns 0 tools for it; no end-to-end MCP test against the bundled example | OPEN | Step-0 code audit: examples/mcp_server.py contains only a print statement |
| B51 | audit | Real-target pipeline never verified against a live endpoint or a real MCP server; only a local fake OpenAI-compatible server | OPEN | It.11/15 log states this plainly; leaderboard.json checked Step 0: 10 entries, all unscored |
| B52 | audit | No one-command demo; README quickstart never followed end-to-end from a clean wheel install by the auditor | OPEN | No demo command in cli.py (Step-0 audit); README promises a 60-second quickstart |

Audit totals at extraction: 52 items -- 44 FIXED, 5 PARTIAL, 3 OPEN.
Open queue for iterations 16-20: B10 (partial, reputational loop), B32 (partial, pipeline without real scores), B37 (partial, Docker), B40 (partial, promptfoo subset), B44 (partial, ASI05 thin), B50, B51, B52 (open).

## Closure update -- end of iteration 20 (2026-11-22)

Every row re-audited against the code and the runs below.

- B10 (It.3, reputational return): FIXED in iteration 18 -- the leaderboard now carries real, dated, version-pinned scores a maintainer can display and dispute mechanically; the remaining step (publishing it) is external, not technical.
- B32 (It.11, pipeline without scores): FIXED in iteration 18 -- run_leaderboard.py produced the first real scores (see B51).
- B37 (It.12, Docker image): PARTIAL -- build steps verified daemon-free by scripts/verify_docker_equivalent.sh (iteration 19: clean copy, pip install, entrypoint, quickstart all pass). Still unverified: the python:3.12-slim base image and daemon behaviour. External blocker: no Docker/Podman/buildah exists in this VM and none can be installed without root; a real `docker build` needs a machine with Docker.
- B40 (It.13, promptfoo subset): FIXED in iteration 19 -- full YAML via the optional PyYAML extra (`agent-gauntlet[promptfoo]`), subset fallback retained, per-type unconverted guidance; model-graded assertions remain unconvertible by design (deterministic verdicts) and now say exactly how to keep the check (canary or plugin detector).
- B44 (It.14, ASI05 thin): FIXED in iteration 17 -- ASI05 1 -> 4 scenarios, battery 1.2.0, `gauntlet coverage` reports no gaps and no thin codes; calibration regenerated.
- B50 (audit, MCP example stub): FIXED in iteration 16 -- examples/mcp_server.py is a real MCP server; the stdio client was fixed (id-matched, notification-tolerant reads); end-to-end `gauntlet mcp` run and tests prove it. A packaged copy (gauntlet/example_server.py) keeps `gauntlet demo` complete from a wheel install (iteration 20).
- B51 (audit, real-target verification): FIXED in iteration 18 -- live runs only. Option (a) attempted first: an Anthropic key exists via the registered connector but the account's credit balance is too low (API returns a billing error), so it could not run. Option (a) via a second registered provider succeeded: the LLM reference agent ran the full battery against the live DeepSeek API, model deepseek-flash (DeepSeek-V4.1-Flash): **91.7, grade A, 84/91, battery 1.2.0**. Option (c) also ran: the official MCP filesystem server (@modelcontextprotocol/server-filesystem@2.4.0, npm) scored **87.2, grade B, 82/91** dynamically and produced **11 findings** under scan-mcp (16 tools). Option (b) Verda was not used: no Verda CLI or credential exists in this VM, and a live key from option (a) made it unnecessary. Caveat recorded: the filesystem server's dynamic score is high partly because the probe's generic arguments do not match its tool schemas, so most calls error instead of acting; its static scan is the sharper signal for that server.
- B52 (audit, demo/README): FIXED in iterations 16+20 -- `gauntlet demo` added; README followed end-to-end from a clean 0.4.0 wheel install (quickstart, list, run --fail-under, demo, coverage all reproduced; one stale README line, "the 40 scenarios", corrected to 91).

Final totals: 52 items -- 51 FIXED, 1 PARTIAL (B37, Docker daemon verification, external blocker above), 0 OPEN.

## Note -- 2026-11-22: rename to AgentOrdeal

The project was renamed from AgentGauntlet to AgentOrdeal (runner iteration 22) before its first public release, after a direct PyPI/GitHub/domain check on the exact name found no collision. Directories, package, CLI, citation format, and docs were renamed; battery 1.2.0, specification 1.0, and all scores are unchanged. This note is appended for the record; no backlog row above was edited.
