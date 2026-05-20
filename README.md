# devflow — AI-Powered Developer Workflow

> **One command. Jira ticket → reviewed, ready-to-merge PR.**

devflow turns a Jira ticket into a merged PR — autonomously. A developer types one command. Claude reads the ticket, writes a plan, creates a branch, implements the feature, writes tests, reviews its own code, and opens a draft PR. When the human leaves review comments, one more command applies the fixes and marks the PR ready to merge.

**No scripts. No boilerplate. No context switching.**

---

## Three Commands, Full Lifecycle

```bash
/devflow SCRUM-42          # ticket → draft PR
/devflow-review SCRUM-42   # review comments → ready PR
/devflow-cleanup SCRUM-42  # merged PR → clean local state
```

---

## How It Works

```
/devflow SCRUM-42
    │
    ├── jira CLI        →  reads ticket, checks blocked dependencies
    ├── Claude          →  writes implementation plan
    ├── git worktree    →  creates isolated feature branch
    ├── Claude agents   →  implements code + writes tests
    ├── Claude          →  self-reviews the diff
    └── gh CLI          →  opens draft PR  ──►  PAUSES for human review

/devflow-review SCRUM-42
    │
    ├── gh CLI          →  fetches your PR comments
    ├── Claude          →  applies fixes or pushes back with explanation
    ├── pytest          →  re-runs tests
    └── gh CLI          →  marks PR ready to merge
```

---

## What Makes It Smart

### Dependency checking before starting

```
⚠️  BLOCKED: SCRUM-42 depends on SCRUM-38 ("Add user model") which is still IN PROGRESS
```

If a blocker ticket isn't done, devflow stops and explains — instead of silently building on a broken foundation.

### Decision checkpoints with logged reasoning

During implementation, every meaningful fork in the road is logged explicitly:

```
⚡ DECISION: Two approaches for rate limiting
   Option A: in-process dict with TTL
             → rejected (resets on worker restart, breaks under multiple uvicorn workers)
   Option B: slowapi library (wraps starlette)
             → chosen (matches existing middleware pattern, battle-tested)
```

Decisions surface in the PR body — reviewers see not just *what* changed but *why*.

### Pushback on wrong review comments

When a reviewer's suggestion would make the code worse, devflow doesn't silently comply:

```
⚡ DECISION: Not applying comment by reviewer on auth.py:42
   Comment: "use a global variable here for simplicity"
   Reason: global state breaks concurrent request handling
   Instead: kept the dependency-injected approach
```

The pushback is posted as a reply directly on the PR comment.

### Ticket-type-aware workflow

| Ticket type | Plan | Branch | Implement | Tests | Review | PR |
|-------------|------|--------|-----------|-------|--------|----|
| Story / Feature | ✅ implementation plan | ✅ | ✅ | ✅ | ✅ | ✅ draft |
| Bug | ✅ root cause analysis | ✅ | ✅ | ✅ if logic changed | ✅ | ✅ draft |
| Task / Chore | ✅ brief | ✅ | ✅ | ⚪ only if logic changed | ✅ | ✅ draft |
| Spike | ✅ findings doc | ❌ | ❌ | ❌ | ❌ | ✅ with findings |

---

## Example: Full Run Output

**Console during run:**

```
MODE: Story
Skipping phases: none

📋 Ticket: SCRUM-42 — Add rate limiting to /api/users endpoint (3 SP)
   Dependencies: none blocked

⚡ DECISION: Two approaches for rate limiting
   Option A: in-process dict with TTL → rejected (not thread-safe under uvicorn workers)
   Option B: slowapi library           → chosen (matches existing middleware pattern)

⚡ DECISION: Where to apply the limiter
   Option A: per-route decorator → chosen (explicit, testable in isolation)
   Option B: global middleware   → rejected (would throttle /health used by load balancer)
```

**Generated PR body:**

```markdown
## Jira Ticket
[SCRUM-42](https://company.atlassian.net/browse/SCRUM-42)

## Summary
- Added rate limiting to `POST /api/users` using `slowapi` (100 req/min per IP)
- Registered `RateLimitExceeded` handler in `app.py`
- Added 3 integration tests covering limit enforcement and reset behaviour

## Decisions
- **slowapi over in-process dict**: in-process state resets on worker restart and breaks
  under multiple uvicorn workers. slowapi integrates cleanly with existing starlette middleware.
- **Per-route decorator over global middleware**: global rate limiting would incorrectly
  throttle the `/health` endpoint used by the load balancer.

## Test plan
- [x] All unit tests pass (`python -m pytest tests/ -v`)
- [x] Acceptance criteria from ticket verified
```

**Final summary:**

```
============================================================
DEVFLOW COMPLETE — AWAITING YOUR REVIEW

Draft PR: https://github.com/org/repo/pull/87

What was automated:
  ✅ Fetched and analyzed ticket (Story, 3 SP)
  ✅ Checked dependencies — no blockers
  ✅ Created implementation plan (5 steps)
  ✅ Implemented in 3 files, +67 / -2 lines
  ⚡ Made 2 decisions (see PR body)
  ✅ Written 4 unit tests — all pass
  ✅ Self code review — 1 issue found and fixed

Time saved: ~2.5–3h of routine work

Next steps:
  1. Open the PR and add review comments
  2. When ready, run: /devflow-review SCRUM-42
============================================================
```

---

## Time Savings: The Breakdown

| Step | Manual time | devflow |
|------|-------------|---------|
| Read ticket + extract requirements | 15 min | automated |
| Check blocker dependencies | 10 min | automated |
| Write implementation plan | 30 min | automated |
| Find existing code patterns to follow | 20 min | automated |
| Create branch with correct naming | 5 min | automated |
| Write unit tests | 30 min | automated |
| Run tests + fix failures | 15 min | automated |
| Self-review diff before pushing | 20 min | automated |
| Write PR description | 15 min | automated |
| Read review comments + apply fixes | 30 min | automated |
| Re-run tests after fixes | 10 min | automated |
| Delete branches after merge | 5 min | automated |
| **Total routine overhead** | **~3h 25min** | **~0** |

---

## Why This Is Different From Copilot or ChatGPT

| Capability | GitHub Copilot | ChatGPT | devflow |
|---|---|---|---|
| Writes code | ✅ | ✅ | ✅ |
| Reads your Jira ticket | ❌ | ❌ | ✅ |
| Checks ticket dependencies | ❌ | ❌ | ✅ |
| Creates isolated git branch | ❌ | ❌ | ✅ |
| Writes and runs tests | ❌ | ❌ | ✅ |
| Self-reviews its own diff | ❌ | ❌ | ✅ |
| Opens a draft PR | ❌ | ❌ | ✅ |
| Logs reasoning at decision points | ❌ | ❌ | ✅ |
| Reads PR comments and applies fixes | ❌ | ❌ | ✅ |
| Pushes back on wrong review comments | ❌ | ❌ | ✅ |
| Cleans up branches after merge | ❌ | ❌ | ✅ |

---

## Setup

### Prerequisites

| Tool | Install |
|------|---------|
| [Claude Code](https://claude.ai/code) | See link |
| [gh](https://cli.github.com/) | `brew install gh` |
| [jira-cli](https://github.com/ankitpokhrel/jira-cli) | `brew install ankitpokhrel/tap/jira-cli` |

### One-time setup

```bash
./devflow/setup.sh
source ~/.zshrc
```

The wizard configures GitHub and Jira credentials, verifies the connection, and prepares the environment.

### Project config

[devflow/config.yml](devflow/config.yml) — set your Jira project key, branch strategy, and test framework. Commit it so the whole team shares the same setup.

```yaml
jira:
  project: SCRUM
  server: https://yourcompany.atlassian.net

github:
  default_branch: main
  draft_pr: true

code:
  language: python
  test_framework: pytest
```

---

## Project Structure

```
.claude/
  commands/
    devflow.md          # /devflow — ticket → draft PR
    devflow-review.md   # /devflow-review — review comments → ready PR
    devflow-cleanup.md  # /devflow-cleanup — merged PR → clean state
devflow/
  setup.sh              # one-time credential wizard
  config.yml            # project-level configuration
  README.md             # quick reference
  DEMO.md               # demo script for presentations
```
