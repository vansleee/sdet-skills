#!/usr/bin/env bash
# 把本 repo 的每支 skill symlink 進 ~/.claude/skills,git pull 後即同步更新。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${HOME}/.claude/skills"
mkdir -p "$DEST"
find "$ROOT/skills" -name SKILL.md -maxdepth 3 | while read -r f; do
  d="$(dirname "$f")"; name="$(basename "$d")"
  ln -sfn "$d" "$DEST/$name"
  echo "linked $name"
done
