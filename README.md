# devflow — AI-Powered Developer Workflow

> **One command. Jira ticket → reviewed, ready-to-merge PR.**

devflow turns a Jira ticket into a draft PR — autonomously. A developer types one command. Claude reads the ticket, writes a plan, creates a branch, implements the feature, writes tests, reviews its own code, and opens a draft PR.

**No scripts. No boilerplate. No context switching.**

---

## Commands

```bash
/devflow SCRUM-42          # ticket → plan → implementation + tests (pauses for your review)
/devflow-review SCRUM-42   # self-review → push → draft PR → Jira "In Review"
/devflow-resume            # restore context from last saved session
/devflow-status            # dashboard of all active worktrees, Jira statuses, and PRs
```

---

## How It Works

```
/devflow SCRUM-42
    │
    ├── jira skill       →  fetches ticket, checks blocked dependencies
    ├── planner agent    →  writes implementation plan
    ├── git worktree     →  creates isolated feature branch
    ├── implementer agent →  implements code step-by-step, logs decisions
    ├── test-writer agent →  writes pytest tests for new logic
    ├── code-reviewer agent → self-reviews diff (BLOCKER/MAJOR/MINOR/NIT)
    └── PAUSE            →  you review the code

/devflow-review SCRUM-42
    │
    ├── code-reviewer agent → self-reviews the diff
    ├── github skill     →  pushes branch, opens draft PR
    └── jira skill       →  moves ticket to "In Review", adds PR link

/devflow-resume
    └── reads .devflow-state.json → checks worktree + Jira + PR → prints "you are here"

/devflow-status
    └── lists all feature/* and spike/* worktrees → fetches Jira + PR status per ticket
```

---

## What Makes It Smart

### Specialist agents for each phase

devflow delegates work to purpose-built agents rather than doing everything in one prompt:

| Agent | Role |
|-------|------|
| `planner` | Reads the codebase, finds reference implementations, produces a concrete step-by-step plan |
| `implementer` | Executes each step, runs tests between steps, logs `⚡ DECISION` entries |
| `test-writer` | Writes tests that cover happy path, edge cases, and error cases — 80%+ coverage |
| `code-reviewer` | Reviews diffs with BLOCKER / MAJOR / MINOR / NIT severity |
| `implementation-reviewer` | Audits workflow completion metrics before PR submission |

### Hooks that enforce devflow rules automatically

| Hook | When | What it does |
|------|------|-------------|
| `guard-main-branch` | Before every `git push/commit` | Blocks direct commits to protected branches |
| `guard-git-add` | Before every `git add` | Blocks `git add .` / `-A` and explicit staging of `.env*`, `*.pem`, `*secret*`, `*.key` |
| `guard-env-read` | Before every file read | Blocks reading `.env` files |
| `lint-on-write` | After every `.py` write/edit | Auto-runs `ruff check --fix` + `ruff format` |
| `save-session` | On session stop | Saves active ticket state for resuming later |

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

### Ticket-type-aware workflow

| Ticket type | Plan | Branch | Implement | Tests | Submit |
|-------------|------|--------|-----------|-------|--------|
| Story / Feature | ✅ implementation plan | ✅ | ✅ | ✅ | → `/devflow-review` |
| Bug | ✅ root cause analysis | ✅ | ✅ | ✅ if logic changed | → `/devflow-review` |
| Task / Chore | ✅ brief | ✅ | ✅ | ⚪ only if logic changed | → `/devflow-review` |
| Spike | ✅ findings doc → `docs/investigations/` | ❌ | ❌ | ❌ | → `/devflow-review` |

---

## Example: Full Run Output

**Console during `/devflow`:**

```
MODE: Story
Skipping phases: none

📋 Ticket: SCRUM-42 — Add rate limiting to /api/users endpoint (3 SP)
   Dependencies: none blocked

⚡ DECISION: Two approaches for rate limiting
   Option A: in-process dict with TTL → rejected (not thread-safe under uvicorn workers)
   Option B: slowapi library           → chosen (matches existing middleware pattern)
```

**PAUSE summary:**

```
============================================================
IMPLEMENTATION COMPLETE — READY FOR YOUR REVIEW

Branch:   feature/SCRUM-42-rate-limiting
Worktree: ../repo-SCRUM-42

What was automated:
  ✅ Fetched ticket (Story, 3 SP)
  ✅ No blockers
  ✅ Implementation plan (5 steps)
  ✅ Jira → "In Progress", assigned to you
  ✅ Implemented 3 files, +67/-2 lines
  ⚡ 2 decisions
  ✅ 4 tests written — all pass

Time saved: ~2–2.5h

Next steps:
  1. Review the code in the worktree
  2. When ready to create the PR, run:
     /devflow-review SCRUM-42
============================================================
```

**After `/devflow-review`:**

```
============================================================
PR CREATED — AWAITING REVIEW

Draft PR: https://github.com/org/repo/pull/87

What was automated:
  ✅ Self review — no blockers found
  ✅ Pushed branch to origin
  ✅ Draft PR created
  ✅ Jira → "In Review" + PR link added

Next steps:
  1. Share the PR link with your reviewer
  2. Address review comments in this session or start a new one
============================================================
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
- [ ] All unit tests pass
- [ ] Acceptance criteria from ticket verified
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
| **Total routine overhead** | **~2h 40min** | **~0** |

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
| Enforces git safety via hooks | ❌ | ❌ | ✅ |
| Auto-lints on every file write | ❌ | ❌ | ✅ |

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
  in_review_status: "In Review"

github:
  default_branch: main
  draft_pr: true

code:
  language: python
  test_framework: pytest

hooks:
  enabled: true
  lint_on_write: true
  guard_main_branch: true
  guard_git_add: true
```

---

## Project Structure

```
.claude/
  agents/
    planner.md              # turns tickets into concrete plans
    implementer.md          # executes plans step-by-step
    test-writer.md          # writes pytest tests (80%+ coverage)
    code-reviewer.md        # reviews diffs with BLOCKER/MAJOR/MINOR/NIT
    implementation-reviewer.md  # audits completion before PR
  commands/
    devflow.md              # /devflow — ticket → implementation + tests
    devflow-review.md       # /devflow-review — self-review → draft PR
    devflow-resume.md       # /devflow-resume — restore context from saved session
    devflow-status.md       # /devflow-status — dashboard of all active worktrees
  hooks/
    guard-main-branch.sh    # blocks commits to protected branches
    guard-git-add.sh        # blocks git add . / -A
    guard-env-read.sh       # blocks reading .env files
    lint-on-write.sh        # auto-lints .py files on write/edit
    save-session.sh         # saves state on session stop
    hooks.json              # hook configuration
  rules/
    python-backend.md       # Python standards (security, testing, style)
    dockerfile.md           # Dockerfile conventions
    yaml.md                 # YAML conventions
  skills/
    jira/SKILL.md           # Jira CLI operations
    github/SKILL.md         # gh CLI operations
    documentation/SKILL.md  # doc creation and updates
devflow/
  setup.sh                  # one-time credential wizard
  config.yml                # project-level configuration
docs/
  plans/                    # implementation plans (Story, Bug, Task)
  investigations/           # findings documents (Spike tickets)
```
