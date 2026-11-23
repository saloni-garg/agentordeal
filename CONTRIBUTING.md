# Contributing to AgentOrdeal

The core package is **standard-library only** on purpose: `pip install
agent-ordeal` must never pull a dependency tree. Framework adapters
live behind optional extras and must import lazily and fail with a
message naming the extra to install.

## Dev setup

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[dev]"
python -m pytest -q
agentordeal quickstart
```

## Adding a scenario

A scenario is data plus a deterministic detector -- never an LLM judge.
Add it to the module for its category in `agentordeal/scenarios/` (or as a
plugin, see `examples/my_plugin.py`):

1. Pick the next free id in the category prefix (PI-, TM-, DE-, MP-,
   GH-, MCP-).
2. Plant a unique canary in `setup.secret`; the verdict must come from
   an observable behaviour: a leaked canary, a forbidden tool call or
   argument, or a poisoned memory write.
3. Fill in `severity`, `owasp_asi`, and the ATLAS mapping (see
   `agentordeal/coverage.py`).
4. Regenerate the calibration file and taxonomy:
   `python -m agentordeal.calibration --write` and update
   `docs/SCENARIO_TAXONOMY.md`.
5. The calibration test asserts the demo agents' verdicts on your
   scenario; if a demo verdict surprises you, that is a finding, not a
   test to silence.

## Adding an adapter

Adapters implement `invoke(prompt, context) -> {text, tool_calls,
memory_writes}` (see `agentordeal/adapters/base.py`). Tests for adapters
whose framework is an optional extra must use fakes, so the suite stays
green with no extras installed.

## Rules that keep scores trustworthy

- Never edit a published scorecard or leaderboard entry by hand.
  Leaderboard changes come only from `leaderboard/run_leaderboard.py`.
- A detector change is a battery change: bump the battery version in
  `agentordeal/scenarios/__init__.py` and note it in `docs/BATTERY.md`.
- Tests must pass with no network and no API keys.

## Pull requests

Keep them small, say which iteration or issue they address, and include
the test output. Commit messages: all lowercase.
