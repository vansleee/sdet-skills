#!/usr/bin/env bash
# 從 plugin 安裝法退回個人 skill 安裝法(2026-07-30 之前的做法)。
#
# 兩種安裝法不能並存,同一支 skill 會重複註冊,所以要先移除 plugin:
#     claude plugin uninstall sdet-skills
#
# 清單不寫死在這裡 —— 交給 link-skills.sh 從 repo 現況掃出來,
# 新增或改名 skill 之後這支不會過期。
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# `claude plugin list` 印的是 "  ❯ sdet-skills@<marketplace>",所以比對 name@ 而非行首。
if claude plugin list 2>/dev/null | grep -q 'sdet-skills@'; then
  echo "sdet-skills plugin 仍安裝中。先執行:" >&2
  echo "    claude plugin uninstall sdet-skills" >&2
  exit 1
fi

exec "$ROOT/scripts/link-skills.sh"
