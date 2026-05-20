# devflow — AI-Powered Developer Workflow

## What is this?

**devflow** turns a Jira ticket number into a merged PR — autonomously.

A developer types one command. Claude reads the ticket, writes a plan, creates a branch, implements the feature, writes tests, reviews its own code, and opens a draft PR. When the human leaves review comments, one more command applies the fixes and marks the PR ready to merge.

**No scripts. No boilerplate. No context switching.** Just Claude Code and three slash commands.

---

## The Problem It Solves

A typical feature ticket involves 6–8 manual steps before a single line of business logic is written:

1. Read the ticket and figure out what it actually means
2. Create a branch with the right naming convention
3. Find relevant existing code to understand patterns
4. Write an implementation plan
5. Implement, then write tests, then run them
6. Self-review the diff before pushing
7. Write a PR description that a reviewer can understand
8. Come back after review, read comments, apply fixes, re-run tests, mark ready

Each step is 10–30 minutes of routine work. devflow automates all of it.

---

## Three Commands, Full Lifecycle

```
/devflow SCRUM-42          # ticket → draft PR (autonomous)
/devflow-review SCRUM-42   # review comments → ready PR (autonomous)
/devflow-cleanup SCRUM-42  # merged PR → clean local state
```

---

## What Makes It Smart

### AI Doesn't Just Execute — It Decides

At every meaningful decision point, devflow logs its reasoning:

```
⚡ DECISION: Found two approaches for caching user data
   Option A: in-memory dict → rejected (not thread-safe under uvicorn workers)
   Option B: Redis with TTL  → chosen (matches existing pattern in auth module)
```

Decisions surface in the PR body under `## Decisions` — reviewers see not just *what* changed but *why*.

### It Checks Dependencies Before Starting

```
⚠️  BLOCKED: SCRUM-42 depends on SCRUM-38 ("Add user model") which is still IN PROGRESS
```

If a blocker ticket isn't done, devflow stops and explains — instead of silently building on a broken foundation.

### It Pushes Back on Bad Review Comments

When a reviewer's suggestion would make the code worse, devflow doesn't silently comply:

```
⚡ DECISION: Not applying comment by reviewer on auth.py:42
   Comment: "use a global variable here for simplicity"
   Reason: global state breaks concurrent request handling
   Instead: kept the dependency-injected approach
```

The pushback is posted as a reply directly on the PR comment.

### PR Body Is Generated, Not Templated

Summary bullets come from `git diff --name-only`, not generic phrases. Risk and Decisions sections only appear if there's something to say.

### Every Run Ends With a Real Summary

```
What was automated:
  ✅ Fetched and analyzed ticket (Story, 3 SP)
  ✅ Checked dependencies — no blockers
  ✅ Created implementation plan (6 steps)
  ✅ Implemented in 3 files, +89 / -4 lines
  ⚡ Made 2 decisions (see PR body)
  ✅ Written 5 unit tests — all pass
  ✅ Self code review — 1 issue found and fixed

Time saved: ~2.5–3h of routine work
```

---

## Why This Is Different From Copilot or ChatGPT

Most AI coding tools are **autocomplete at the line level** — they help you write code faster, but you still manage the entire workflow yourself.

devflow operates at the **workflow level**:

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

The difference: Copilot augments a developer. devflow **replaces the routine parts of a developer's day** while keeping the human in control of the decisions that matter.

---

## Time Savings: The Breakdown

"Saves 2–3 hours per ticket" is not a guess. Here is the per-step accounting:

| Step | Manual time | devflow |
|------|-------------|---------|
| Read ticket + extract requirements | 15 min | 0 (automated) |
| Check blocker dependencies | 10 min | 0 (automated) |
| Write implementation plan | 30 min | 0 (automated) |
| Find existing code patterns to follow | 20 min | 0 (automated) |
| Create branch with correct naming | 5 min | 0 (automated) |
| Implement feature | varies | varies (AI-assisted) |
| Write unit tests | 30 min | 0 (automated) |
| Run tests + fix failures | 15 min | 0 (automated) |
| Self-review diff before pushing | 20 min | 0 (automated) |
| Write PR description | 15 min | 0 (automated) |
| Read review comments + apply fixes | 30 min | 0 (automated) |
| Re-run tests after fixes | 10 min | 0 (automated) |
| Delete branches after merge | 5 min | 0 (automated) |
| **Total routine overhead** | **~3h 25min** | **~0** |

Implementation time itself is not in the table — that varies by ticket and AI still needs human oversight. Everything else is eliminated.

---

## Example: Full Run Output

A real `/devflow` run on a 3-point Story ticket looks like this:

**Console output during run:**

```
MODE: Story
Skipping phases: none

📋 Ticket: SCRUM-42 — Add rate limiting to /api/users endpoint (3 SP)
   Dependencies: none blocked

⚡ DECISION: Two approaches for rate limiting
   Option A: in-process dict with TTL → rejected (resets on worker restart, breaks under multiple uvicorn workers)
   Option B: slowapi library (wraps starlette) → chosen (matches existing middleware pattern, battle-tested)

⚡ DECISION: Where to apply the limiter
   Option A: per-route decorator → chosen (explicit, testable in isolation)
   Option B: global middleware → rejected (too broad, would break health check endpoint)
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

## Setup

```bash
./devflow/setup.sh   # one-time wizard: GitHub + Jira credentials
```

Requires: Claude Code, `gh`, `jira-cli`.

---

## Project Configuration

[devflow/config.yml](devflow/config.yml) — Jira project key, branch strategy, test framework. Commit it with the repo so the whole team shares the same setup.
