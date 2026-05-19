You are an autonomous software engineer executing a full devflow for Jira ticket **$ARGUMENTS**.

Work through the following phases in order. Do not stop or ask for confirmation between phases — complete the entire workflow autonomously until you reach the PAUSE point at the end.

---

## PHASE 1 — Fetch & Analyze the Jira Ticket

Use the `jira` skill to fetch ticket $ARGUMENTS.

Extract and summarize:
- Title and description
- Acceptance criteria (if present)
- Story points / complexity hints
- Any linked tickets or dependencies

If the ticket cannot be found, stop immediately and print a clear error.

---

## PHASE 2 — Create Implementation Plan

Use the `superpowers:writing-plans` skill to create a detailed implementation plan.

The plan must cover:
- What files to create or modify
- Data flow and component interactions
- Edge cases to handle
- Test strategy (what to unit test)

Save the plan to: `docs/plans/YYYYMMDD-$ARGUMENTS-plan.md` (use today's date in YYYYMMDD format).

---

## PHASE 3 — Create Isolated Feature Branch

Use the `superpowers:using-git-worktrees` skill to create an isolated workspace.

Branch name: `feature/$ARGUMENTS-<short-slug>` where slug is a 2-3 word kebab-case summary of the ticket title.

All implementation work happens on this branch.

---

## PHASE 4 — Implement the Feature

Use the `superpowers:subagent-driven-development` skill to implement the feature.

Requirements:
- Python codebase — follow existing conventions in the project
- Check existing files for patterns before creating new ones
- Prefer editing existing files over creating new ones
- Do not add comments explaining what code does — only add comments for non-obvious WHY
- Do not add error handling for scenarios that cannot happen
- Do not add features beyond what the ticket requires

---

## PHASE 5 — Write Unit Tests

Generate pytest unit tests covering:
- Happy path for each function/endpoint added
- Edge cases identified in the plan
- Error scenarios at system boundaries

Place tests in `tests/` following the existing project structure.
If no `tests/` directory exists, create it with a `conftest.py`.

Run the tests and fix any failures before proceeding.

Command to run tests: `python -m pytest tests/ -v`

---

## PHASE 6 — Self Code Review

Use the `superpowers:requesting-code-review` skill to review the implementation from a fresh perspective.

Apply all fixes from the self-review before proceeding.

Re-run tests after fixes to confirm everything still passes.

---

## PHASE 7 — Commit and Create Draft PR

1. Stage and commit all changes with a concise commit message (no co-author lines).
2. Push the branch to origin.
3. Create a draft PR using:

```
gh pr create --draft \
  --title "$ARGUMENTS: <ticket title>" \
  --body "$(cat <<'EOF'
## Jira Ticket
$ARGUMENTS

## Summary
<1-3 bullet points describing what was implemented>

## Test plan
- [ ] All unit tests pass (`python -m pytest tests/ -v`)
- [ ] Acceptance criteria from ticket verified

## Notes
<any implementation decisions worth explaining>
EOF
)"
```

---

## PAUSE — Await User Review

After creating the draft PR, print exactly this message (fill in the actual PR URL):

```
============================================================
DEVFLOW COMPLETE — AWAITING YOUR REVIEW

Draft PR: <PR_URL>

Next steps:
  1. Open the PR and add review comments
  2. When ready, run:
     /devflow-review $ARGUMENTS
============================================================
```

Then stop. Do not continue past this point.
