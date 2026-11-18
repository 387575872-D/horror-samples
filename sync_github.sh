#!/usr/bin/env bash
# 一键同步当前项目到 GitHub
# 用法：bash sync_github.sh "提交说明"
set -euo pipefail
cd "$(dirname "$0")"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
case "$BRANCH" in
  LS_*) ;;
  *) echo "当前分支 $BRANCH 不是 LS_ 开头，本机约定不允许推送。"; exit 1 ;;
esac

git add -A
if git diff --cached --quiet; then
  echo "没有变更，跳过提交。"
  exit 0
fi

MSG="${1:-自动同步：$(date '+%Y-%m-%d %H:%M')}"
git commit -q -m "$MSG"
git -c http.schannelCheckRevoke=false push origin "$BRANCH"
echo "已推送 $BRANCH：$MSG"
