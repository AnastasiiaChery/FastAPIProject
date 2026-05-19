#!/usr/bin/env bash
# devflow setup wizard — run once per machine
set -euo pipefail

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $*"; }
fail() { echo -e "  ${RED}✗${NC} $*"; }
warn() { echo -e "  ${YELLOW}!${NC} $*"; }
ask()  { echo -e "\n${CYAN}${BOLD}?${NC} $*"; }
step() { echo -e "\n${BOLD}── $* ${NC}"; }

confirm() {
  local prompt="$1" default="${2:-n}"
  local options="[y/N]"; [[ "$default" == "y" ]] && options="[Y/n]"
  read -rp "  $prompt $options " ans
  ans="${ans:-$default}"
  [[ "$ans" =~ ^[Yy]$ ]]
}

add_or_replace_in_shell() {
  local key="$1" value="$2" rc="$3"
  if grep -q "$key" "$rc" 2>/dev/null; then
    # Replace existing line
    local tmpfile; tmpfile="$(mktemp)"
    grep -v "$key" "$rc" > "$tmpfile"
    mv "$tmpfile" "$rc"
  fi
  echo "" >> "$rc"
  echo "# devflow" >> "$rc"
  echo "$value" >> "$rc"
}

detect_shell_rc() {
  if [[ -f "$HOME/.zshrc" ]]; then echo "$HOME/.zshrc"
  elif [[ -f "$HOME/.bashrc" ]]; then echo "$HOME/.bashrc"
  else echo "$HOME/.bash_profile"; fi
}

SHELL_RC="$(detect_shell_rc)"

echo ""
echo -e "${BOLD}=================================================="
echo -e "  devflow — Setup Wizard"
echo -e "==================================================${NC}"

# ── STEP 1: Prerequisites ──────────────────────────────
step "Step 1 — Checking prerequisites"
echo ""

MISSING=()
for tool in claude gh jira; do
  if command -v "$tool" &>/dev/null; then
    ok "$tool  $(command -v $tool)"
  else
    fail "$tool  not found"
    MISSING+=("$tool")
  fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo ""
  warn "Missing: ${MISSING[*]}"
  echo ""
  for t in "${MISSING[@]}"; do
    case "$t" in
      claude) echo "    claude → https://claude.ai/code" ;;
      gh)     echo "    gh     → brew install gh" ;;
      jira)   echo "    jira   → brew install ankitpokhrel/tap/jira-cli" ;;
    esac
  done
  echo ""
  confirm "Continue anyway?" || exit 1
fi

# ── STEP 2: GitHub ─────────────────────────────────────
step "Step 2 — GitHub authentication"
echo ""

if gh auth status &>/dev/null; then
  GITHUB_USER="$(gh api user --jq '.login' 2>/dev/null || echo 'unknown')"
  ok "Already authenticated as ${GITHUB_USER}"
else
  warn "Not authenticated"
  echo ""
  echo "  Choose how to authenticate:"
  echo "    1) Browser (recommended)"
  echo "    2) Personal Access Token (PAT)"
  read -rp "  > [1/2] " gh_method
  gh_method="${gh_method:-1}"

  if [[ "$gh_method" == "2" ]]; then
    ask "GitHub Personal Access Token"
    echo "  (create at https://github.com/settings/tokens — needs: repo, workflow, read:org)"
    read -rsp "  > " GH_TOKEN
    echo ""
    echo "$GH_TOKEN" | gh auth login --with-token
  else
    gh auth login
  fi
fi

# Configure git to use gh credentials for push/pull
if gh auth status &>/dev/null; then
  gh auth setup-git 2>/dev/null && ok "Git credentials configured via gh"
fi

# ── STEP 3: Jira ───────────────────────────────────────
step "Step 3 — Jira configuration"
echo ""

JIRA_CONFIG="$HOME/.config/.jira/.config.yml"
SKIP_JIRA=false

if [[ -f "$JIRA_CONFIG" ]]; then
  CURRENT_SERVER="$(grep 'server:' "$JIRA_CONFIG" | awk '{print $2}')"
  CURRENT_LOGIN="$(grep 'login:' "$JIRA_CONFIG" | awk '{print $2}')"
  warn "Existing config found: ${CURRENT_SERVER} / ${CURRENT_LOGIN}"
  if ! confirm "Overwrite it?"; then
    ok "Keeping existing Jira config"
    SKIP_JIRA=true
  fi
fi

if [[ "$SKIP_JIRA" == false ]]; then
  ask "Jira server URL  (e.g. https://mycompany.atlassian.net):"
  read -rp "  > " JIRA_SERVER
  JIRA_SERVER="${JIRA_SERVER%/}"

  ask "Jira login email:"
  read -rp "  > " JIRA_EMAIL

  ask "Jira API token  (create at https://id.atlassian.com/manage-api-tokens):"
  read -rsp "  > " JIRA_TOKEN
  echo ""

  mkdir -p "$(dirname "$JIRA_CONFIG")"
  cat > "$JIRA_CONFIG" <<EOF
auth_type: basic
installation: Cloud
login: $JIRA_EMAIL
server: $JIRA_SERVER
issue:
  types:
    - id: "10002"
      name: Task
      handle: task
      subtask: false
    - id: "10001"
      name: Story
      handle: story
      subtask: false
    - id: "10004"
      name: Bug
      handle: bug
      subtask: false
    - id: "10007"
      name: Subtask
      handle: subtask
      subtask: true
    - id: "10000"
      name: Epic
      handle: epic
      subtask: false
EOF

  # Save token to shell config
  if grep -q "JIRA_API_TOKEN" "$SHELL_RC" 2>/dev/null; then
    warn "JIRA_API_TOKEN already in $SHELL_RC"
    if confirm "Replace it?"; then
      add_or_replace_in_shell "JIRA_API_TOKEN" "export JIRA_API_TOKEN=\"$JIRA_TOKEN\"" "$SHELL_RC"
      ok "Token updated in $SHELL_RC"
    fi
  else
    add_or_replace_in_shell "JIRA_API_TOKEN" "export JIRA_API_TOKEN=\"$JIRA_TOKEN\"" "$SHELL_RC"
    ok "Token saved to $SHELL_RC"
  fi

  # Verify connection
  echo ""
  echo "  Testing Jira connection..."
  if JIRA_API_TOKEN="$JIRA_TOKEN" jira me &>/dev/null; then
    ok "Connected as $(JIRA_API_TOKEN="$JIRA_TOKEN" jira me)"
  else
    fail "Connection failed — check server URL, email, and token"
    warn "Re-run this script to fix: ./devflow/setup.sh"
  fi
fi

# ── Done ───────────────────────────────────────────────
echo ""
echo -e "${BOLD}=================================================="
echo -e "  Setup complete!"
echo -e "==================================================${NC}"
echo ""
echo "  Activate in current shell:"
echo "    source $SHELL_RC"
echo ""
echo "  Then open Claude Code and run:"
echo "    /devflow TICKET-123"
echo "    /devflow-review TICKET-123"
echo ""
