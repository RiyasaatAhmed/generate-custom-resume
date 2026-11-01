#!/usr/bin/env bash
# Set up the generate-custom-resume kit.
#
#   ./setup.sh             project setup: profile files, command + skills for Claude Code and Cursor
#                          inside this folder, then a smoke test
#   ./setup.sh --global    also install the command + skills for your user, so
#                          /generate-custom-resume works from any folder
#   ./setup.sh --uninstall-global   remove the user-level install (only files this kit created)
#
# Safe to re-run. Re-run after moving this folder: the command embeds its absolute path.
set -euo pipefail

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMD_NAME="generate-custom-resume"
SKILLS=(generate-custom-resume cover-letter cover-letter-generator clarity)
RETIRED_SKILLS=(humanizer-zh)   # removed from the kit; their old links get cleaned up
TOOLS=(.claude .cursor)

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
ok()   { printf '  \033[32m✓\033[0m %s\n' "$*"; }
warn() { printf '  \033[33m!\033[0m %s\n' "$*"; }
fail() { printf '  \033[31m✗\033[0m %s\n' "$*"; exit 1; }

render_command() { # $1 = destination file
  mkdir -p "$(dirname "$1")"
  # escape sed replacement metacharacters so any folder path survives
  local kit_esc
  kit_esc="$(printf '%s' "$KIT" | sed 's/[&|\\]/\\&/g')"
  sed "s|{{KIT}}|$kit_esc|g" "$KIT/commands/$CMD_NAME.md" > "$1"
}

link_skill() { # $1 = skills dir, $2 = skill name
  local dest="$1/$2"
  mkdir -p "$1"
  if [ -L "$dest" ]; then
    local target
    target="$(readlink "$dest")"
    if [ "$target" = "$KIT/skills/$2" ]; then
      ok "$dest already points to this kit"
    elif [ ! -e "$dest" ] && [[ "$target" == */skills/"$2" ]]; then
      # dangling link left behind when the kit folder moved; nothing to preserve
      ln -sfn "$KIT/skills/$2" "$dest"
      ok "$dest repointed from missing $target"
    else
      warn "$dest points elsewhere; left it alone (the command uses this kit's explicit path)"
    fi
  elif [ -e "$dest" ]; then
    warn "$dest already exists and is not from this kit; left it alone"
    return
  else
    ln -s "$KIT/skills/$2" "$dest"
  fi
}

unlink_ours() { # $1 = link path; removes it only if it points into this kit
  if [ -L "$1" ] && [[ "$(readlink "$1")" == "$KIT/skills/"* ]]; then rm "$1"; fi
}

install_into() { # $1 = base dir that holds .claude / .cursor
  for tool in "${TOOLS[@]}"; do
    local cmd="$1/$tool/commands/$CMD_NAME.md"
    if [ -f "$cmd" ] && ! grep -qF "$KIT" "$cmd"; then
      cp "$cmd" "$cmd.bak.$(date +%Y%m%d%H%M%S)"
      warn "backed up your existing $cmd"
    fi
    render_command "$cmd"
    for skill in "${SKILLS[@]}"; do link_skill "$1/$tool/skills" "$skill"; done
    for skill in "${RETIRED_SKILLS[@]}"; do unlink_ours "$1/$tool/skills/$skill"; done
    ok "$tool: command + ${#SKILLS[@]} skills -> $1/$tool"
  done
}

uninstall_global() {
  bold "Removing user-level install"
  for tool in "${TOOLS[@]}"; do
    local cmd="$HOME/$tool/commands/$CMD_NAME.md"
    if [ -f "$cmd" ] && grep -qF "$KIT" "$cmd"; then rm "$cmd"; ok "removed $cmd"; fi
    for skill in "${SKILLS[@]}" "${RETIRED_SKILLS[@]}"; do
      local link="$HOME/$tool/skills/$skill"
      if [ -L "$link" ] && [ "$(readlink "$link")" = "$KIT/skills/$skill" ]; then rm "$link"; ok "removed $link"; fi
    done
  done
}

GLOBAL=0
SKIP_SMOKE=0
for option in "$@"; do
  case "$option" in
    --global) GLOBAL=1 ;;
    --skip-smoke) SKIP_SMOKE=1 ;;
    --uninstall-global) uninstall_global; exit 0 ;;
    -h|--help) sed -n '2,10p' "$0"; echo '  --skip-smoke    install without running browser export'; exit 0 ;;
    *) fail "unknown option: $option (try --help)" ;;
  esac
done

bold "1. Checking requirements"
command -v python3 >/dev/null || fail "python3 not found. Install Python 3.9+ from https://www.python.org/downloads/"
python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' || fail "Python 3.9+ required (found $(python3 -V))"
ok "$(python3 -V)"
if CHROME="$(KIT_SCRIPTS="$KIT/scripts" python3 -c "import os, sys; sys.path.insert(0, os.environ['KIT_SCRIPTS']); import kit; print(kit.find_chrome())" 2>/dev/null)"; then
  ok "Chrome: $CHROME"
else
  warn "Chrome not found: DOCX export works; PDF export needs Chrome or CHROME_PATH."
  SKIP_SMOKE=1
fi
if python3 -c 'import pypdf' 2>/dev/null; then
  ok "pypdf installed (PDF content, link, and page checks enabled)"
else
  warn "pypdf not installed: PDF content/link/page checks will be skipped. Install with: python3 -m pip install pypdf"
fi
if command -v pdftoppm >/dev/null || python3 -c 'import pypdfium2, PIL' 2>/dev/null; then
  ok "PDF page renderer available (actual page previews enabled)"
else
  warn "No PDF page renderer: previews skipped. Optional: install poppler (pdftoppm) or python3 -m pip install pypdfium2 pillow"
fi

bold "2. Creating your profile"
for pair in "profile.example.json:profile.json" "base-resume.example.md:base-resume.md" "candidate-notes.example.md:candidate-notes.md"; do
  src="${pair%%:*}"; dst="${pair##*:}"
  if [ -f "$KIT/profile/$dst" ]; then
    ok "profile/$dst exists, kept"
  else
    cp "$KIT/profile/$src" "$KIT/profile/$dst"
    ok "created profile/$dst (edit this with your details)"
  fi
done
mkdir -p "$KIT/applications"

bold "3. Installing the command + skills into this folder"
install_into "$KIT"
if [ "$GLOBAL" = 1 ]; then
  bold "   ...and for your user (--global)"
  install_into "$HOME"
fi

if [ "$SKIP_SMOKE" = 0 ]; then
  bold "4. Smoke test: exporting the example resume"
  RESUME_PROFILE="$KIT/profile/profile.example.json" python3 "$KIT/scripts/smoke.py" \
    || fail "export smoke test failed (see the error above)"
else
  warn "Export smoke test skipped; run python3 scripts/smoke.py when Chrome is available."
fi

echo
bold "Done."
if grep -q "Jane Doe" "$KIT/profile/base-resume.md" 2>/dev/null; then
  echo "Next: fill in your profile (profile/profile.json, base-resume.md, candidate-notes.md)."
  echo "      The README walks through each file."
fi
if [ "$GLOBAL" = 1 ]; then
  echo "Then run /$CMD_NAME <job post URL> in Claude Code or Cursor, from any folder."
else
  echo "Then open this folder in Claude Code (cd \"$KIT\" && claude) or Cursor and run:"
  echo "  /$CMD_NAME <job post URL>"
fi
