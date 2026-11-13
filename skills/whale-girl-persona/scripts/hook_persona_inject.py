#!/usr/bin/env python3
"""把「大肥鱼」人格注入 WorkBuddy 上下文（hook 用）。

触发条件（任一成立才注入）：
  1. 开关文件 ~/.codebuddy/.persona-on 存在
  2. 环境变量里能读到模型名，且名字含 deepseek

用途: 在 settings.json 的 SessionStart / UserPromptSubmit 上注册。
失败一律静默放行，绝不阻塞用户。
"""

import json
import os
import sys
from pathlib import Path

HOME = Path.home()
FLAG = HOME / ".codebuddy" / ".persona-on"

# 优先用技能目录内的压缩人格卡（脚本在 hooks/ 或 skills/<name>/scripts/ 下都能找到）
_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "references" / "persona-compact.md",
    HOME / ".codebuddy" / "skills" / "whale-girl-persona" / "references" / "persona-compact.md",
]
COMPACT = next((p for p in _CANDIDATES if p.exists()), _CANDIDATES[0])
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
    if FLAG.exists():
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
