You are a **senior software engineer** cleaning up after a merged or closed ticket **$ARGUMENTS**.

> **Before doing anything else:** if `$ARGUMENTS` is empty or missing, print:
> ```
> Usage: /devflow-cleanup <TICKET-ID>
> Example: /devflow-cleanup SCRUM-123
> ```
> Then stop immediately. Do not proceed without a ticket ID.

Work through the following phases in order. Complete the entire workflow autonomously.

---

## PHASE 1 — Find the PR

Find the PR for ticket $ARGUMENTS (merged or closed):

```
gh pr list --state merged --search "$ARGUMENTS" --json number,title,url,headRefName,mergedAt | head -1
```

If not found in merged, check closed:
```
gh pr list --state closed --search "$ARGUMENTS" --json number,title,url,headRefName
```

If no PR is found at all, stop and print:
```
⚠️  No merged or closed PR found for $ARGUMENTS. Nothing to clean up.
```

Extract `headRefName` (the feature branch name) for use in subsequent phases.

---

## PHASE 2 — Verify Safe to Delete

Before deleting anything, verify:

1. **PR is merged or closed** — confirm status from Phase 1 output
2. **Branch is not the current branch** — run `git branch --show-current` and confirm it differs from `headRefName`
3. **No uncommitted changes on the branch** — run `git stash list` and check for any stash entries referencing the branch

If any check fails, stop and print what blocked cleanup.

---

## PHASE 3 — Remove Worktree (if exists)

Check if a worktree exists for this branch:
```
git worktree list
```

If a worktree path matches the branch, remove it:
```
git worktree remove <worktree-path> --force
```

If no worktree exists for this branch, skip silently.

---

## PHASE 4 — Delete Local Branch

Delete the local branch:
```
git branch -d <headRefName>
```

If `-d` fails (branch not fully merged according to git), do NOT use `-D` automatically. Instead print:

```
⚠️  DECISION: Local branch <headRefName> is not marked as merged by git.
    PR status: <merged/closed>
    Options:
      A) Force delete with -D (safe if PR is merged)
      B) Skip branch deletion

    Choosing A — PR is confirmed merged.
```

Then proceed with `git branch -D <headRefName>` only if the PR status from Phase 1 is `merged`.

---

## PHASE 5 — Delete Remote Branch (if still exists)

Check if remote branch still exists:
```
git ls-remote --heads origin <headRefName>
```

If it exists, delete it:
```
git push origin --delete <headRefName>
```

If it no longer exists (already deleted by GitHub after merge), skip silently.

---

## PHASE 6 — Prune Remote Tracking Refs

```
git remote prune origin
```

---

## PHASE 7 — Print Summary

```
============================================================
DEVFLOW CLEANUP COMPLETE

Ticket:  $ARGUMENTS
Branch:  <headRefName>
PR:      <PR_URL> (<merged|closed>)

Cleaned up:
  <✅ Worktree removed: <path> | ⚪ No worktree found>
  <✅ Local branch deleted | ⚪ Local branch already gone>
  <✅ Remote branch deleted | ⚪ Remote branch already gone>
  ✅ Remote tracking refs pruned
============================================================
```

