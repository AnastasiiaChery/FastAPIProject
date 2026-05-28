You are a **senior software engineer** preparing code for review for Jira ticket **$ARGUMENTS**.

> **Before doing anything else:** if `$ARGUMENTS` is empty or missing, print:
> ```
> Usage: /devflow-review <TICKET-ID>
> Example: /devflow-review SCRUM-123
> ```
> Then stop immediately. Do not proceed without a ticket ID.

This command runs after `/devflow` has completed implementation and tests. It performs a self-review of the code, then commits, pushes, and opens a draft PR.

Work through the following phases in order. Do not stop or ask for confirmation between phases — complete the entire workflow autonomously until you reach the PAUSE point at the end.

**Skills and agents available:**
- Jira operations → use the **`jira` skill** (`.claude/skills/jira/SKILL.md`)
- GitHub operations → use the **`github` skill** (`.claude/skills/github/SKILL.md`)
- Code review → delegate to the **`code-reviewer` agent** (`.claude/agents/code-reviewer.md`)

---

## PHASE 0 — Load Project Config

Read `devflow/config.yml` and extract:
- `jira.project` — to validate the ticket prefix
- `jira.server` — to build Jira ticket URLs
- `jira.in_review_status` — the exact Jira status name to transition to (default: `"In Review"` if key absent)
- `github.default_branch` — base branch for `git diff` and PRs
- `github.draft_pr` — whether to open the PR as draft (`true`) or ready (`false`); default `true` if absent
- `code.test_framework` — the test command to re-run after fixes
- `paths.plans` — where plan files are saved (default: `docs/plans/`)

Use these values in all subsequent phases instead of hardcoded defaults.

Then validate the ticket prefix — extract everything before the first `-` from `$ARGUMENTS` and compare to `jira.project`. If they don't match, stop:
```
🚫 WRONG PROJECT: ticket $ARGUMENTS belongs to project <prefix>, but this repo is configured for <jira.project>.
   Check devflow/config.yml or make sure you passed the right ticket ID.
```

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

> ⚪ **Skip for Spike/Investigation tickets** (branch starts with `spike/`).

**Delegate to the `code-reviewer` agent** (`.claude/agents/code-reviewer.md`).

Pass: `git diff origin/<github.default_branch>...HEAD`, ticket ID, base branch.

The agent classifies each finding as BLOCKER, MAJOR, MINOR, or NIT.

If the agent reports any `BLOCKER` or `MAJOR` issues:
1. Apply all required fixes
2. Re-run the test suite (`code.test_framework` from config) to confirm everything passes
3. Commit the fixes:
   ```bash
   git add <list every changed file by name — never git add . or git add -A>
   git commit -m "fix: self-review fixes for $ARGUMENTS"
   ```

Note the result (count of BLOCKER/MAJOR issues or "no blockers") for the PAUSE summary.

---

## PHASE 3 — Push & Open Draft PR

Use the **`github` skill** and **`jira` skill** for all operations.

### Push

```bash
git push -u origin HEAD
```

### Build PR body

Locate the plan file:
```bash
find <paths.plans> -name "*-$ARGUMENTS-plan.md" | sort | tail -1
```

Write `/tmp/pr-body-$ARGUMENTS.md` with the following — substitute all placeholders with real values:

**Summary** — run `git diff --name-only origin/<github.default_branch>...HEAD`, group by area:
- 2-4 bullets max, each referencing a real file or function (not generic phrases)

**Decisions** — read `## Decisions` from the plan file. Omit entire section if absent or empty.

**Risk** — include only if: pre-existing bug found, scope assumption made, or pattern deviation chosen.

**Out of scope** — include only if explicitly excluded items exist in the plan file.

```markdown
## Jira Ticket
[$ARGUMENTS](<jira.server>/browse/$ARGUMENTS)

## Summary
<2-4 bullets from actual changed files — reference real files/functions>

## Decisions
<## Decisions section from plan file — omit entire section if empty or file not found>

## Risk
<pre-existing bugs, scope assumptions, pattern deviations — omit entire section if none>

## Out of scope
<explicitly excluded items from plan — omit entire section if none>

## Test plan
- [ ] All unit tests pass
- [ ] Acceptance criteria from ticket verified
```

### Create PR

```bash
gh pr create [--draft if github.draft_pr is true] \
  --title "$ARGUMENTS: <exact ticket title>" \
  --body-file /tmp/pr-body-$ARGUMENTS.md
   ```

5. After the PR is created, update Jira:
   ```bash
   jira issue move $ARGUMENTS "<jira.in_review_status>"
   jira issue comment add $ARGUMENTS "PR opened: <PR_URL>"
   ```

   If the transition fails — do not guess an alternative status name. Capture the error for the PAUSE summary and continue. The PR is already created and that is the critical outcome.

---

## PAUSE — Await Reviewer

Collect the following from what actually happened:
- Number of BLOCKER/MAJOR issues found and fixed (from Phase 2)
- PR URL (from Phase 3)
- Jira transition status (from Phase 3)

Then print exactly this message:

```
============================================================
PR CREATED — AWAITING REVIEW

Draft PR: <PR_URL>

What was automated:
  <✅ Self review — <N> BLOCKER/MAJOR issue(s) found and fixed | ✅ Self review — no blockers found | ⚪ Self review skipped (Spike)>
  ✅ Pushed branch to origin
  ✅ Draft PR created
  <✅ Jira → "In Review" + PR link added | ⚠️  Jira transition failed: <error message> — move manually>

Next steps:
  1. Share the PR link with your reviewer
  2. Address review comments in this session or start a new one
============================================================
```

Then stop. Do not continue past this point.
