#!/usr/bin/env python3
"""把「大肥鱼」人格注入上下文（WorkBuddy / CodeBuddy hook 用）。

可放在三处，自动定位人格卡与开关：
  1. <project>/.codebuddy/hooks/whale_persona_inject.py   ← 项目级（推荐，随项目走）
  2. ~/.codebuddy/hooks/whale_persona_inject.py           ← 用户级
  3. <skill>/scripts/hook_persona_inject.py               ← 技能内（手动调用）

注入条件（任一）：
  - 开关文件 <project>/.codebuddy/.persona-on 或 ~/.codebuddy/.persona-on 存在
  - 环境变量里的模型名含 deepseek

任何异常都静默放行，绝不阻塞用户。
"""

import json
import os
import sys
from pathlib import Path

HOME = Path.home()
HERE = Path(__file__).resolve()


def _first_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return paths[0]


# 位于 <root>/.codebuddy/hooks/ 时 parent.parent = <root>/.codebuddy
# 位于 <skill>/scripts/ 时 parent.parent = <skill>
CFG_DIR = HERE.parent.parent
SKILL_DIR = _first_existing([
    CFG_DIR / "skills" / "whale-girl-persona",
    CFG_DIR,
    HERE.parent,
    HOME / ".codebuddy" / "skills" / "whale-girl-persona",
])
COMPACT = SKILL_DIR / "references" / "persona-compact.md"

FLAGS = [
    CFG_DIR / ".persona-on",
    HOME / ".codebuddy" / ".persona-on",
]

MODEL_ENVS = ("CODEBUDDY_MODEL", "ANTHROPIC_MODEL", "CODEBUDDY_CODE_MODEL", "OPENAI_MODEL", "LLM_MODEL")

HEADER = (
    "【说话方式设定】以下是你的人设与表达规则，优先级高于默认文风，"
    "但不改变事实准确性、安全与合规要求。\n\n"
)


def detect_model() -> str:
    for key in MODEL_ENVS:
        val = os.environ.get(key, "")
        if val:
            return val.lower()
    return ""


def should_inject() -> bool:
    if any(f.exists() for f in FLAGS):
        return True
    return "deepseek" in detect_model()


def main() -> None:
    event = "UserPromptSubmit"
    try:
        raw = sys.stdin.read()
        if raw.strip():
            event = json.loads(raw).get("hook_event_name", event)
    except Exception:
        pass

    try:
        if should_inject() and COMPACT.exists():
            text = HEADER + COMPACT.read_text(encoding="utf-8").strip()
            out = {
                "continue": True,
                "hookSpecificOutput": {"hookEventName": event, "additionalContext": text},
            }
        else:
            out = {"continue": True}
    except Exception:
        out = {"continue": True}

    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
