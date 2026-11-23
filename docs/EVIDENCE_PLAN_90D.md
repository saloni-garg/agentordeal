# 90-Day Evidence Plan -- adoption first, evidence as the by-product

Goal: not stars for their own sake. The petition-grade exhibits are **dependents,
CI installs, citations, and 3-5 adopter letters** banked in the first 90 days.
Stars are the funnel that produces those; every week below names the exhibit it
is meant to produce, not just the activity.

## Metrics to log as exhibits (from day 1, in a dated log)
- GitHub stars, forks, clones, and **dependents** (repos / workflows using the Action).
- PyPI downloads (weekly snapshot, dated screenshot + CSV).
- GitHub Action installs: workflows referencing the Action (code search count, dated).
- Citations: papers, blog posts, talks and docs that cite the suite or a scorecard.
- Adopter letters: company / project, signer, date, exact production use described.
- Maintainer correspondence for privately notified scores (dates, rerun outcomes).

## Launch sequence (weeks 1-2)
1. Score 2-3 popular open agents privately. Notify their maintainers first, with
   the scorecard, the pinned version, and the 14-day rerun / fix window in
   METHODOLOGY.md. Do not publish a critical score before that window.
2. Ship the GitHub Action the same week as the public leaderboard, so the first
   wave of attention converts into CI installs, not just stars.
3. Launch posts: Hacker News (Show HN), Reddit r/netsec / r/LocalLLaMA / relevant
   security subs, and the MCP / agent framework Discords. One post, one claim:
   "we scored named open agents; here is the reproducible scorecard."
4. Leaderboard goes live with unscored placeholders clearly marked; scored entries
   are added only after the maintainer window above.

## Weekly milestones
- **Weeks 1-2:** launch sequence above. Target: Action live, 3 private maintainer
  notifications sent, leaderboard live. Exhibit: notification letters + Action page.
- **Weeks 3-4:** first framework adapter PRs / issues (LangGraph, CrewAI, OpenAI
  Agents SDK -- in that order, by community size). Ask the first 5 company users
  for adopter letters while the value is fresh (template below). Target: 1 letter.
- **Weeks 5-6:** first leaderboard update release (a news moment: new scores,
  reruns, fixes). Target: 10+ dependents, 2 letters banked.
- **Weeks 7-8:** workshop / paper submission: submit the scenario taxonomy and
  leaderboard results to an agent-security or evals workshop (targets: NeurIPS /
  ICLR evals and agent workshops, USENIX / CCS security workshops -- pick by the
  deadline that falls in this window; do not miss it for polish). Exhibit: submission receipt.
- **Weeks 9-10:** maintainer office-hours / talk proposals to agent and MCP meetups
  and conferences (judging + speaking record). Target: 1 accepted talk, 3 letters.
- **Weeks 11-12:** second leaderboard release + a short results write-up citing
  dependents and reruns. Target: 3-5 letters, 25+ dependents, citation trail started.
- **Day 90 gate:** if letters < 3 or dependents < 10, the next 90 days go to adopter
  outreach and adapters, not new scenarios. Adoption compounds; scenarios do not.

## Adopter letter -- ask template (outline)
- Who: an engineer / lead who ran Ordeal in CI or in an evaluation, at a named org.
- Ask (one paragraph, sent while the value is fresh): "Would you write 4-6 sentences
  on your letterhead: what you ran it on, where it runs (CI / eval), what it caught
  or changed, and that you would recommend it? I will not edit your words; you approve
  the final text before it is used anywhere."
- The letter must state production / CI use in the signer's own words, name the org
  and the signer's role, and be dated. A star or a quote in a README is not a letter.

## What not to do
- Do not publish a named agent's critical score before its maintainer window.
- Do not fabricate scores, dependents or letters. An unscored placeholder is
  labelled unscored; that honesty is what makes the scored entries citable.
- Do not add scenarios instead of chasing adopters after the day-90 gate.
