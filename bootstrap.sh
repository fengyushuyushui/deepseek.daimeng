#!/usr/bin/env bash
# 一条命令重装「大肥鱼」人格（项目级，云电脑新对话不丢）。
#
# 本地仓库里跑:
#   bash bootstrap.sh /workspace
#
# 没有仓库时（联网）:
#   curl -fsSL https://raw.githubusercontent.com/fengyushuyushui/codebuddy-skills/main/bootstrap.sh | bash -s -- /workspace
#
# 换源: WHALE_REPO=https://github.com/you/your-fork.git bash bootstrap.sh
set -euo pipefail

REPO_URL="${WHALE_REPO:-https://github.com/fengyushuyushui/codebuddy-skills.git}"
TARGET="${1:-$PWD}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "")"

echo "目标: $TARGET"

if [ -n "$HERE" ] && [ -d "$HERE/skills/whale-girl-persona" ]; then
  SRC="$HERE"
  echo "源: 本地仓库 $SRC"
else
  TMP="$(mktemp -d)"
  echo "源: $REPO_URL（克隆到临时目录）"
  if ! git clone --depth 1 "$REPO_URL" "$TMP/repo" >/dev/null 2>&1; then
    echo "克隆失败：仓库还没推上去，或者当前环境没网/没权限。" >&2
    echo "本地有仓库的话，直接进仓库目录跑 install-to-project.sh。" >&2
    exit 1
  fi
  SRC="$TMP/repo"
fi

bash "$SRC/install-to-project.sh" "$TARGET"

# 自检：hook 能不能真的吐出人格卡
set +e
HOOK="$TARGET/.codebuddy/hooks/whale_persona_inject.py"
CARD="$TARGET/.codebuddy/skills/whale-girl-persona/references/persona-compact.md"
if [ -f "$HOOK" ] && [ -f "$CARD" ]; then
  N=$(echo '{}' | CODEBUDDY_PROJECT_DIR="$TARGET" python3 "$HOOK" 2>/dev/null \
      | python3 -c 'import sys,json;d=json.load(sys.stdin);print(len(d.get("hookSpecificOutput",{}).get("additionalContext","")))' 2>/dev/null)
  echo "自检: 注入 ${N:-0} 字"
else
  echo "自检: 缺文件，安装可能没完成" >&2
fi
set -e

echo
echo "装完了。重启 WorkBuddy 或新建会话才生效。"
