---
name: jira
description: "Interact with Jira using the CLI. Use when users mention ticket IDs, ask to list/search issues, or want to view/update/comment on tickets."
---

# Jira CLI Skill

Use the `jira` CLI for all Jira operations. Do NOT use MCP or direct API calls.

## When to Use

- User mentions a ticket ID (e.g., "PROJ-123", "look at ABC-456")
- User asks to list, search, or find issues
- User wants to view, update, comment, or transition a ticket
- User asks about sprints, boards, or projects

## Invocation Examples

- "Show me ticket API-123" → `jira issue view API-123`
- "What are my open tickets?" → `jira issue list -a$(jira me) -s"To Do,In Progress"`
- "Find bugs in the API project" → `jira issue list -p API -tBug`
- "What did I work on this week?" → `jira issue list -a$(jira me) --updated week`
- "Add a comment to CORE-456" → `jira issue comment add CORE-456 "..."`

## Natural Language → JQL Translation

| User Says | Flags / JQL |
|-----------|-------------|
| "my tickets" | `-a$(jira me)` |
| "my open tickets" | `-a$(jira me) -s"To Do,In Progress"` |
| "high priority bugs" | `-tBug -yHigh` |
| "created this week" | `--created week` |
| "updated today" | `--updated today` |
| "tickets with label X" | `-l X` |
| "search for 'auth'" | `-q "summary ~ auth OR description ~ auth"` |

## Common Commands

| Task | Command |
|------|---------|
| View ticket | `jira issue view PROJ-123` |
| View with comments | `jira issue view PROJ-123 --comments 5` |
| My issues | `jira issue list -a$(jira me)` |
| List with filters | `jira issue list -p PROJECT -s"In Progress" -yHigh` |
| Raw JQL | `jira issue list -q "project = PROJ AND status != Done"` |
| Open in browser | `jira open PROJ-123` |
| Add comment | `jira issue comment add PROJ-123 "Comment text"` |
| Transition | `jira issue move PROJ-123 "In Review"` |
| Assign to self | `jira issue assign PROJ-123 $(jira me)` |
| Current sprint | `jira sprint list --current` |

## Output Formats

- `--plain` - Simple text for piping/scripting
- `--csv` - Export to CSV
- `--raw` - Raw JSON

## Tips

- Use `--no-input` to skip interactive prompts when you have all info
- Verify with `jira issue view` before editing/transitioning
- Interactive mode: `v`=view, `m`=move, `Enter`=browser, `c`=copy URL

## Troubleshooting

### "invalid issue types in config" error

If you get this error when creating issues, your config is missing issue types. Manually add issue types to `~/.config/.jira/.config.yml`:

```yaml
issue:
  types:
    - id: "10002"
      name: Task
      handle: task
      subtask: false
```
