#!/usr/bin/env bash
# Link the matchcut skills into your agents' skill folders (macOS, Linux). Links, not copies:
# a `git pull` here updates every installed skill in place. On Windows use install.ps1.
#
#   ./install.sh                          # Claude Code, Codex and Hermes (the ones that exist)
#   ./install.sh --targets claude         # only Claude Code (claude, codex, hermes, agents)
#   ./install.sh --only matchcut,ui-reel
#   ./install.sh --dest /tmp/skills       # any folder
#   ./install.sh --list
#   ./install.sh --uninstall
set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS="$REPO/skills"
targets="claude,codex,hermes"; only=""; dest=""; mode=install
while [[ $# -gt 0 ]]; do
  case "$1" in
    --targets) targets="$2"; shift ;;
    --only) only="$2"; shift ;;
    --dest) dest="$2"; shift ;;
    --list) mode=list ;;
    --uninstall) mode=uninstall ;;
    -h|--help) sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

folder_for() {
  case "$1" in
    claude) echo "$HOME/.claude/skills" ;; codex) echo "$HOME/.codex/skills" ;;
    hermes) echo "$HOME/.hermes/skills" ;; agents) echo "$HOME/.agents/skills" ;;
    *) echo "unknown target: $1" >&2; exit 2 ;;
  esac
}
folders=()
if [[ -n $dest ]]; then folders=("$dest"); else IFS=',' read -ra ts <<<"$targets"; for t in "${ts[@]}"; do folders+=("$(folder_for "$t")"); done; fi

wanted() { [[ -z $only ]] && return 0; [[ ",$only," == *",$1,"* ]]; }

for dir in "$SKILLS"/*/; do
  dir="${dir%/}"; name="$(basename "$dir")"
  [[ -f $dir/SKILL.md ]] || continue
  wanted "$name" || continue
  if [[ $mode == list ]]; then
    printf '%-18s %s\n' "$name" "$(grep -m1 '^description:' "$dir/SKILL.md" | sed 's/^description:[[:space:]]*//' | cut -c1-90)"
    continue
  fi
  for folder in "${folders[@]}"; do
    if [[ -z $dest && ! -d $(dirname "$folder") ]]; then continue; fi
    mkdir -p "$folder"
    link="$folder/$name"
    if [[ $mode == uninstall ]]; then
      [[ -L $link && "$(readlink "$link")" == "$SKILLS"/* ]] && rm "$link" && echo "removed  $link"
      continue
    fi
    if [[ -L $link ]]; then
      if [[ "$(readlink "$link")" == "$SKILLS"/* ]]; then rm "$link"; else echo "skip     $link (links somewhere else)"; continue; fi
    elif [[ -e $link ]]; then echo "skip     $link (a real folder is there)"; continue; fi
    ln -s "$dir" "$link" && echo "linked   $link"
  done
done
[[ $mode == install ]] && echo "Done. Start a new agent session to load the skills." || true
