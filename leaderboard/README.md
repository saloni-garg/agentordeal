# Leaderboard

The leaderboard's home is now the separate **agentordeal-leaderboard**
repository (local staging at `~/workspace/agentordeal-leaderboard/`).
`scores.json` in that repository is the canonical public record of
AgentOrdeal benchmark results; its `index.html` is generated from
`scores.json` by that repository's `generate.py`.

The files in this directory (`leaderboard.json`, `index.html`,
`results/`) are the runner's local pipeline output, produced by
`run_leaderboard.py`. They are the input to the public record, not
the public record itself.

## Exporting to the leaderboard repository

After building the leaderboard, also write the data in the
leaderboard repository's `scores.json` format (same fields, plus a
per-entry `battery_version` and, for scored entries, the per-category
`categories` breakdown read from each scorecard):

```
python leaderboard/run_leaderboard.py --export ../agentordeal-leaderboard/scores.json
```

Without `--export`, the behaviour of `run_leaderboard.py` is
unchanged. After exporting, append a history line per scored target
under `history/` in the leaderboard repository and regenerate its
site with `python3 generate.py` there. See that repository's
README.md for the history format and the full flow.
