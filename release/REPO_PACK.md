# Repository presentation pack -- AgentOrdeal

Exact values to set on GitHub at publish time for each of the three repositories: the About description (350 characters or fewer), the website field, and the topic list (20 topics or fewer). Set them in the browser session on release day, following the publish runbook. Nothing in this file has been applied anywhere.

Character counts were counted on the text as written.

---

## 1. Runner -- saloni-garg/agentordeal

About description (217 characters):

Reference implementation of the AgentOrdeal benchmark for autonomous agent security. Runs battery 1.2.0 (91 adversarial scenarios), produces graded, version pinned scorecards. Specification 1.0. pip install agentordeal

Website field:

Leave empty on release day. Fill it with the leaderboard site URL once GitHub Pages is live on the leaderboard repository, so the main repository points at the public record.

Topics (14):

- agent-security
- ai-agents
- autonomous-agents
- benchmark
- evaluation
- llm
- llm-security
- mcp
- model-context-protocol
- prompt-injection
- python
- red-teaming
- security
- ai-safety

Release to create: tag v0.5.0, title and notes from release/RELEASE_NOTES_v0.5.0.md part 1. Attach the two files from release/dist/ to the release as assets as well as publishing to PyPI.

---

## 2. Specification -- saloni-garg/agentordeal-spec

About description (201 characters):

The AgentOrdeal Specification 1.0: the definition of the benchmark for autonomous agent security. Battery 1.2.0 as data, scoring and detector rules, calibration protocol, and the versioning policy.

Website field:

Leave empty. This repository is a document and data record. If a website is wanted later, point it at the leaderboard site.

Topics (11):

- agent-security
- ai-agents
- benchmark
- evaluation
- llm-security
- mcp
- prompt-injection
- specification
- standard
- ai-safety
- security

Release to create: title and notes from release/RELEASE_NOTES_v0.5.0.md part 2. Tag v1.0 if the specification is tagged by its own version, or v0.5.0 if one tag is used across all three repositories. Decide once on release day and use the same choice in every link.

---

## 3. Leaderboard -- saloni-garg/agentordeal-leaderboard

About description (187 characters):

The public record of AgentOrdeal benchmark results. Ranked scores for open agent frameworks and MCP servers under Specification 1.0, battery 1.2.0, each with its full citation string.

Website field:

Set by GitHub Pages itself when Pages is enabled on this repository. The expected URL form is https://saloni-garg.github.io/agentordeal-leaderboard/ -- confirm the exact URL GitHub shows after enabling Pages and copy that URL into the website field here and into the runner repository website field.

Topics (10):

- agent-security
- ai-agents
- benchmark
- evaluation
- leaderboard
- llm-security
- mcp
- prompt-injection
- ai-safety
- security

Release to create: tag v0.5.0, title and notes from release/RELEASE_NOTES_v0.5.0.md part 3.

GitHub Pages setting for this repository: enable Pages, source = deploy from a branch, branch = main, folder = / (root). The site is the generated index.html at the repository root. No build step and no custom domain on release day.

---

## Tier 2 check of the runner README first screen

Test applied to the top of ~/workspace/agent-ordeal/README.md, down to the end of the Install section, which is what a reader sees first.

- Says AgentOrdeal is the benchmark: PASS. The first lines read: A reproducible benchmark for autonomous agent security. Then: AgentOrdeal is a benchmark. This repository is its reference implementation. Then: The benchmark -- not this code -- is the standard.
- What a score is: PARTIAL. The Report a score section gives the citation string and says a score without its battery version is not an AgentOrdeal result. It does not state in one place on the first screen that a score is a 0 to 100 graded number over the battery. That definition sits further down, under How the benchmark works.
- How a score is computed: PARTIAL on the first screen, PASS in the full page. Severity weights, the 0 to 100 scale, grades A to F, per category subscores, and the usefulness cap are all stated under How the benchmark works. A first screen reader has to scroll to reach them.
- How to reproduce: PARTIAL. The quickstart reproduces a run in 60 seconds and the Conformance section explains calibration. There is no short first screen statement that a released battery is immutable, so the same battery version is the same test, and that comparing citation strings is the reproduction check.
- How to submit an agent: GAP on the first screen. Submitting is covered indirectly: the Benchmark results section describes the leaderboard and the maintainer rerun window, and the leaderboard repository has a Submit your agent section. The runner README itself has no submit instruction near the top, and a framework maintainer landing on this repository would not see the path in the first screen.

### Fix drafted, not applied

release/README_TOP_BLOCK.md contains one short block, What is an AgentOrdeal score, drafted to sit under the tagline. It answers what a score is, how it is computed, how to reproduce it, and how to submit an agent, with the citation format. It is held for the user to approve as exact text before anyone edits README.md.

### Two smaller first screen items, noted for release day

- The two shields at the top are placeholders (CI placeholder, PyPI placeholder). Replace them with the real badges after the first publish.
- The GitHub Action example in the README uses the old repository name form and v0.1.0 and says placeholder until published. Update it to the published name and the v0.5.0 tag on release day.
