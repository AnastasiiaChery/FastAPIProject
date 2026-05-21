You are a **senior software engineer** preparing code for review for Jira ticket **$ARGUMENTS**.

This command runs after `/devflow` has completed implementation and tests. It performs a self-review of the code, then commits, pushes, and opens a draft PR.

Work through the following phases in order. Do not stop or ask for confirmation between phases — complete the entire workflow autonomously until you reach the PAUSE point at the end.

---

## PHASE 0 — Load Project Config

Read `devflow/config.yml` and extract:
- `jira.project` — to validate the ticket prefix
- `github.default_branch` — base branch for `git diff` and PRs
- `code.test_framework` — the test command to re-run after fixes
- `jira.server` — to build Jira ticket URLs

Use these values in all subsequent phases instead of hardcoded defaults.

---

## PHASE 1 — Locate Worktree / Branch

Determine the working branch and directory for this ticket:

1. Check if the worktree `../<repo-name>-$ARGUMENTS` exists:
   ```bash
   git worktree list
   ```
2. If it exists — all subsequent commands run from that worktree path.
3. If it does not exist — check if the current branch matches `feature/$ARGUMENTS-*` or `spike/$ARGUMENTS`. If yes, use the current directory.
4. If neither — stop and print:
   ```
   🚫 CANNOT PROCEED: No worktree or feature/spike branch found for $ARGUMENTS.
   Run /devflow $ARGUMENTS first, or check out the correct branch manually.
   ```

> For Spike/Investigation tickets the branch is `spike/$ARGUMENTS` (no worktree). Subsequent phases will detect this and skip self-review.

---

## PHASE 2 — Self Code Review

> ⚪ **Skip for Spike/Investigation tickets** (current branch starts with `spike/`).

Run `git diff $BASE_BRANCH` (where `$BASE_BRANCH` is from `devflow/config.yml`) and review the entire diff as if you are a senior engineer who did NOT write this code. Check:

- **Clarity**: would a colleague understand this diff in 2 minutes with no context?
- **Minimal footprint**: is every new abstraction actually needed, or does it add indirection without value?
- **Silent failures**: are there errors that could be swallowed, states that could be corrupted?
- **Edge cases**: does this handle everything the ticket requires?
- **Naming**: is it consistent with the rest of the codebase?
- **Security**: no SQL string concatenation, no `eval()`, inputs validated at boundaries

For each issue found, print:
```
🔍 REVIEW: <file>:<line> — <issue description>
   Fix: <what was changed>
```

Apply all fixes. Re-run the test suite after fixes to confirm everything still passes. Use the test command from `devflow/config.yml`.

If no issues are found, print: `✅ Self review — no issues found`

---

## PHASE 3 — Commit and Create Draft PR

1. If self-review produced fixes, commit them:
   ```bash
   git add -A
   git commit -m "fix: self-review fixes for $ARGUMENTS"
   ```
   If self-review found no issues (or was skipped), skip this step — the implementation commit from Phase 5.5 of `/devflow` is already in place.

2. Push the branch to origin.

3. Before creating the PR, build the body dynamically:

   **Summary** — derive from actual changed files (`git diff --name-only $BASE_BRANCH`), not generic phrases:
   - Group changes by area (e.g. "Added X to `api/`", "Updated schema in `models/`")
   - 2-4 bullets max, each referencing a real file or function

   **Decisions** — locate the plan file with:
   ```bash
   find docs/plans -name "*-$ARGUMENTS-plan.md" | sort | tail -1
   ```
   Read the `## Decisions` section from that file (written there by `/devflow` Phase 4.5). If the section is absent, empty, or the file is not found, omit this section from the PR entirely.

   **Risk** — include only if at least one of these is true:
   - A pre-existing bug was found and noted
   - A scope assumption was made (ticket was ambiguous)
   - A pattern deviation was chosen over convention

   **Out of scope** — include only if explicitly excluded items exist in the plan file (same path resolved above).

4. Create the draft PR:

```
gh pr create --draft \
  --title "$ARGUMENTS: <ticket title>" \
  --body "$(cat <<'EOF'
## Jira Ticket
[$ARGUMENTS](<jira.server>/browse/$ARGUMENTS)

## Summary
<derived from changed files — 2-4 bullets>

## Decisions
<all ⚡ DECISION entries from implementation — omit section if none>

## Risk
<pre-existing bugs found, scope assumptions made, pattern deviations — omit section if none>

## Out of scope
<items explicitly excluded in the plan — omit section if none>

## Test plan
- [ ] All unit tests pass
- [ ] Acceptance criteria from ticket verified
EOF
)"
```

5. After the PR is created, update Jira:

```bash
# Move ticket to In Review
jira issue move $ARGUMENTS "In Review"

# Add PR link as a comment
jira issue comment add $ARGUMENTS "PR opened: <PR_URL>"
```

If the transition fails (status name differs), skip silently and note it in the final summary.

---

## PAUSE — Await Reviewer

Collect the following from what actually happened:
- Number of self-review issues found and fixed (from Phase 2)
- PR URL (from Phase 3)
- Jira transition status (from Phase 3)

Then print exactly this message:

```
============================================================
PR CREATED — AWAITING REVIEW

Draft PR: <PR_URL>

What was automated:
  <✅ Self review — <N> issue(s) found and fixed | ✅ Self review — no issues found | ⚪ Self review skipped (Spike)>
  ✅ Committed and pushed branch
  ✅ Draft PR created
  <✅ Jira ticket moved to "In Review" + PR link added | ⚠️  Jira transition skipped: <reason>>

Next steps:
  1. Share the PR link with your reviewer
  2. When review comments arrive, run:
     /devflow-review $ARGUMENTS
============================================================
```

Then stop. Do not continue past this point.
