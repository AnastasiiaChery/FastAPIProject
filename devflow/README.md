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

## Re-run setup

To update credentials or switch Jira projects:

```bash
./devflow/setup.sh
```

The script will ask before overwriting any existing config.
