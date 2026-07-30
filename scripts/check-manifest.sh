#!/usr/bin/env bash
# 檢查 .claude-plugin/plugin.json 的 skills 清單與檔案系統是否一致。
#
# plugin 安裝法要手動維護清單(symlink 時代是掃描出來的),所以新增或改名 skill
# 很容易忘記改 manifest —— 忘了就是那支 skill 悄悄不存在。這支把兩個方向都比對:
#   1. manifest 宣告了但目錄沒有 SKILL.md → 改名或刪除後沒同步
#   2. 有 SKILL.md 但 manifest 沒宣告     → 新增 skill 後沒同步
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

declared="$(jq -r '.skills[]' .claude-plugin/plugin.json | sed 's#^\./##' | sort)"
actual="$(find skills -maxdepth 3 -name SKILL.md -print0 \
  | xargs -0 -n1 dirname | sort)"

missing="$(comm -23 <(printf '%s\n' "$declared") <(printf '%s\n' "$actual"))"
undeclared="$(comm -13 <(printf '%s\n' "$declared") <(printf '%s\n' "$actual"))"

status=0
if [ -n "$missing" ]; then
  status=1
  echo "plugin.json 宣告了這些 skill,但找不到 SKILL.md:" >&2
  printf '  %s\n' $missing >&2
fi
if [ -n "$undeclared" ]; then
  status=1
  echo "這些 skill 有 SKILL.md,但 plugin.json 沒宣告:" >&2
  printf '  %s\n' $undeclared >&2
fi

if [ "$status" -ne 0 ]; then
  echo >&2
  echo "修正 .claude-plugin/plugin.json 的 skills 陣列後重跑。" >&2
  exit 1
fi

echo "manifest 一致:$(printf '%s\n' "$declared" | wc -l | tr -d ' ') 支 skill"
