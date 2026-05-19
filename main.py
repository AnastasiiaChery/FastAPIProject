"""
🧠 AI PR Autopilot — Multi-Agent Pipeline (MVP)
Uses Anthropic API to convert a task description into a ready-to-merge PR.

Improvements:
  1. Retry logic with exponential backoff (RateLimitError / APIError)
  2. Context compression to avoid token overflow
  3. Strict unified diff format for coder
  4. Structured pytest output for tester
  5. Reviewer split into Reviewer + Fixer agents
  6. DAG-style pipeline: coder → tester & reviewer in parallel → fixer
  7. Explicit API key via env var
  8. Safe JSON output with error handling
  9. Shared state dict passed between all agents
 10. PR description generator (GitHub-ready markdown)
 11. Demo mode: python main.py --demo
 12. CLI entry-point: ai-pr "task" (via setup.py / pipx)
"""

import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import anthropic
from anthropic import APIError, RateLimitError

# ─────────────────────────────────────────────
# Client & constants
# ─────────────────────────────────────────────

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))  # #7 explicit env var
MODEL = "claude-sonnet-4-20250514"

# ─────────────────────────────────────────────
# Core LLM call with retry  (#1)
# ─────────────────────────────────────────────

def call_agent(
    system_prompt: str,
    user_message: str,
    max_tokens: int = 1500,
    retries: int = 3,
) -> str:
    """Single LLM call with exponential-backoff retry."""
    for attempt in range(retries):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text.strip()
        except (RateLimitError, APIError) as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  ⚠️  API error ({e}), retrying in {wait}s…")
            time.sleep(wait)
    return ""  # unreachable, satisfies type checkers


# ─────────────────────────────────────────────
# Context compressor  (#2)
# ─────────────────────────────────────────────

def compress(text: str) -> str:
    """Summarise long agent output into short technical notes."""
    system = (
        "You are a technical summariser. "
        "Compress the following code/plan into concise bullet-point technical notes. "
        "Keep all file names, function names, and key decisions. "
        "Max 15 bullets."
    )
    return call_agent(system, text, max_tokens=500)


# ─────────────────────────────────────────────
# Formatting helper
# ─────────────────────────────────────────────

def section(title: str, content: str) -> str:
    border = "=" * 60
    return f"\n{border}\n  {title}\n{border}\n{content}\n"


# ─────────────────────────────────────────────
# Agent 1 — Planner
# ─────────────────────────────────────────────

def planner_agent(state: dict) -> None:
    system = (
        "You are a senior software architect. "
        "Break the task into a numbered implementation plan. "
        "Identify files to modify/create. Keep it minimal and practical."
    )
    state["plan"] = call_agent(system, f"Task: {state['task']}")
    state["plan_summary"] = compress(state["plan"])


# ─────────────────────────────────────────────
# Agent 2 — Coder  (#3 strict unified diff)
# ─────────────────────────────────────────────

def coder_agent(state: dict) -> None:
    system = (
        "You are an expert backend developer. "
        "Return ONLY a valid unified diff (git patch format). "
        "Use '--- a/file' / '+++ b/file' headers and @@ hunks. "
        "Do not include any explanations outside the diff."
    )
    prompt = (
        f"Task: {state['task']}\n\n"
        f"Plan (summary):\n{state['plan_summary']}\n\n"
        "Produce the unified diff."
    )
    state["code"] = call_agent(system, prompt, max_tokens=2000)
    state["code_summary"] = compress(state["code"])


# ─────────────────────────────────────────────
# Agent 3 — Tester  (#4 structured pytest)
# ─────────────────────────────────────────────

def tester_agent(state: dict) -> None:
    system = (
        "You are a QA engineer. "
        "Write pytest tests only. "
        "Use fixtures where appropriate. "
        "Cover happy paths, edge cases, and validation errors. "
        "Output a single valid Python test file and nothing else."
    )
    prompt = (
        f"Task: {state['task']}\n\n"
        f"Code summary:\n{state['code_summary']}\n\n"
        "Write the test file."
    )
    state["tests"] = call_agent(system, prompt, max_tokens=2000)


# ─────────────────────────────────────────────
# Agent 4a — Reviewer  (#5 split reviewer/fixer)
# ─────────────────────────────────────────────

def reviewer_agent(state: dict) -> None:
    system = (
        "You are a senior code reviewer. "
        "Analyse the diff and tests. "
        "Output ONLY a numbered list of issues: bugs, security risks, "
        "performance problems, missing test coverage. "
        "If there are no issues, respond with exactly: 'No issues found'. "
        "Be specific and concise."
    )
    prompt = (
        f"Task: {state['task']}\n\n"
        f"Diff summary:\n{state['code_summary']}\n\n"
        f"Tests:\n{state['tests']}\n\n"
        "List all issues."
    )
    state["review"] = call_agent(system, prompt, max_tokens=1500)


# ─────────────────────────────────────────────
# Agent 4b — Fixer  (#5 split reviewer/fixer)
# ─────────────────────────────────────────────

def fixer_agent(state: dict) -> None:
    system = (
        "You are an expert backend developer fixing code issues. "
        "Given the original diff and a list of review issues, "
        "produce a corrected unified diff that fixes all critical issues. "
        "If no fixes are needed, respond with exactly: 'No changes needed'."
    )
    prompt = (
        f"Original diff:\n{state['code']}\n\n"
        f"Review issues:\n{state['review']}\n\n"
        "Produce the fixed diff."
    )
    state["fixed_code"] = call_agent(system, prompt, max_tokens=2000)


# ─────────────────────────────────────────────
# Pipeline — DAG orchestrator  (#6)
# ─────────────────────────────────────────────
#
#   planner
#      ↓
#   coder
#    ↓    ↓
# tester  reviewer   ← run in parallel
#      ↓
#    fixer  (skipped if no issues)
#

def run_pipeline(task: str) -> dict:
    # #9 shared state dict
    state: dict = {
        "task": task,
        "plan": None,
        "plan_summary": None,
        "code": None,
        "code_summary": None,
        "tests": None,
        "review": None,
        "fixed_code": None,
    }

    print(f"\n🚀 AI PR Autopilot — task:\n  \"{task}\"\n")

    # Step 1: Plan
    print("🧩 [1] Planner Agent…")
    planner_agent(state)

    # Step 2: Code
    print("💻 [2] Coder Agent…")
    coder_agent(state)

    # Step 3: Tester + Reviewer in parallel
    print("🧪🔍 [3] Tester & Reviewer Agents (parallel)…")
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(tester_agent, state): "tester",
            executor.submit(reviewer_agent, state): "reviewer",
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                future.result()
                print(f"  ✅ {name} done")
            except Exception as exc:
                print(f"  ❌ {name} failed: {exc}")
                raise

    # Step 4: Fixer — skip if no issues
    no_issues = (state["review"] or "").strip().lower().startswith("no issues")
    if no_issues:
        state["fixed_code"] = "No changes needed"
        print("🔧 [4] Fixer — no issues found, skipping")
    else:
        print("🔧 [4] Fixer Agent…")
        fixer_agent(state)

    return state


# ─────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────

def generate_pr_description(state: dict) -> str:
    """Produce a GitHub-ready PR description in Markdown."""
    final_diff = state.get("fixed_code") or "No changes needed"
    return f"""\
## 📋 Summary
{state['plan']}

## 💻 Changes
{state['code_summary']}

## 🧪 Tests
```python
{state['tests']}
```

## 🔍 Review
{state['review']}

## 🔧 Final Diff (after fixes)
```diff
{final_diff}
```
"""


def print_result(state: dict) -> None:
    print(section("📋 TASK", state["task"]))
    print(section("📐 PLAN", state["plan"] or ""))
    print(section("💻 CODE DIFF", state["code"] or ""))
    print(section("🧪 UNIT TESTS", state["tests"] or ""))
    print(section("🔍 REVIEW ISSUES", state["review"] or ""))
    print(section("🔧 FIXED DIFF", state["fixed_code"] or "No changes needed"))
    print(section("📝 PR DESCRIPTION", state.get("pr_description") or ""))
    print("\n✅ PR Autopilot complete!\n")


def save_result(state: dict, path: str = "pr_output.json") -> None:
    # #8 safe JSON save
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        print(f"💾 JSON saved  → {path}")
    except Exception as e:
        print(f"⚠️  Failed to save JSON: {e}")

    # Also save the human-readable PR description as Markdown
    pr_md = state.get("pr_description")
    if pr_md:
        md_path = path.replace(".json", ".md")
        try:
            with open(md_path, "w", encoding="utf-8") as f:
                f.write(pr_md)
            print(f"📄 PR description → {md_path}")
        except Exception as e:
            print(f"⚠️  Failed to save markdown: {e}")


# ─────────────────────────────────────────────
# Entry point  (#11 demo mode, #12 ai-pr alias)
# ─────────────────────────────────────────────

DEMO_TASK = "Add rate limiting to login endpoint"
EXAMPLE_TASK = "Add caching layer to GET /users endpoint"


def main() -> None:
    args = sys.argv[1:]

    # --demo flag: judges can run without thinking
    if "--demo" in args or not args:
        if "--demo" in args:
            task = DEMO_TASK
            print(f"🎬 Demo mode — task: \"{task}\"\n")
        else:
            task = EXAMPLE_TASK
            print(f"ℹ️  No task given — using example: \"{task}\"")
            print("   Usage: python main.py \"Your task here\"")
            print("          python main.py --demo\n")
    else:
        task = " ".join(args)

    state = run_pipeline(task)
    state["pr_description"] = generate_pr_description(state)  # #10 PR generator

    print_result(state)
    save_result(state)


if __name__ == "__main__":
    main()