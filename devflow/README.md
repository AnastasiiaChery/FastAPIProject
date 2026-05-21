# devflow

Automated workflow: Jira ticket → plan → implementation → tests → **your review** → self-review → PR.

## Prerequisites

| Tool | Install |
|------|---------|
| [Claude Code](https://claude.ai/code) | See link |
| [gh](https://cli.github.com/) | `brew install gh` |
| [jira](https://github.com/ankitpokhrel/jira-cli) | `brew install ankitpokhrel/tap/jira-cli` |

## Setup (once per machine)

```bash
./devflow/setup.sh
source ~/.zshrc
```

The wizard will ask for:
- GitHub login (opens browser)
- Jira server URL (e.g. `https://mycompany.atlassian.net`)
- Jira email
- Jira API token (create at https://id.atlassian.com/manage-api-tokens)

## Usage

Open Claude Code in your project, then:

```
/devflow TICKET-123
```

Claude will automatically:
1. Read the Jira ticket
2. Create an implementation plan in `docs/plans/`
3. Create a feature branch
4. Implement the feature in Python
5. Write and run pytest tests
6. **Pause — let you review the code**

When you're happy with the implementation:

```
/devflow-submit TICKET-123
```

Claude will self-review the code, commit, push, open a draft PR, and move the Jira ticket to "In Review".

After reviewers add comments to the PR:

```
/devflow-review TICKET-123
```

Claude will fetch the comments, apply fixes, run tests, and mark the PR ready to merge.

After the PR is merged:

```
/devflow-cleanup TICKET-123
```

Claude will delete the feature branch and worktree.

## How it works

```
/devflow TICKET-123
    │
    ├── jira CLI       → reads ticket requirements
    ├── git worktree   → creates isolated feature branch
    ├── Claude         → implements code + tests
    └── PAUSE          → you review the code

/devflow-submit TICKET-123
    │
    ├── Claude         → self-reviews the diff
    ├── git + gh CLI   → commits, pushes, opens draft PR
    └── jira CLI       → moves ticket to "In Review"

/devflow-review TICKET-123
    │
    ├── gh CLI         → fetches PR comments
    ├── Claude         → applies fixes, re-runs tests
    └── gh CLI         → marks PR ready to merge

/devflow-cleanup TICKET-123
    │
    ├── git            → removes worktree
    └── git + gh CLI   → deletes local and remote branch
```

## Example run

### `/devflow SCRUM-42`

```
MODE: Story
Skipping phases: none

⚡ DECISION: storage approach
   Option A: list with linear scan → rejected (O(n) lookup/delete)
   Option B: dict[int, Item] → chosen (O(1) lookup/delete, simpler code)

============================================================
IMPLEMENTATION COMPLETE — READY FOR YOUR REVIEW

Branch: feature/SCRUM-42-add-items-api
Worktree: ../MyProject-SCRUM-42

What was automated:
  ✅ Fetched and analyzed ticket (Story, 3 SP)
  ✅ Checked dependencies — no blockers
  ✅ Created implementation plan (6 steps)
  ✅ Implemented in 2 files, +89 / -0 lines
  ⚡ Made 1 decision (see above)
  ✅ Written 8 unit tests — all pass

Time saved: ~1.5–2h of routine work

Next steps:
  1. Review the code in the worktree
  2. When ready to create the PR, run:
     /devflow-submit SCRUM-42
============================================================
```

### `/devflow-submit SCRUM-42`

```
🔍 REVIEW: app/items.py:34 — variable name `d` is not descriptive
   Fix: renamed to `item_data`

============================================================
PR CREATED — AWAITING REVIEW

Draft PR: https://github.com/org/repo/pull/17

What was automated:
  ✅ Self review — 1 issue found and fixed
  ✅ Committed and pushed branch
  ✅ Draft PR created
  ✅ Jira ticket moved to "In Review" + PR link added

Next steps:
  1. Share the PR link with your reviewer
  2. When review comments arrive, run:
     /devflow-review SCRUM-42
============================================================
```

### `/devflow-review SCRUM-42`

```
📋 COMMENT SUMMARY (3 total)
   Trivial:      1
   Substantive:  1
   Conflicting:  0
   Questionable: 1 — will push back

============================================================
REVIEW FIXES COMPLETE

PR is now ready for merge: https://github.com/org/repo/pull/17

Comments processed: 3 total
  ✅ Applied (2): renamed variable in items.py; added missing 404 test
  ⚡ Pushed back (1): suggested removing input validation — would break AC item 3

Files changed: 2 files, +12 / -3 lines
Tests: all pass
============================================================
```

### `/devflow-cleanup SCRUM-42`

```
============================================================
DEVFLOW CLEANUP COMPLETE

Ticket:  SCRUM-42
Branch:  feature/SCRUM-42-add-items-api
PR:      https://github.com/org/repo/pull/17 (merged)

Cleaned up:
  ✅ Worktree removed: ../MyProject-SCRUM-42
  ✅ Local branch deleted
  ✅ Remote branch deleted
  ✅ Remote tracking refs pruned
============================================================
```

## Re-run setup

To update credentials or switch Jira projects:

```bash
./devflow/setup.sh
```

The script will ask before overwriting any existing config.
