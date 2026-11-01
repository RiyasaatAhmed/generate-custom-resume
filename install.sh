#!/usr/bin/env bash
# Install generate-custom-resume from a clone of this repo.
#
#   ./install.sh                 link the skill for Claude Code and every agent that reads
#                                ~/.agents/skills (Cursor, Antigravity, Codex, Gemini CLI, ...),
#                                then create your data folder (~/resume-kit or $RESUME_KIT_HOME)
#   ./install.sh --target claude only link ~/.claude/skills   (or: --target agents)
#   ./install.sh --smoke         also export the fictional example resume to test PDF export
#   ./install.sh --uninstall     remove only the links this repo created; your data is kept
#
# Prefer a package manager when you are not developing the skill:
#   npx skills add RiyasaatAhmed/generate-custom-resume -g
# Safe to re-run. Links point at this folder, so re-run after moving it.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NAME="generate-custom-resume"
SKILL="$KIT/skills/$NAME"
RETIRED=(cover-letter cover-letter-generator clarity humanizer-zh)

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$*"; exit 1; }

target_dirs() {
  case "$TARGET" in
    claude) echo "$HOME/.claude/skills" ;;
    agents) echo "$HOME/.agents/skills" ;;
    all) printf '%s\n' "$HOME/.claude/skills" "$HOME/.agents/skills" ;;
  esac
}

link_skill() { # $1 = skills dir
  local dest="$1/$NAME"
  mkdir -p "$1"
  if [ -L "$dest" ]; then
    local target
    target="$(readlink "$dest")"
    if [ "$target" = "$SKILL" ]; then
      ok "$dest already points here"
    elif [ ! -e "$dest" ] || [[ "$target" == "$KIT/"* ]]; then
      ln -sfn "$SKILL" "$dest"   # dangling, or an older layout of this repo
      ok "$dest repointed (was $target)"
    else
      warn "$dest points to another copy ($target); left it alone"
    fi
  elif [ -e "$dest" ]; then
    warn "$dest exists and is not a link to this repo (installed by a package manager?); left it alone"
  else
    ln -s "$SKILL" "$dest"
    ok "linked $dest"
  fi
}

remove_ours() { # $1 = path; removes a symlink into this repo, or a command file that names it
  if [ -L "$1" ] && [[ "$(readlink "$1")" == "$KIT/"* ]]; then
    rm "$1"; ok "removed $1"
  elif [ -f "$1" ] && [[ "$1" == *.md ]] && grep -qF "$KIT" "$1"; then
    rm "$1"; ok "removed $1"
  fi
}

clean_old_layout() {
  # setup.sh (v0) rendered slash commands and linked extra skills into these places.
  local base tool skill
  for base in "$HOME" "$KIT"; do
    for tool in .claude .cursor; do
      remove_ours "$base/$tool/commands/$NAME.md"
      for skill in "${RETIRED[@]}"; do remove_ours "$base/$tool/skills/$skill"; done
    done
  done
  # Project-level links inside the repo would duplicate the user-level install.
  remove_ours "$KIT/.claude/skills/$NAME"
  remove_ours "$KIT/.cursor/skills/$NAME"
  remove_ours "$HOME/.cursor/skills/$NAME"   # Cursor reads ~/.agents/skills
}

TARGET=all
SMOKE=0
UNINSTALL=0
while [ $# -gt 0 ]; do
  case "$1" in
    --target) shift; TARGET="${1:-}"; [[ "$TARGET" =~ ^(claude|agents|all)$ ]] || fail "--target must be claude, agents, or all" ;;
    --smoke) SMOKE=1 ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) fail "unknown option: $1 (try --help)" ;;
  esac
  shift
done

if [ "$UNINSTALL" = 1 ]; then
  bold "Removing links to $KIT"
  for dir in "$HOME/.claude/skills" "$HOME/.agents/skills" "$HOME/.cursor/skills"; do remove_ours "$dir/$NAME"; done
  clean_old_layout
  echo "Your data folder was not touched."
  exit 0
fi

bold "1. Checking requirements"
command -v python3 >/dev/null || fail "python3 not found. Install Python 3.9+ from https://www.python.org/downloads/"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' || fail "Python 3.9+ required (found $(python3 -V))"
ok "$(python3 -V)"

bold "2. Linking the skill"
clean_old_layout
while IFS= read -r dir; do link_skill "$dir"; done < <(target_dirs)

bold "3. Preparing your data folder"
python3 "$SKILL/scripts/init_kit.py"

if [ "$SMOKE" = 1 ]; then
  bold "4. Smoke test: exporting the fictional example resume"
  python3 "$SKILL/scripts/smoke.py" || fail "export smoke test failed (see the error above)"
fi

echo
bold "Done."
echo "If the data folder still holds the example profile, fill it in first. Then ask your agent"
echo "to tailor a resume for a job post, or run /$NAME <job post URL>."
