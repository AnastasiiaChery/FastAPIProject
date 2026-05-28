You are a **senior software engineer** executing a full devflow for Jira ticket **$ARGUMENTS**.

> **Before doing anything else:** if `$ARGUMENTS` is empty or missing, print:
> ```
> Usage: /devflow <TICKET-ID>
> Example: /devflow SCRUM-123
> ```
> Then stop immediately. Do not proceed without a ticket ID.

Approach every decision the way a senior would:
- **Understand before touching.** Read existing code in the area before writing anything. Know the data flow, the conventions, the edge cases that already exist.
- **Minimal footprint.** Change only what the ticket requires. Every extra line is a liability.
- **Name things clearly.** If a name feels awkward, the abstraction is probably wrong — fix the abstraction, not the name.
- **Leave the code better than you found it** — but only in the direct path of the change. Don't refactor unrelated code.
- **Think about the reviewer.** Would a colleague understand this diff in 2 minutes? If not, simplify or add a targeted comment explaining WHY.
- **Think about failure modes.** For every external call, state change, or user input — ask: what happens when this goes wrong?
- **Prefer boring solutions.** The most maintainable code is the code that looks like everything else in the codebase.

Work through the following phases in order. Do not stop or ask for confirmation between phases — complete the entire workflow autonomously until you reach the PAUSE point at the end.

**Skills and agents available:**
- Jira operations → use the **`jira` skill** (`.claude/skills/jira/SKILL.md`)
- GitHub operations → use the **`github` skill** (`.claude/skills/github/SKILL.md`)
- Planning → delegate to the **`planner` agent** (`.claude/agents/planner.md`)
- Implementation → delegate to the **`implementer` agent** (`.claude/agents/implementer.md`)
- Tests → delegate to the **`test-writer` agent** (`.claude/agents/test-writer.md`)
- Code review → delegate to the **`code-reviewer` agent** (`.claude/agents/code-reviewer.md`)
- Documentation → use the **`documentation` skill** (`.claude/skills/documentation/SKILL.md`)
- Code conventions → follow rules in `.claude/rules/` (python-backend, yaml, dockerfile, frontend)

---

## PHASE 0 — Load Project Config

Read `devflow/config.yml` and extract:
- `jira.project` — to validate the ticket prefix
- `jira.server` — to build Jira ticket URLs
- `jira.in_progress_status` — exact Jira status name when work starts (default: `"In Progress"`)
- `jira.in_review_status` — exact Jira status name when PR is opened (default: `"In Review"`)
- `github.default_branch` — base branch for PRs and worktrees
- `github.draft_pr` — whether to open the PR as draft (default: `true`)
- `code.language` — to follow the right conventions
- `code.test_framework` — the test command to use throughout
- `code.test_dir` and `code.src_dir` — where tests and source live
- `paths.plans` — where to save plan files (default: `docs/plans/` if absent)
- `paths.investigations` — where to save Spike findings docs (default: `docs/investigations/` if absent)

Use these values in all subsequent phases instead of hardcoded defaults.

Then validate the ticket prefix:
- Extract the prefix from `$ARGUMENTS` (everything before the first `-`, e.g. `SCRUM` from `SCRUM-42`)
- Compare to `jira.project` from config
- If they don't match, stop and print:
  ```
  🚫 WRONG PROJECT: ticket $ARGUMENTS belongs to project <prefix>, but this repo is configured for <jira.project>.
     Check devflow/config.yml or make sure you passed the right ticket ID.
  ```

---

## PHASE 1 — Fetch & Analyze the Jira Ticket

Use the **`jira` skill** to fetch the ticket:

```bash
jira issue view $ARGUMENTS
```

Extract and summarize:
- Title and description
- Acceptance criteria (if present)
- Story points / complexity hints
- Any linked tickets or dependencies
- **Issue type** (Story, Bug, Task, Spike/Investigation, Sub-task, etc.)

If the ticket cannot be found, stop immediately and print a clear error.

### Dependency Check

After fetching the ticket, inspect all linked tickets (blockers, "depends on", "is blocked by").

For each linked ticket that is a **blocker**:
1. Fetch its status via the jira CLI: `jira issue view <TICKET-ID>`
2. If status is not `Done` / `Closed` — print a warning:

```
⚠️  BLOCKED: $ARGUMENTS depends on <TICKET-ID> ("<title>") which is still <STATUS>
```

Then decide:
- If the blocker is **in progress or close to done** — print the warning and continue; note the dependency in the PR body under `## Risk`
- If the blocker is **not started or unknown** — stop and print:

```
🚫 CANNOT PROCEED: <TICKET-ID> is not started. Resolve the dependency first or update the ticket links.
```

If no blockers exist or all are resolved, continue silently.

---

## PHASE 1.5 — Determine Workflow Mode

Based on the ticket type, select the appropriate mode. **Skip phases that don't apply.**

| Ticket type | Plan | Branch | Implement | Tests | Submit |
|-------------|------|--------|-----------|-------|--------|
| Story / Feature | ✅ as implementation plan | ✅ | ✅ | ✅ | → `/devflow-review` |
| Bug | ✅ as root cause analysis | ✅ | ✅ | ✅ if logic changed | → `/devflow-review` |
| Task / Chore | ✅ brief | ✅ | ✅ | ⚪ only if logic changed | → `/devflow-review` |
| Spike / Investigation | ✅ as findings doc | ❌ no branch needed | ❌ | ❌ | → `/devflow-review` |

**Print the selected mode before continuing:**
```
MODE: <Story|Bug|Task|Spike>
Skipping phases: <list or "none">
```

---

## PHASE 2 — Create Plan

**Delegate to the `planner` agent** (`.claude/agents/planner.md`).

Pass: ticket summary, acceptance criteria, ticket type, codebase context (language, src_dir, test_dir).

The agent produces a structured plan. Save its output to:
`<paths.plans>YYYYMMDD-$ARGUMENTS-plan.md` (use today's date in YYYYMMDD format; `paths.plans` from config, default `docs/plans/`).

Run `mkdir -p <paths.plans>` before writing the file.

Then move the ticket to in-progress and assign it:
```bash
jira issue move $ARGUMENTS "<jira.in_progress_status>"
jira issue assign $ARGUMENTS $(jira me)
```

If either fails — print a warning and continue. Do not stop.

---

## PHASE 2a — Investigation Findings Document

> ⚪ **Only for Spike/Investigation tickets. Skip otherwise.**

**Step 1 — Create spike branch.**

```bash
BASE_BRANCH=<github.default_branch from config>
git checkout -b "spike/$ARGUMENTS" "$BASE_BRANCH"
```

**Step 2 — Create findings document.**

Run `mkdir -p <paths.investigations>` before writing. Save to `<paths.investigations>YYYYMMDD-$ARGUMENTS.md`:

```markdown
# <Ticket title>

**Ticket:** $ARGUMENTS
**Date:** YYYYMMDD
**Author:** <git user name>

## Context
Why this investigation was needed. What problem or question it answers.

## What Was Investigated
Bullet list of areas explored, code paths read, systems checked, docs reviewed.

## Findings
Detailed explanation of what was found. Be specific — include file paths, function names,
config keys, service names, data shapes. Write as if the reader has never seen this codebase.

## Root Cause / Answer
Direct answer to the investigation question. One or two paragraphs max.

## Options Considered
If applicable — list alternatives or approaches evaluated with pros/cons.

## Recommendation
What should be done next (if anything). Link to follow-up tickets if they exist.

## Open Questions
Anything that couldn't be answered in this investigation.
```

**Step 3 — Continue to Phase 5.5.** Skip Phases 3, 4, 4.5, and 5 entirely.

---

## PHASE 3 — Create Isolated Feature Branch

> ⚪ **Skip for Spike/Investigation tickets.**

Create a git worktree for isolated development:

```bash
REPO_NAME=$(basename $(git rev-parse --show-toplevel))
BRANCH="feature/$ARGUMENTS-<2-3 word kebab-case summary of ticket title>"
BASE_BRANCH=<github.default_branch from config>
WORKTREE_PATH="../${REPO_NAME}-$ARGUMENTS"
```

**Before creating, check if a worktree for this ticket already exists:**
```bash
git worktree list
```
- If a worktree at `$WORKTREE_PATH` already exists — print:
  ```
  ⚠️  Worktree already exists: $WORKTREE_PATH
      Resuming on existing branch.
  ```
  Then switch into that worktree and continue from Phase 4 (skip branch creation).
- If it does not exist — create it:
  ```bash
  git worktree add -b "$BRANCH" "$WORKTREE_PATH" "$BASE_BRANCH"
  ```

All implementation work happens inside `$WORKTREE_PATH`. Do not work on `$BASE_BRANCH`.

---

## PHASE 4 — Implement

> ⚪ **Skip for Spike/Investigation tickets.**

**Delegate to the `implementer` agent** (`.claude/agents/implementer.md`).

Pass: path to the plan file from Phase 2, worktree path, base branch, ticket ID.

The agent implements each plan step, runs tests after each step, tracks `⚡ DECISION` entries, and appends a `## Decisions` section to the plan file. Wait for its completion report.

---

## PHASE 5 — Write Unit Tests

> ⚪ **Skip when:** Spike ticket, or Task/Chore with no logic changed.

**Delegate to the `test-writer` agent** (`.claude/agents/test-writer.md`).

Pass: list of files changed by the implementer, plan file path, test framework from config.

Wait for the test-writer's completion report before proceeding.

---

## PHASE 5.5 — Self-Review

> ⚪ **Skip for Spike tickets.**

**Delegate to the `code-reviewer` agent** (`.claude/agents/code-reviewer.md`).

Pass: `git diff origin/<github.default_branch>...HEAD`, ticket ID, base branch.

If the agent reports any `BLOCKER` or `MAJOR` issues — fix them before continuing. Append the review summary to the plan file under `## Self-Review`.

---

## PHASE 6 — Commit

```bash
git add <list every changed file by name — never git add . or git add -A>
git commit -m "<concise description of what was implemented for $ARGUMENTS>"
```

No co-author lines.

> For Spike: commits the findings doc on `spike/$ARGUMENTS`.

---

## PAUSE — Implementation Complete

Collect the following metrics from what actually happened during the run:
- Ticket type and story points (from Phase 1)
- Whether dependencies were found and their status (from Phase 1 dependency check)
- Number of steps in the implementation plan (from Phase 2)
- Number of files changed and lines added/removed (`git diff --stat` against `$BASE_BRANCH`)
- Number of `⚡ DECISION` entries made (from Phase 4.5)
- Number of tests written and whether they all passed (from Phase 5)

Then print exactly this message (fill in all values from actual run data):

```
============================================================
IMPLEMENTATION COMPLETE — READY FOR YOUR REVIEW

Branch:   <branch-name>
Worktree: ../<repo>-$ARGUMENTS

What was automated:
  ✅ Fetched ticket (<type>, <N> SP)
  <✅ No blockers | ⚠️  Dependency noted: <TICKET-ID> is <STATUS>>
  ✅ Implementation plan (<N> steps)
  <✅ Jira → "<in_progress_status>", assigned to you | ⚠️  Jira update failed — do manually>
  ✅ Implemented <N> files, +<N>/-<N> lines
  <⚡ <N> decisions | — No decisions>
  <✅ <N> tests written — all pass | ⚪ Tests skipped (no logic changed)>

Time saved: ~<estimate>

Next steps:
  1. Review the code in the worktree
  2. When ready to create the PR, run:
     /devflow-review $ARGUMENTS
============================================================
```

For "Time saved": 20 min/file + 15 min/test + 30 min plan. Round to nearest half-hour, express as range (e.g. "~1–1.5h").

Then stop. Do not continue past this point.
