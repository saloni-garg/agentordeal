# Security Policy

AgentOrdeal is a security testing tool. It contains attack payloads
(prompt injection, exfiltration, tool-misuse and related scenarios) that
are intended to be run only against systems you own or are authorised
to test.

## Reporting a vulnerability in Ordeal itself

Please do NOT open a public issue for a vulnerability in the harness
(for example a way for a target under test to escape the harness,
execute code on the runner, or falsify a scorecard). Instead, use
GitHub's private vulnerability reporting on this repository
(Security -> Report a vulnerability). You should receive an
acknowledgement within 7 days.

## Findings against third-party agents

Scores and findings produced by Ordeal against third-party projects
follow the rerun and dispute process in docs/METHODOLOGY.md, including
private notification and a 14-day fix window for critical findings
before any leaderboard publication.

## Supported versions

Only the latest released version receives fixes.
