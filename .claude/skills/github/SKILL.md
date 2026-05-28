---
name: github
description: "Use for all GitHub operations: creating PRs, fetching review comments, marking PRs ready, listing open PRs, resolving repo slugs. Trigger phrases: 'open a PR', 'fetch review comments', 'mark PR ready', 'find the PR for TICKET-ID', 'push and create PR'. Use the gh CLI for all operations. Do NOT use for Jira operations — use the jira skill for those."
---

# GitHub CLI Skill

Use the `gh` CLI for all GitHub operations. Do NOT use the GitHub API directly
or MCP unless the `gh` CLI is unavailable.

## Pre-flight check

Before any operation, verify `gh` is authenticated:

```bash
gh auth status
```

If not authenticated, stop and print: `Run: gh auth login`

## Common operations

### Find PR for a ticket

```bash
gh pr list --state open --search "TICKET-ID" --json number,title,url,headRefName
```

### Push branch to remote

Always push before creating a PR. Never assume the branch exists on remote.

```bash
git push -u origin HEAD
```

### Create a draft PR from a body file

```bash
gh pr create --draft \
  --title "TICKET-ID: <exact ticket title>" \
  --body-file /tmp/pr-body-TICKET-ID.md
```

### Mark PR ready for review

```bash
gh pr ready <PR_NUMBER>
```

### Fetch inline review comments

```bash
REPO=$(gh repo view --json nameWithOwner -q '.nameWithOwner')
gh api repos/$REPO/pulls/<PR_NUMBER>/comments \
  --jq '[.[] | {id: .id, path: .path, line: .line, body: .body}]'
```

### Fetch general PR comments

```bash
gh api repos/$REPO/issues/<PR_NUMBER>/comments \
  --jq '[.[] | {id: .id, body: .body}]'
```

### Reply to a review comment

```bash
gh api repos/$REPO/pulls/<PR_NUMBER>/comments/<COMMENT_ID>/replies \
  -f body="<reply text>"
```

### Check for uncommitted changes

```bash
git status --porcelain
```

If output is non-empty, stop and tell the user to commit or stash before proceeding.

## Safety rules

- Never push directly to `main` — always push to a feature branch
- Always verify the repo slug with `gh repo view` before API calls
- Never create a ready (non-draft) PR without running the full test suite first
- If `gh` is not authenticated, stop and print: `Run: gh auth login`
