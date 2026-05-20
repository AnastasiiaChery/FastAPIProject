# devflow — Demo Script

**Duration:** 5–7 minutes  
**What the audience sees:** one Jira ticket becomes a reviewed, ready-to-merge PR — live, with zero manual steps

---

## Before You Start

- [ ] Claude Code open in this project
- [ ] A real Jira ticket ready (Story or Bug works best for demo — has visible requirements)
- [ ] Terminal visible, browser with Jira and GitHub tabs open in background
- [ ] `git status` is clean, you're on `main`

---

## The Script

### 1. Set the scene (30 seconds)

> "This is a real Jira ticket from our backlog. Normally, turning this into a PR takes a senior developer 2–3 hours: reading the ticket, planning the implementation, writing the code, writing tests, reviewing the diff, writing the PR description. We're going to do it in under 5 minutes. One command."

### 2. Run devflow (live, ~3–4 minutes)

Type in Claude Code:
```
/devflow SCRUM-<your ticket>
```

Let it run. While it's running, narrate what's happening:

- **Phase 1:** "It's reading the Jira ticket right now — extracting requirements, acceptance criteria, checking if there are any blocked dependencies"
- **Phase 2:** "Now it's writing an implementation plan — not jumping straight to code, it's thinking first"
- **Phase 3:** "Creating an isolated git branch so nothing touches main"
- **Phase 4:** "Implementing. Watch for the decision points — when it hits a fork in the road, it logs its reasoning out loud"
- **Phase 5:** "Writing tests. Not after — as part of the flow"
- **Phase 6:** "Self-review. It's reading its own diff as if it's a different person"
- **Phase 7:** "Opening the draft PR"

### 3. Show the PR (30 seconds)

Open the GitHub PR that was just created. Point out:

- **Summary** — derived from actual changed files, not a generic template
- **Decisions section** — "Here's where it explains why it made specific choices"
- **Risk section** — only present if something worth flagging was found

> "A senior developer would be proud to send this PR. It took 4 minutes."

### 4. Show the review flow (optional, 1 minute)

Add one comment on the PR (inline or general). Then run:
```
/devflow-review SCRUM-<your ticket>
```

> "Now it reads our comment, decides whether it agrees, applies the fix — or pushes back if the comment is wrong — runs tests again, and marks the PR ready."

### 5. Close (20 seconds)

Point to the final summary Claude printed:

> "Time saved: ~2.5 hours. That's per ticket, per developer, every sprint. This is what 'code less, AI more' looks like in a real engineering team."

---

## If Something Goes Wrong

| Problem | Recovery |
|---------|----------|
| Jira ticket not found | Have a backup ticket ID ready |
| Tests fail during demo | Let it run — devflow fixes failures automatically, that's part of the story |
| Decision point doesn't trigger | Mention it verbally: "On more complex tickets this is where it logs its reasoning" |
| PR creation fails (no GitHub auth) | Run `gh auth login` before the demo |

---

## Key Messages (for Q&A)

- **"Is this just ChatGPT?"** — No. It's Claude Code with structured workflow commands that use real CLI tools: jira-cli, gh, git. It reads your actual codebase, not a description of it.
- **"What if the code is wrong?"** — That's why it opens a draft PR, not a direct merge. A human reviews. The AI handles the routine; the human handles the judgment.
- **"How long did it take to build this?"** — The workflow is defined in markdown. Setup takes under an hour. That's the point.
- **"Does it work on any project?"** — Any Python project with a Jira board and GitHub repo. Configure `devflow/config.yml` and run setup.
