---
name: documentation
description: "Use after implementing features to create or update documentation. Trigger phrases: 'document this feature', 'update the docs', 'write documentation for TICKET-ID', 'Phase 6 of devflow', 'create API docs'. Ensures documentation is synchronized with code changes following project conventions."
---

# Documentation Skill

Use this skill after features are implemented to create or update project documentation.
This ensures documentation stays synchronized with code changes.

## When to Use This Skill

Invoke this skill:
- After implementing a feature (following the implementer agent)
- After completing implementation review (following implementation-reviewer agent)
- Before creating a PR when documentation changes are needed
- When user explicitly requests documentation updates

**Do NOT use this skill for:**
- Writing code comments (those go in the code itself)
- Writing implementation plans (that's the planner agent's job)
- Writing test documentation (that's inline with tests)

---

## Documentation Structure (from CLAUDE.md)

```
repo/
├── README.md                    # Project overview (one per repo, in root)
└── docs/
    ├── architecture.md          # System design, component diagrams
    ├── changelogs/              # Version history
    │   └── YYYY-MM-DD.md
    ├── guides/                  # Tutorials and how-tos (if needed)
    │   └── feature-guide.md
    └── plans/                   # Implementation plans (created by planner agent)
        └── YYYYMMDD-TICKET-plan.md
```

**ADRs (Architecture Decision Records)** are tracked in Jira, not in the repo.

---

## Pre-flight Check

Before writing documentation, gather context:

### 1. Check if implementation plan exists
```bash
fd -t f ".*TICKET-ID.*plan.md" docs/plans/
```

If found, read it to understand:
- What was implemented
- Why it was implemented
- What decisions were made
- What edge cases were handled

### 2. Analyze code changes
```bash
# Get list of changed files
git diff --name-only main...HEAD

# Get summary of changes
git diff --stat main...HEAD

# View actual changes
git diff main...HEAD
```

### 3. Check for decision markers
```bash
rg "⚡ DECISION" --type md
```

### 4. Identify what docs need updates

**Use fd and rg to find existing documentation:**
```bash
# Find all markdown docs
fd -e md . docs/

# Search for references to changed modules/features
rg "module_name|feature_name" docs/
```

---

## Documentation Types & When to Create Them

### README.md Updates

**Update README.md when:**
- New major feature is added
- Installation/setup steps change
- New dependencies are added
- Project scope or purpose changes

**README.md sections typically include:**
- Project overview and purpose
- Installation instructions
- Quick start guide
- Key features list
- Configuration overview
- License and contributing info

**Don't add to README.md:**
- Detailed API documentation (goes in `docs/`)
- Implementation details (goes in `docs/architecture.md`)
- Step-by-step tutorials (goes in `docs/guides/`)

### Architecture Documentation

**Create/update `docs/architecture.md` when:**
- New system components are added
- Data flow changes
- Integration points change
- Architectural patterns are introduced

**Use Mermaid diagrams for:**
```markdown
## System Architecture

### Component Interaction
\`\`\`mermaid
flowchart TB
    A[API Gateway] --> B[Auth Service]
    B --> C[User Service]
    A --> D[Data Service]
    D --> E[(Database)]
\`\`\`

### Data Flow
\`\`\`mermaid
sequenceDiagram
    Client->>API: POST /users
    API->>Validator: validate_input()
    Validator-->>API: Valid
    API->>Database: save_user()
    Database-->>API: user_id
    API-->>Client: 201 Created
\`\`\`

### Data Models
\`\`\`mermaid
classDiagram
    class User {
        +str id
        +str email
        +datetime created_at
        +validate()
        +save()
    }
    class Session {
        +str token
        +User user
        +datetime expires_at
    }
    User "1" --> "*" Session
\`\`\`
```

### Feature Guides

**Create `docs/guides/<feature>-guide.md` when:**
- Feature is complex and needs explanation
- Multiple steps required to use the feature
- Common use cases need examples
- Feature has configuration options

**Structure:**
```markdown
# Feature Name Guide

## Overview
Brief description of what this feature does and why it exists.

## Prerequisites
- What needs to be set up first
- Required configuration

## Basic Usage
Step-by-step instructions with code examples.

## Advanced Usage
Optional advanced patterns and customization.

## Troubleshooting
Common issues and solutions.

## Related Features
Links to other relevant documentation.
```

### API Documentation

**Update API docs when:**
- New endpoints are added
- Request/response formats change
- Authentication methods change
- Error codes change

**Use tables for API reference:**
```markdown
## API Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/users` | Create new user | No |
| GET | `/api/users/{id}` | Get user details | Yes |
| PUT | `/api/users/{id}` | Update user | Yes |

### POST /api/users

Create a new user account.

**Request:**
\`\`\`json
{
  "email": "user@example.com",
  "name": "John Doe"
}
\`\`\`

**Response (201 Created):**
\`\`\`json
{
  "id": "usr_123",
  "email": "user@example.com",
  "name": "John Doe",
  "created_at": "2026-05-22T10:30:00Z"
}
\`\`\`

**Errors:**
- `400 Bad Request` - Invalid email format
- `409 Conflict` - Email already exists
```

### Changelogs

**Create `docs/changelogs/YYYY-MM-DD.md` when:**
- Releasing a new version
- Significant features or fixes are deployed
- Breaking changes are introduced

**Format (Keep What Changed):**
```markdown
# Changelog - 2026-05-22

## TICKET-123: User Authentication

### Added
- JWT-based authentication endpoints
- Password validation with complexity requirements
- Session management with refresh tokens

### Changed
- User model now includes `last_login` timestamp
- API error responses now include error codes

### Fixed
- Race condition in session cleanup
- Memory leak in token validation

### Technical Details
- Implementation: See `docs/plans/20260522-TICKET-123-plan.md`
- Files changed: 8 files, +450/-120 lines
- Tests added: 23 unit tests, all passing
```

---

## Workflow

### Step 1: Gather Context

1. **Read the implementation plan** (if exists):
   ```bash
   fd ".*TICKET-ID.*plan.md" docs/plans/
   ```

2. **Invoke jira skill** to get ticket details:
   ```bash
   jira issue view TICKET-ID
   ```
   Extract: ticket title, description, acceptance criteria

3. **Analyze git changes**:
   ```bash
   git diff --stat main...HEAD
   git diff main...HEAD
   ```

4. **Find decision markers**:
   ```bash
   rg "⚡ DECISION" --type md docs/plans/
   ```

### Step 2: Determine What Docs Need Updates

**Decision matrix:**

| Change Type | Update README | Update Architecture | Create Guide | Update API Docs | Create Changelog |
|-------------|---------------|---------------------|--------------|-----------------|------------------|
| New feature | If major | If affects system | If complex | If adds endpoints | Yes |
| Bug fix | No | No | No | If changes API | Yes |
| Refactoring | No | If pattern changes | No | No | Only if user-visible |
| New endpoint | No | Maybe | No | Yes | Yes |
| Config change | Yes | Maybe | Maybe | No | Yes |

### Step 3: Write Documentation

**For each document type needed:**

1. **Check if document exists:**
   ```bash
   fd "^architecture.md$" docs/
   ```

2. **If exists:** Read it first, then update relevant sections
3. **If new:** Create following the structure templates above

**Documentation style (from CLAUDE.md):**
- Use tables for comparisons, options, and reference data
- Use Mermaid diagrams for flows, sequences, and data models
- Answer: What? Why? How? (in that order)
- Prefer examples over explanations
- One topic per file
- Link between files for navigation

### Step 4: Validate Documentation

**Check documentation quality:**
- [ ] All code examples are syntactically correct
- [ ] All internal links work (use relative paths)
- [ ] Mermaid diagrams render correctly
- [ ] No sensitive information (secrets, credentials, internal IPs)
- [ ] Date format is ISO YYYYMMDD in comments/filenames
- [ ] Follows project's documentation structure

**Test with fd and rg:**
```bash
# Check for broken internal links
rg "\[.*\]\(docs/.*\.md\)" docs/ | while read line; do
  # Extract and verify file exists
  # (implementation detail)
done

# Check for exposed secrets (should return empty)
rg -i "password|secret|api_key|token" docs/ --type md
```

### Step 5: Suggest ADRs for Jira

If implementation decisions were made (found via `⚡ DECISION` markers or in plan file):

**Output format:**
```
📋 Significant decisions were made during implementation:
  1. **Error handling**: Chose custom exceptions over ValueError — provides better context
  2. **Caching strategy**: Chose Redis over in-memory — supports horizontal scaling

Suggest creating an ADR ticket in Jira to document these decisions:
  Title: "ADR: <brief topic summary>"
  Description: Link to the implementation plan and decision details
```

**Do NOT create ADR files in the repo** — they belong in Jira per project conventions.

---

## Integration with Other Skills

### Use jira skill for:
- Getting ticket details: `jira issue view TICKET-ID`
- Checking ticket type (Story/Bug/Task affects documentation depth)
- Getting acceptance criteria (helps validate documentation completeness)

### Use github skill for:
- Finding related PRs: `gh pr list --search "TICKET-ID"`
- Getting PR descriptions (may contain context for docs)

---

## Safety Rules

- **NEVER commit or push** unless user explicitly requests it
- **NEVER expose secrets** in documentation (check with rg before saving)
- **NEVER document internal implementation details** in public-facing docs
- **ALWAYS update related documentation** when functionality changes (per CLAUDE.md)
- **ALWAYS use ISO YYYYMMDD** format for dates in filenames and comments

---

## Examples

### Example 1: After implementing new authentication feature

```bash
# 1. Gather context
fd ".*SCRUM-42.*plan.md" docs/plans/
# Found: docs/plans/20260522-SCRUM-42-plan.md

# Read plan to understand what was implemented
# Implementation added JWT auth with refresh tokens

# 2. Determine docs needed
# - Update README.md (new setup required for JWT secret)
# - Create docs/guides/authentication-guide.md (complex feature)
# - Update docs/architecture.md (new auth flow)
# - Create docs/changelogs/2026-05-22.md

# 3. Write documentation
# ... create/update each file following templates above ...

# 4. Validate
rg -i "secret|password|api_key" docs/ --type md  # Should be empty

# 5. Output
Documentation updated:
  ✅ README.md - Added JWT secret configuration
  ✅ docs/guides/authentication-guide.md - Created new guide
  ✅ docs/architecture.md - Added auth flow diagram
  ✅ docs/changelogs/2026-05-22.md - Created changelog

📋 Decision found: Suggest creating ADR ticket for "JWT vs Session cookies"
```

### Example 2: After bug fix

```bash
# 1. Gather context
jira issue view BUG-123
# Bug fix: Race condition in user registration

# 2. Determine docs needed
# - No README update (internal fix)
# - No architecture update (no design change)
# - Create docs/changelogs/2026-05-22.md (user-visible fix)

# 3. Write changelog only
# ... create changelog documenting the fix ...

Documentation updated:
  ✅ docs/changelogs/2026-05-22.md - Documented race condition fix
```

---

## Output Format

After completing documentation updates, output:

```
============================================================
DOCUMENTATION UPDATED

Ticket: TICKET-ID
Files updated:
  ✅ README.md - <what changed>
  ✅ docs/architecture.md - <what changed>
  ✅ docs/guides/<guide>.md - <created new | updated>
  ✅ docs/changelogs/YYYY-MM-DD.md - <created>

Documentation coverage:
  ✅ Feature overview documented
  ✅ API changes documented
  ✅ Configuration changes documented
  ✅ Architecture diagrams updated
  ⚪ No user guide needed (feature is self-explanatory)

Quality checks:
  ✅ No secrets exposed
  ✅ All links valid
  ✅ Mermaid diagrams render correctly
  ✅ Date format is ISO YYYYMMDD

📋 ADR suggestions:
  - "<decision topic>" - Create Jira ticket to document decision

Next steps:
  1. Review the documentation changes
  2. Include documentation files in your PR commit
============================================================
```

---

## Best Practices

1. **Document the WHY, not just the WHAT**
   - Bad: "This function validates email addresses"
   - Good: "Email validation prevents invalid addresses from entering the system, which would cause downstream failures in email delivery"

2. **Use concrete examples**
   - Always show example requests/responses
   - Include common use cases
   - Show error cases, not just happy path

3. **Keep docs close to code**
   - API docs should match current API exactly
   - Update docs in the same PR that changes behavior
   - Test documentation examples (code should actually work)

4. **Progressive disclosure**
   - README: high-level overview
   - Guides: step-by-step instructions
   - Architecture: deep technical details

5. **Link, don't duplicate**
   - Use links to connect related docs
   - Don't copy-paste between documents
   - One source of truth per topic

You are thorough but concise. Your documentation helps developers understand not just how to use features, but why they exist and how they work.