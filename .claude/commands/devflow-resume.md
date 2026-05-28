You are a **senior software engineer** restoring a saved devflow session.

This command reads the saved session state and tells you exactly where you left off so you can continue without losing context.

Work through the following steps in order. Do not ask for confirmation between steps — complete the full status report autonomously.

---

## STEP 1 — Load Project Config

Read `devflow/config.yml` and extract:
- `jira.server` — to build Jira ticket URLs
- `github.default_branch` — base branch (for worktree recreation instructions)
- `paths.plans` — where plan files are saved (default: `docs/plans/` if absent)

---

## STEP 2 — Read Saved State

```bash
cat .devflow-state.json
```

If the file does not exist, print:
```
ℹ️  No saved devflow session found (.devflow-state.json missing).
   Start a new session with: /devflow TICKET-ID
```
Then stop.

Extract these fields from the JSON:
- `active_ticket` → set as `$TICKET`
- `worktrees` → list of absolute worktree paths
- `current_branch`
- `saved_at`

If `active_ticket` is empty, null, or missing, print:
```
⚠️  State file found but no active ticket detected. Branch was: <current_branch>
   If you know the ticket ID, run: /devflow TICKET-ID
```
Then stop.

---

## STEP 3 — Validate Worktree

```bash
git worktree list
```

Compare each path from the `worktrees` list in state against the output. Set `WORKTREE_EXISTS` to true if any match is found, false otherwise. Note the matching path for use in Step 5.

---

## STEP 4 — Fetch Live Status

Run all three lookups independently — they do not depend on each other:

**Jira status and summary:**
```bash
jira issue view $TICKET --plain | grep -E "^(Status|Summary):"
```

**Plan file:**
```bash
find <paths.plans> -name "*-$TICKET-plan.md" | sort | tail -1
```

**Open or merged PR:**
```bash
gh pr list --state all --search "$TICKET" --json number,title,url,isDraft,state | head -c 2000
```

---

## STEP 5 — Infer Phase and Build Status Block

Based on what was found in Steps 3 and 4, select the matching case below.

**Case A — Worktree missing, no PR found:**
```
⚠️  Worktree no longer exists. Plan: <found: path | not found>
Next step: Re-create worktree with:
  git worktree add -b <current_branch> ../<repo-name>-$TICKET <default_branch>
Then continue implementation and run /devflow-review $TICKET when ready.
```

**Case B — Worktree exists, no open PR:**
```
✅ Worktree: <path>
✅ Plan: <path | not found>
📍 Implementation complete or in progress — PR not yet created.
Next step: When ready, run:
  /devflow-review $TICKET
```

**Case C — PR found, draft=true:**
```
✅ Draft PR #<number>: <title>
   <url>
📍 Awaiting code review.
Next step: Share PR with your reviewer.
```

**Case D — PR found, draft=false, state=open:**
```
✅ PR #<number> ready for review: <url>
📍 Review in progress.
Next step: Monitor review comments and address feedback when it arrives.
```

---

## STEP 6 — Print Session Summary

Wrap the case output from Step 5 in the following block. Fill every placeholder with real values — do not leave angle-bracket placeholders in the output.

```
============================================================
DEVFLOW SESSION RESTORED

Ticket:  $TICKET — <Summary value from Jira>
Saved:   <saved_at>
Branch:  <current_branch>
Status:  <Status value from Jira>

Where you left off:
  <case A / B / C / D text from Step 5>
============================================================
```

Then stop. Do not continue past this point.
