# devflow — project context for Claude

devflow automates the full developer workflow: Jira ticket → implementation plan → feature branch → code + tests → self-review → draft PR.

## Commands

| Command | What it does |
|---------|-------------|
| `/devflow TICKET-ID` | Fetches ticket, plans, implements, tests, self-reviews — stops for your review |
| `/devflow-review TICKET-ID` | Self-reviews code, pushes, opens draft PR, moves Jira to "In Review" |
| `/devflow-resume` | Restores context from last saved session — shows where you left off and what to do next |
| `/devflow-status` | Dashboard of all active worktrees, Jira statuses, and PR links |

Commands are defined in `.claude/commands/`. Each command is self-contained — read it before running to understand the phases.

## Agents

| Agent | Role |
|-------|------|
| `planner` | Turns a Jira ticket into a concrete implementation plan |
| `implementer` | Executes the plan step-by-step, tracks decisions |
| `test-writer` | Writes thorough pytest tests for new logic |
| `code-reviewer` | Reviews diffs with BLOCKER/MAJOR/MINOR severity |
| `implementation-reviewer` | Audits workflow completion before PR submission |

Agents are defined in `.claude/agents/`. Commands delegate to agents automatically.

## Skills

| Skill | Purpose |
|-------|---------|
| `jira` | All Jira CLI operations (view, move, comment) |
| `github` | All gh CLI operations (push, PR create, review comments) |
| `documentation` | Create/update docs after implementation |

Skills are defined in `.claude/skills/`.

## Hooks

Active hooks enforce devflow rules automatically:

| Hook | Trigger | What it does |
|------|---------|--------------|
| `guard-main-branch` | Before Bash (git push/commit) | Blocks commits/pushes to main |
| `guard-git-add` | Before Bash (git add) | Blocks `git add .` / `git add -A` and explicit staging of `.env*`, `*.pem`, `*secret*`, `*.key` |
| `guard-env-read` | Before Read | Blocks reading `.env` files |
| `lint-on-write` | After Write/Edit on `.py` | Auto-runs ruff check + format |
| `save-session` | On Stop | Saves active ticket state to `.devflow-state.json` |

See `.claude/hooks/hooks.json` for hook configuration.

## Project config

`devflow/config.yml` controls Jira project key, default branch, and test framework. Read it at the start of any devflow run.

## Conventions

- Language: Python
- Tests: pytest in `tests/`
- Plans: saved to `docs/plans/YYYYMMDD-TICKET-plan.md`
- Spike findings: saved to `docs/investigations/YYYYMMDD-TICKET.md`
- Branch naming: `feature/TICKET-ID-short-slug`
- PRs: always draft first, never push directly to main
- Commit messages: short, no co-author lines
