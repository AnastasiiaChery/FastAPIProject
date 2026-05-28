You are a **senior software engineer** showing the status of all active devflow sessions.

Work through the following steps in order. Do not ask for confirmation between steps — complete the full status report autonomously.

---

## STEP 1 — Load Project Config

Read `devflow/config.yml` and extract:
- `jira.project` — to validate ticket prefixes
- `jira.server` — to build Jira ticket URLs
- `paths.plans` — where plan files are saved (default: `docs/plans/` if absent)

---

## STEP 2 — List Devflow Worktrees

```bash
git worktree list --porcelain
```

Parse the output. Each worktree block has the form:

```
worktree /abs/path
HEAD abc123
branch refs/heads/feature/SCRUM-42-add-auth
```

Filter to blocks where the `branch` line matches `refs/heads/feature/*` or `refs/heads/spike/*`.

For each matching block, extract:
- `WORKTREE_PATH` — the absolute path from the `worktree` line
- `BRANCH` — the short branch name (strip `refs/heads/`)
- `TICKET` — run `grep -oE '[A-Z]+-[0-9]+'` on the branch name; take the first match

**If no devflow worktrees are found**, print:

```
ℹ️  No active devflow worktrees found.
   Start a new session with: /devflow TICKET-ID
```

Then check whether `.devflow-state.json` exists. If it does and contains a non-empty `active_ticket` field, print:

```
   Last saved session: <active_ticket> (saved <saved_at>)
   Resume with: /devflow-resume
```

Then stop.

---

## STEP 3 — Collect Status for Each Ticket

For each devflow worktree found in Step 2, fetch the following three pieces of information. Run the Jira and PR fetches independently — do not wait for one before starting the other.

**Jira status:**
```bash
jira issue view $TICKET --plain | grep -E "^Status:" | sed 's/^Status:[[:space:]]*//'
```

**PR (most recent, any state):**
```bash
gh pr list --state all --search "$TICKET" --json number,url,isDraft,state --limit 1
```

**Plan file:**
```bash
find <paths.plans> -name "*-$TICKET-plan.md" | sort | tail -1
```

If any fetch fails for a ticket, record `⚠️  fetch failed` for that field and continue to the next ticket. Do not stop.

---

## STEP 4 — Print Dashboard

Using today's date (YYYY-MM-DD format) and all collected data, print the dashboard exactly as shown below. Fill every placeholder with real values — do not leave angle-bracket placeholders in the output.

```
============================================================
DEVFLOW STATUS — <YYYY-MM-DD>
============================================================

  TICKET     BRANCH                         JIRA            PR
  ─────────────────────────────────────────────────────────────────────
  <rows — one per ticket, see rules below>

Worktrees:
  <WORKTREE_PATH>  →  <BRANCH>
  (one line per worktree)

Tip: resume the most recent session with /devflow-resume
============================================================
```

**Row format** — align columns with spaces:

```
  SCRUM-42   feature/SCRUM-42-add-auth      In Progress     #12 draft  https://github.com/...
```

**PR column rules:**
- No PR found → `—`
- `isDraft: true` → `#N draft  <url>`
- `isDraft: false`, `state: OPEN` → `#N ready  <url>`
- `state: MERGED` → `#N merged  <url>`
- Fetch failed → `⚠️  fetch failed`

Then stop. Do not continue past this point.
