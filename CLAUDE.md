# devflow — project context for Claude

devflow automates the full developer workflow: Jira ticket → implementation plan → feature branch → code + tests → self-review → draft PR → review fixes → merge-ready PR.

## Commands

| Command | What it does |
|---------|-------------|
| `/devflow TICKET-ID` | Fetches ticket, plans, implements, tests — stops for your review |
| `/devflow-submit TICKET-ID` | Self-reviews code, commits, pushes, opens draft PR, moves Jira to "In Review" |
| `/devflow-review TICKET-ID` | Reads PR comments, applies fixes or pushes back, marks PR ready |
| `/devflow-cleanup TICKET-ID` | Deletes feature branch and worktree after merge |

Commands are defined in `.claude/commands/`. Each command is self-contained — read it before running to understand the phases.

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
