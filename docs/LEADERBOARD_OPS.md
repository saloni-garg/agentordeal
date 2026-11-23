# Running the leaderboard yourself

The leaderboard is a pipeline, not a page someone edits.

## The pipeline

```bash
pip install .
python leaderboard/run_leaderboard.py            # all configured targets
python leaderboard/run_leaderboard.py --only llm-reference
```

Configuration is `leaderboard/targets.json`: one entry per project
with a `target` (anything `agentordeal run --target` accepts, including
`llm:<model>`), a pinned `version`, and a `url`. Entries with
`"target": null` are listed as unscored. The script:

1. Runs the full battery against each configured target.
2. Writes scorecards (JSON, HTML, SARIF, JUnit, badge, trace) to
   `leaderboard/results/<slug>/`.
3. Regenerates `leaderboard/leaderboard.json` and
   `leaderboard/index.html` from those scorecards -- target spec,
   pinned version, tool version, battery version (inside each
   scorecard's metadata) and run date included.

An entry whose target cannot run (for example an `llm:` target with no
`AGENTORDEAL_LLM_API_KEY` in the environment) is reported as skipped in
the script's JSON report and stays unscored. Scores are never carried
over from a previous run.

## Scheduled, self-hosted

`examples/leaderboard-update.yml` is a ready GitHub Actions workflow:
weekly (and on demand), it installs the package, runs the pipeline,
and uploads the whole `leaderboard/` directory as an artifact. It has
`contents: read` permission only and commits nothing -- a human
reviews the artifact, honours the maintainer rerun window for critical
findings (docs/METHODOLOGY.md), and only then publishes.

For `llm:` targets, provide the key as a repository secret named
`AGENTORDEAL_LLM_API_KEY` and the model as a variable
`AGENTORDEAL_LLM_MODEL`. The key is read from the environment at runtime
and is never written to a scorecard, trace, or the leaderboard.

## Comparing runs over time

Every scorecard carries run metadata (timestamp, duration, seed,
target version, battery version). To see what changed between two
runs of the same target:

```bash
agentordeal diff leaderboard/results/<slug>/scorecard.json new/scorecard.json --fail-on-regression
```
