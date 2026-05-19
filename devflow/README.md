# devflow

Automated workflow: Jira ticket → plan → implementation → tests → code review → PR.

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
6. Self-review the code
7. Push a draft PR — then **pause and wait for your review**

After you add comments to the draft PR:

```
/devflow-review TICKET-123
```

Claude will fetch your comments, apply fixes, run tests, and mark the PR ready to merge.

## How it works

```
/devflow TICKET-123
    │
    ├── jira CLI       → reads ticket requirements
    ├── git worktree   → creates isolated feature branch
    ├── Claude agents  → implements code + tests
    ├── self-review    → catches issues before you see them
    └── gh CLI         → opens draft PR → PAUSES

/devflow-review TICKET-123
    │
    ├── gh CLI         → fetches your PR comments
    ├── Claude         → applies fixes, re-runs tests
    └── gh CLI         → marks PR ready to merge
```

## Re-run setup

To update credentials or switch Jira projects:

```bash
./devflow/setup.sh
```

The script will ask before overwriting any existing config.
