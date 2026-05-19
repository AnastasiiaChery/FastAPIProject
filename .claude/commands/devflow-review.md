You are an autonomous software engineer applying PR review feedback for Jira ticket **$ARGUMENTS**.

Work through the following phases in order. Complete the entire workflow autonomously.

---

## PHASE 1 — Find the Draft PR

Find the open draft PR for ticket $ARGUMENTS:

```
gh pr list --state open --search "$ARGUMENTS" --json number,title,url,headRefName
```

If no PR is found, stop and print an error. If multiple PRs are found, pick the most recent one.

Switch to the PR branch:
```
git checkout <headRefName>
```

---

## PHASE 2 — Fetch All Review Comments

Fetch all review comments from the PR:

```
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments \
  --jq '[.[] | {id: .id, path: .path, line: .line, body: .body, diff_hunk: .diff_hunk}]'
```

Also fetch general PR comments (not inline):
```
gh api repos/{owner}/{repo}/issues/<PR_NUMBER>/comments \
  --jq '[.[] | {id: .id, body: .body}]'
```

Summarize all comments before proceeding so you have a clear picture of what needs to change.

If there are no comments, print:
```
No review comments found on PR. Nothing to fix.
```
Then stop.

---

## PHASE 3 — Apply Fixes

For each comment, address it systematically:
- Understand the concern before making any change
- Make the minimal change that satisfies the comment
- Do not refactor beyond what the comment requests
- Do not introduce new features

After applying all fixes, verify nothing was accidentally broken by re-reading the changed files.

---

## PHASE 4 — Run Tests

```
python -m pytest tests/ -v
```

If any tests fail:
- Fix the failures before proceeding
- Do not mark work complete with failing tests

---

## PHASE 5 — Commit and Push Fixes

1. Stage changed files by name (not `git add .` — only the files you actually changed)
2. Commit with a message in the format: `$ARGUMENTS: address review comments`
3. Push: `git push`

---

## PHASE 6 — Mark PR Ready for Review

Convert the draft PR to ready-for-review:

```
gh pr ready <PR_NUMBER>
```

Then print:

```
============================================================
REVIEW FIXES COMPLETE

PR is now ready for merge: <PR_URL>

Changes applied:
<bullet list of what was fixed>
============================================================
```
