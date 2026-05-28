---
name: jira
description: "Use when any Jira operation is needed: fetching ticket details, checking blocker status, transitioning ticket status, adding PR links as comments. Trigger phrases: 'fetch the ticket', 'check if blockers are done', 'move ticket to In Review', 'add PR link to Jira', 'get details for TICKET-ID'. Use the jira CLI for all operations. Do NOT use for GitHub operations — use the github skill for those."
---

# Jira CLI Skill

Use the `jira` CLI for all Jira operations. Do NOT use the Jira API directly
or MCP unless the `jira` CLI is unavailable.

## Pre-flight check

Before any operation, verify `jira` is authenticated:

```bash
jira me
```

If not authenticated, stop and print: `Run: jira init`

## Common operations

### Fetch ticket details

```bash
jira issue view TICKET-ID
```

### Check if a dependency ticket is done

```bash
jira issue view TICKET-ID --plain | grep -E "^Status:"
```

Proceed only if status is `Done` or `Closed`. If blocked, stop and report:
`⛔ BLOCKED: TICKET-ID is not Done (status: <status>). Cannot proceed.`

### Transition ticket status

```bash
jira issue move TICKET-ID "STATUS"
```

Use the exact status name from `config.yml` (`jira.in_review_status`).
Never hardcode the status string.

### Add a comment (e.g. PR link)

```bash
jira issue comment add TICKET-ID \
  --body "PR opened: <PR_URL>"
```

### List issues in project

```bash
jira issue list \
  --project PROJECT-KEY \
  --status "In Progress"
```

### Search with JQL

```bash
jira issue list --jql "project = SCRUM AND status = 'To Do' AND assignee = currentUser()"
```

## Ordering rule

When both Jira and GitHub actions are needed in the same phase, always complete the
GitHub action first, then transition the Jira ticket. Never transition before the PR exists.

## Safety rules

- Never transition a Jira ticket before the corresponding GitHub action succeeds
- Always read the status name from `config.yml` — never hardcode it
- Never close or archive a ticket — only move to the status defined in config
- If `jira` is not authenticated, stop and print: `Run: jira init`
