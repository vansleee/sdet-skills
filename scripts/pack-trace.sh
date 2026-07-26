#!/usr/bin/env bash
# pack-trace.sh <task-evidence-dir>
# 把 Playwright MCP 暫存區的 raw trace 檔打包成 trace.zip、搬進當次證據資料夾、再清空暫存區。
# 指令形狀固定(不含動態檔名),權限只需放行一條 Bash(bash scripts/pack-trace.sh:*)。
set -euo pipefail

STAGE="${PW_TRACE_DIR:-.pw-mcp-traces}"   # 暫存 output-dir,對齊 config/product-context.md
DEST="${1:?用法: bash scripts/pack-trace.sh <task-evidence-dir>}"

[ -d "$STAGE" ] || { echo "找不到暫存區:$STAGE"; exit 1; }
if [ -z "$(ls -A "$STAGE" 2>/dev/null)" ]; then
  echo "暫存區是空的,沒有 trace 可打包:$STAGE"; exit 1
fi

mkdir -p "$DEST"
( cd "$STAGE" && zip -qr trace.zip . -x trace.zip )   # ← 指令形狀永遠一樣
mv "$STAGE/trace.zip" "$DEST/"
find "$STAGE" -mindepth 1 -delete                     # 清空暫存,準備下一次
echo "已打包 → ${DEST%/}/trace.zip"
