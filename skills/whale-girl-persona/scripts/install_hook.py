#!/usr/bin/env python3
"""把人格 hook 装进 WorkBuddy（写入 ~/.codebuddy/hooks 并注册 settings.json）。

用法:
  python3 scripts/install_hook.py            # 安装
  python3 scripts/install_hook.py --uninstall # 卸载
  python3 scripts/install_hook.py --status    # 看状态

装完需要**重启 WorkBuddy 或新建会话**才生效（settings.json 不热加载）。
开关: touch ~/.codebuddy/.persona-on / rm 该文件
"""

import json
import os
import shutil
import sys
import time
from pathlib import Path

HOME = Path.home()
CFG_DIR = HOME / ".codebuddy"
HOOKS_DIR = CFG_DIR / "hooks"
SETTINGS = CFG_DIR / "settings.json"
FLAG = CFG_DIR / ".persona-on"
CMD = f"python3 {HOOKS_DIR / 'whale_persona_inject.py'}"
SKILL_DIR = Path(__file__).resolve().parent.parent
SRC = SKILL_DIR / "scripts" / "whale_persona_inject.py"


def load_settings() -> dict:
    if not SETTINGS.exists():
        return {}
    try:
        return json.loads(SETTINGS.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        sys.exit(f"{SETTINGS} 不是合法 JSON，先修好再装")


def save_settings(cfg: dict) -> None:
    SETTINGS.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def is_registered(cfg: dict, event: str) -> bool:
    for entry in cfg.get("hooks", {}).get(event, []):
        for h in entry.get("hooks", []):
            if h.get("command") == CMD:
                return True
    return False


def install() -> None:
    HOOKS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SRC, HOOKS_DIR / "whale_persona_inject.py")
    os.chmod(HOOKS_DIR / "whale_persona_inject.py", 0o755)

    cfg = load_settings()
    if SETTINGS.exists():
        backup = SETTINGS.with_suffix(f".json.bak-{time.strftime('%Y%m%d%H%M%S')}")
        shutil.copy2(SETTINGS, backup)
        print(f"已备份原设置: {backup}")

    hooks = cfg.setdefault("hooks", {})
    added = []
    for event, matcher in (("SessionStart", "startup"), ("UserPromptSubmit", None)):
        arr = hooks.setdefault(event, [])
        if is_registered(cfg, event):
            continue
        entry: dict = {"hooks": [{"type": "command", "command": CMD, "timeout": 15}]}
        if matcher:
            entry = {"matcher": matcher, **entry}
        arr.append(entry)
        added.append(event)

    save_settings(cfg)
    print(f"hook 已写入: {HOOKS_DIR / 'whale_persona_inject.py'}")
    print(f"注册事件: {', '.join(added) if added else '已存在，跳过'}")
    print("\n生效方式: 重启 WorkBuddy 或新建会话（settings.json 不热加载）")
    print("默认不注入。开关:")
    print(f"  touch {FLAG}    # 打开（每次提问都注入）")
    print(f"  rm {FLAG}       # 关闭")
    print("若环境变量里能读到模型名且含 deepseek，无需开关也会注入。")


def uninstall() -> None:
    cfg = load_settings()
    hooks = cfg.get("hooks", {})
    for event in list(hooks.keys()):
        kept = []
        for entry in hooks[event]:
            entry["hooks"] = [h for h in entry.get("hooks", []) if h.get("command") != CMD]
            if entry["hooks"]:
                kept.append(entry)
        if kept:
            hooks[event] = kept
        else:
            hooks.pop(event)
    if not hooks and "hooks" in cfg:
        cfg.pop("hooks")
    save_settings(cfg)
    hook_file = HOOKS_DIR / "whale_persona_inject.py"
    if hook_file.exists():
        hook_file.unlink()
    print("已卸载 hook 与注册项。重启后彻底失效。")


def status() -> None:
    cfg = load_settings()
    print(f"hook 文件: {'存在' if (HOOKS_DIR / 'whale_persona_inject.py').exists() else '缺失'}")
    for event in ("SessionStart", "UserPromptSubmit"):
        print(f"{event}: {'已注册' if is_registered(cfg, event) else '未注册'}")
    print(f"开关文件: {'打开' if FLAG.exists() else '关闭'}")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--uninstall":
        uninstall()
    elif arg == "--status":
        status()
    else:
        install()
