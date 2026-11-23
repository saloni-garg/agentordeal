# Publish runbook -- AgentOrdeal v0.5.0

The ordered steps for release day. One coherent release: runner, specification, leaderboard, documentation, and the PyPI package go out together. Nothing in this runbook has been done. Every step waits for the user to say go.

Step counts: 22 steps Muse can do through the user signed in browser session or from this machine once the go is given, 5 steps only the user can do, and 7 post publish verification checks. Total 34 numbered steps.

Names used throughout:

- Runner repository: saloni-garg/agentordeal -- already claimed. The empty public repository created 2026-02-23 was renamed to this name on 2026-11-22. No code has been pushed to it.
- Specification repository: saloni-garg/agentordeal-spec -- to be created by renaming an existing empty or near empty repository, see step 3.
- Leaderboard repository: saloni-garg/agentordeal-leaderboard -- to be created by renaming an existing repository, see step 4.
- Local sources: ~/workspace/agent-ordeal/ (runner), ~/workspace/agentordeal-spec/ (specification), ~/workspace/agentordeal-leaderboard/ (leaderboard), release pack in ~/workspace/agent-ordeal/release/.

Rules that hold for the whole runbook:

- No outward text is posted in any form the user has not confirmed. The About descriptions, topics, and release notes in this pack are the confirmed text source. If any wording needs to change on the day, stop and get the new wording confirmed before using it.
- Commit messages are all lowercase, with variable names keeping their case, and never mention AI assistance.
- The PyPI token, any password, and any one time code are entered by the user only, through secure entry. They are never written to a file, a commit, or a log.

---

## Phase A -- User only steps that unlock the rest (5 steps)

U1. Confirm the two rename candidates. Earlier identification, still subject to confirmation on the day: gen-ai-model-sgvton (created 2025-02-20, private, empty) as the source for agentordeal-spec, and hr-ninja (created 2025-03-01, private, 80 KB) as the source for agentordeal-leaderboard. A third candidate, voip-india (created 2025-03-03, private, 165 KB), is the fallback for either. If the user picks different sources, update steps 3 and 4 with the picked names before doing them.

U2. Create the PyPI account if one does not exist, enable two factor authentication on it, and create an API token scoped to the agentordeal project (a first upload may need an account scoped token; scope it to the project right after the first upload). Enter the token only through secure entry when step 15 asks for it. Never paste it into chat or a file.

U3. Give the release go. One clear go covers steps 1 to 22 in order. Any step the user wants held is named at that point and skipped, not improvised around.

U4. Domain decision. Optional on release day and not a blocker for the GitHub and PyPI release. If the user wants a domain (agentordeal.ai, .dev, or .org were the candidates discussed), the user buys and registers it through their own registrar account and payment. Muse does not buy domains.

U5. Trademark decision. Optional and separate from release day. If the user wants a trademark search or filing for AgentOrdeal, the user instructs counsel or files directly. Muse does not file trademarks. The release does not wait for this.

## Phase B -- Repository renames and first pushes (steps 1 to 8, Muse via browser session and this machine)

1. Rename the specification source repository. In the browser session: open the confirmed source repository from step U1 (default gen-ai-model-sgvton), Settings, General, rename to agentordeal-spec. Confirm the new URL loads: https://github.com/saloni-garg/agentordeal-spec

2. Set the specification repository visibility. If the source repository is private, change visibility to public in the same Settings session, after the rename. Confirm the repository page loads while signed out or in a private window if the session allows it.

3. Rename the leaderboard source repository. In the browser session: open the confirmed source repository from step U1 (default hr-ninja), Settings, General, rename to agentordeal-leaderboard. Confirm the new URL loads: https://github.com/saloni-garg/agentordeal-leaderboard

4. Set the leaderboard repository visibility to public, the same way as step 2, and confirm the page loads.

5. Push the runner. From this machine: the local runner repository already targets the claimed name. Add the remote https://github.com/saloni-garg/agentordeal.git if it is not set, then push the main branch. The claimed repository is empty, so this is a first push, not a force push. Confirm the file list on the repository page matches the local tree.

6. Push the specification. Add the remote https://github.com/saloni-garg/agentordeal-spec.git to the local specification repository and push its branch. Confirm SPEC.md renders on the repository page.

7. Push the leaderboard. Add the remote https://github.com/saloni-garg/agentordeal-leaderboard.git to the local leaderboard repository and push the main branch. Confirm index.html, scores.json, and generate.py are present.

8. Check all three repository pages signed out. Each should load with no sign in, show the MIT license, and show no placeholder text that says local staging. If the leaderboard README still says nothing is published yet, that line is edited in step 12 before the releases are created.

## Phase C -- Repository presentation (steps 9 to 12, Muse via browser session)

9. Runner About. On saloni-garg/agentordeal: set the About description, website field, and topics exactly as written in release/REPO_PACK.md section 1. Website stays empty in this step.

10. Specification About. On saloni-garg/agentordeal-spec: set About and topics exactly as in release/REPO_PACK.md section 2.

11. Leaderboard About. On saloni-garg/agentordeal-leaderboard: set About and topics exactly as in release/REPO_PACK.md section 3. Leave the website field for step 13, after Pages gives the real URL.

12. Release day README edits, runner and leaderboard. Two small edits, both already drafted or noted, neither applied before this step:
    - Runner README: if the user approved release/README_TOP_BLOCK.md, insert that block under the tagline. Replace the two placeholder shields with the real CI badge for the ci workflow and the real PyPI badge for agentordeal. Update the GitHub Action example to uses: saloni-garg/agentordeal@v0.5.0 and remove the placeholder wording.
    - Leaderboard README: remove the local staging status paragraph and replace it with one line stating the leaderboard is live at the Pages URL from step 13.
    Each edit is its own commit, message in lowercase, for example: update readme for first public release

## Phase D -- Leaderboard site (step 13, Muse via browser session)

13. Enable GitHub Pages on the leaderboard repository. Settings, Pages: source = deploy from a branch, branch = main, folder = / (root). Wait for the deployment GitHub reports, open the site URL, and confirm the ranked table loads with the 10 scored entries. Copy the exact site URL into the website field of the leaderboard repository and the website field of the runner repository.

## Phase E -- PyPI release (steps 14 to 16)

14. Re-check the name and the artifacts. Confirm agentordeal is still the expected project name state on PyPI, confirm release/dist/ holds exactly the two 0.5.0 artifacts, and re-run the twine check output recorded in release/PYPI_AUDIT.md against them if any file changed since the audit.

15. Upload. The user enters the PyPI API token through secure entry (step U2). With the token in place for this one command only, run the upload from this machine: twine upload release/dist/agentordeal-0.5.0-py3-none-any.whl release/dist/agentordeal-0.5.0.tar.gz -- the token is not saved, not written to a config file, and not echoed. If PyPI asks for a one time code at any point, the user enters it.

16. Scope the token down. In the browser session, with the user present: if an account scoped token was used for the first upload, replace it with a project scoped token for agentordeal for future releases.

## Phase F -- GitHub Releases (steps 17 to 19, Muse via browser session)

17. Runner release. On saloni-garg/agentordeal: Releases, create release, tag v0.5.0, title and notes from release/RELEASE_NOTES_v0.5.0.md part 1. Attach the wheel and the sdist from release/dist/ as release assets. Publish the release.

18. Specification release. On saloni-garg/agentordeal-spec: create the release with the title and notes from release/RELEASE_NOTES_v0.5.0.md part 2, using the tag choice recorded in that file (v1.0 for the specification version, or v0.5.0 for one shared tag). Publish the release.

19. Leaderboard release. On saloni-garg/agentordeal-leaderboard: create the release, tag v0.5.0, title and notes from release/RELEASE_NOTES_v0.5.0.md part 3. Publish the release.

## Phase G -- Action and cross links (steps 20 to 22, Muse via browser session)

20. Confirm the Action reference works as written. The action.yml in the runner repository installs agentordeal from PyPI and falls back to the action checkout. After step 15 the PyPI path is live, so the example in the README (updated in step 12) is now a working reference, not a placeholder.

21. Cross link the three repositories. Pin or link from each README if not already present: the runner links the specification and the leaderboard, the specification links the runner and the leaderboard, the leaderboard links the runner and the specification. Project URLs on PyPI already carry all three links from step 15.

22. Announce nothing yet. No posts, no messages, no submissions are part of this runbook. Any announcement is a separate decision with its own confirmed text.

## Post publish verification checklist (7 checks)

V1. Clean install from PyPI. In a fresh venv on this machine: pip install agentordeal, then agentordeal --help exits 0 and agentordeal demo prints demo-vulnerable 12.3 grade F and demo-hardened 100.0 grade A.

V2. Citation in a fresh scorecard. The demo run in V1 writes scorecards whose specification field carries the citation string in the form AgentOrdeal-1.0 / battery=1.2.0 / seed=none / score=100.0 for the hardened target.

V3. Test suite from PyPI install. Run the repository test suite against the installed package the same way as the audit (run from /tmp, imports from the installed wheel). Expected: 123 passed.

V4. Leaderboard site live. The Pages URL from step 13 loads signed out, the ranked table shows 10 scored entries, AutoGen first at 93.5 A and smolagents last at 75.8 C, and the not yet scored section shows no invented scores.

V5. Action smoke test. In a scratch repository or a workflow dispatch on the runner repository, run the Action against demo-hardened with fail-under 70. Expected: job passes, score and grade outputs are set, and the scorecard artifact is uploaded.

V6. All three releases visible. The runner, specification, and leaderboard release pages load signed out, with the notes as written in release/RELEASE_NOTES_v0.5.0.md and, on the runner release, both distribution files attached.

V7. PyPI page correct. The agentordeal project page shows version 0.5.0, the README as the long description, License-Expression MIT, and the six project URLs pointing at the three repositories, the issues page, and the changelog.

## If something fails mid release

- A push is rejected: stop, read the exact error, and report it. Never force push over the claimed repository without the user seeing the state first.
- PyPI rejects the upload for a name or metadata reason: stop before any rename or version change. A failed first upload does not burn the version unless files were accepted. Report the exact PyPI message.
- Pages does not deploy: check the Pages build message in the leaderboard repository settings and report it. The release stands without the site; the website fields stay empty until the site loads.
- Any step that would change wording the user confirmed: stop and ask. Confirmed text is used as written or not at all.
