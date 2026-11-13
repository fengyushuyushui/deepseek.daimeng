#!/usr/bin/env bash
# 把 whale-girl-persona 装成「项目级」，随项目持久（云电脑 / 新对话不丢）。
#
# 用法:
#   bash install-to-project.sh                # 装到当前目录
#   bash install-to-project.sh /path/to/proj  # 装到指定项目
#   bash install-to-project.sh --user         # 装到 ~/.codebuddy（用户级，所有项目）
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$HERE/skills/whale-girl-persona"
[ -d "$SKILL_SRC" ] || SKILL_SRC="$HERE/.codebuddy/skills/whale-girl-persona"
[ -d "$SKILL_SRC" ] || { echo "找不到技能目录（需在仓库根执行）"; exit 1; }

MODE="project"
TARGET="$PWD"
if [ "${1:-}" = "--user" ]; then
  MODE="user"; TARGET="$HOME"
elif [ -n "${1:-}" ]; then
  TARGET="$(cd "$1" && pwd)"
fi

CFG="$TARGET/.codebuddy"
mkdir -p "$CFG/skills" "$CFG/hooks" "$CFG/commands"
rm -rf "$CFG/skills/whale-girl-persona"
cp -r "$SKILL_SRC" "$CFG/skills/whale-girl-persona"
cp "$SKILL_SRC/scripts/whale_persona_inject.py" "$CFG/hooks/whale_persona_inject.py"
chmod +x "$CFG/hooks/whale_persona_inject.py"

if [ -f "$HERE/commands/whale.md" ]; then
  cp "$HERE/commands/whale.md" "$CFG/commands/whale.md"
  echo "slash 命令已装: /whale"
fi

HOOK_ABS="$CFG/hooks/whale_persona_inject.py"
python3 - "$CFG/settings.json" "$HOOK_ABS" <<'PY'
import json, sys, pathlib, time, shutil
path, hook = sys.argv[1], sys.argv[2]
p = pathlib.Path(path)
cfg = {}
if p.exists():
    try:
        cfg = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        sys.exit(f"{path} 不是合法 JSON，先修好")
    shutil.copy2(p, p.with_suffix(f".json.bak-{time.strftime('%Y%m%d%H%M%S')}"))

cmd = f'python3 "${{CODEBUDDY_PROJECT_DIR:-{hook.rsplit("/.codebuddy/",1)[0]}}}/.codebuddy/hooks/whale_persona_inject.py"'
hooks = cfg.setdefault("hooks", {})
for event, matcher in (("SessionStart", "startup"), ("UserPromptSubmit", None)):
    arr = hooks.setdefault(event, [])
    if any(h.get("command") == cmd for e in arr for h in e.get("hooks", [])):
        continue
    entry = {"hooks": [{"type": "command", "command": cmd, "timeout": 15}]}
    if matcher:
        entry = {"matcher": matcher, **entry}
    arr.append(entry)
p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已写入 hook 配置: {path}")
PY

echo "技能已装到: $CFG/skills/whale-girl-persona"
echo "hook 已装到: $HOOK_ABS"
echo
echo "开关（默认打开，因为你装它就是为了用它）:"
touch "$CFG/.persona-on"
echo "  开: touch $CFG/.persona-on"
echo "  关: rm $CFG/.persona-on"
echo
echo "生效: 重启 WorkBuddy 或新建会话（settings.json 不热加载）"
if [ "$MODE" = "user" ]; then
  echo "注意: 用户级对全部项目生效，干活前记得关。"
fi
