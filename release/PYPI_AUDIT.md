# PyPI readiness audit -- agentordeal 0.5.0

Date prepared: 2026-11-22 (America/Los_Angeles)
Status: preparation only. Nothing was uploaded.

## Name availability

- Project name: agentordeal
- Last checked: 2026-11-22. At that check the name agentordeal was free on PyPI, and there was no GitHub repository or organization under that exact name before the user claimed saloni-garg/agentordeal.
- Note recorded at that check: the bare name ordeal on PyPI is a different package (a chaos testing library). The distribution must always be agentordeal, never ordeal.
- This audit does not re-check live PyPI and does not upload anything. Re-check the name once on release day before the first upload, in the runbook.

## Artifacts built for this audit

- release/dist/agentordeal-0.5.0-py3-none-any.whl -- 58710 bytes
- release/dist/agentordeal-0.5.0.tar.gz -- 415156 bytes
- Built with python -m build in a build venv under ~/.cache/buildvenv.
- twine check result: both artifacts PASSED.
  - Checking release/dist/agentordeal-0.5.0-py3-none-any.whl: PASSED
  - Checking release/dist/agentordeal-0.5.0.tar.gz: PASSED

## Wheel install verification

Fresh clean venv under ~/.cache/cleanvenv, wheel installed from the local file only.

- agentordeal --help: exit 0. Output lists the subcommands list, import-promptfoo, export-promptfoo, coverage, diff, replay, scan-mcp, badge, quickstart, demo, run, mcp, and describes the package as the reference implementation of the AgentOrdeal Specification.
- agentordeal demo --out /tmp/agentordeal-demo-out: exit 0.
  - demo-vulnerable: grade F, score 12.3 / 100, passed 14 / 91. Citation: AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=12.3
  - demo-hardened: grade A, score 100.0 / 100, passed 91 / 91. Citation: AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=100.0
- agentordeal quickstart --out /tmp/agentordeal-qs-out: same two scores and citations, scorecards written.
- Test suite against the installed package: pytest and PyYAML were installed into the same clean venv, then the repository test suite was run from /tmp so imports resolved to the installed wheel, not the source tree. Result: 123 passed.

## Metadata present in the built wheel

From agentordeal-0.5.0.dist-info/METADATA:

- Metadata-Version: 2.4
- Name: agentordeal
- Version: 0.5.0
- Summary: Reference implementation of the AgentOrdeal Specification -- the benchmark that measures whether autonomous agents are actually safe
- Author: Saloni Garg
- License-Expression: MIT
- License-File: LICENSE
- Requires-Python: >=3.10
- Description-Content-Type: text/markdown, body is the full README.md, so the PyPI project page renders the README as the long description.
- Keywords: ai-agents, agent-security, benchmark, mcp, security, prompt-injection, red-teaming, evaluation, llm, autonomous-agents
- Classifiers: Python 3, 3.10, 3.11, 3.12; Topic Security; Topic Scientific/Engineering Artificial Intelligence; Development Status 4 Beta; Intended Audience Developers; Intended Audience Science/Research; Environment Console; Operating System OS Independent.
- Project URLs:
  - Homepage: https://github.com/saloni-garg/agentordeal
  - Repository: https://github.com/saloni-garg/agentordeal
  - Specification: https://github.com/saloni-garg/agentordeal-spec
  - Leaderboard: https://github.com/saloni-garg/agentordeal-leaderboard
  - Issues: https://github.com/saloni-garg/agentordeal/issues
  - Changelog: https://github.com/saloni-garg/agentordeal/blob/main/CHANGELOG.md
- Entry point: agentordeal = agentordeal.cli:main
- Core dependencies: none. The package is stdlib only at runtime.
- Optional extras: dev (pytest), langgraph, openai-agents, crewai, pydantic-ai, promptfoo (PyYAML).

## Fixes applied in this preparation pass

Applied to pyproject.toml in the runner repo, then the artifacts were rebuilt and rechecked above. The test suite passed against the rebuilt wheel.

1. Homepage URL corrected. It pointed at https://github.com/saloni-garg/agent-ordeal, which is not the claimed repository. It now points at https://github.com/saloni-garg/agentordeal.
2. Project URLs expanded. Only Homepage existed. Repository, Specification, Leaderboard, Issues, and Changelog were added, pointing at the runner repo and the two sibling repos.
3. Keywords expanded from 6 to 10, adding agent-security, benchmark, llm, and autonomous-agents.
4. Classifiers expanded, adding Topic Scientific/Engineering Artificial Intelligence, Intended Audience Science/Research, Environment Console, and Operating System OS Independent.
5. License modernized. The build warned that project.license as a TOML table is deprecated and that license classifiers are deprecated. Changed to the SPDX string form license = "MIT", removed the License classifier, and raised the build requirement to setuptools>=77 so the SPDX form is supported. The wheel now carries License-Expression: MIT and the build emits no license deprecation warning.

## Gaps and notes, not blockers

- Placeholder badges in the README. The top of README.md still shows CI placeholder and PyPI placeholder shields. They render, so twine check passes, but they should be replaced with the real workflow and PyPI badges after the first publish. Listed in the runbook as a post-publish edit, not a pre-publish blocker.
- Placeholder Action reference in the README. The GitHub Action example still reads saloni-garg/agent-ordeal@v0.1.0 and says placeholder until published. Update it to the published repository name and tag as part of the release day edits in the runbook.
- No author email or maintainer field is set. That is a deliberate choice, not an oversight: PyPI does not require it and no email needs to be published for the release to work. Add one only if the user wants a public contact.
- Development Status is 4 Beta. That matches a first public release at 0.5.0. Move to 5 Production/Stable only when the user decides the runner, as distinct from the specification, is stable.
- The sdist is larger than the wheel (415156 bytes against 58710 bytes) because MANIFEST.in includes docs, leaderboard data, examples, and the GitHub templates. That is intended: the sdist is the complete source record.

## Verdict

Metadata is complete for a first PyPI page: name, version, summary, rendered README long description, MIT license in SPDX form, author, keywords, classifiers, six project URLs, entry point, and declared extras are all present in the built artifacts, and both artifacts pass twine check.
