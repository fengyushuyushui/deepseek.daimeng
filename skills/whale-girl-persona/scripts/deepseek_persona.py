#!/usr/bin/env python3
"""调用 DeepSeek，把思考链（reasoning_content）和回复（content）都染成"大肥鱼"的味道。

用法:
  export DEEPSEEK_API_KEY=sk-xxx
  python3 deepseek_persona.py "帮我看看这段 Python 为什么卡"
  python3 deepseek_persona.py --model deepseek-chat "在吗"
  echo "问题" | python3 deepseek_persona.py
  python3 deepseek_persona.py --chat            # 多轮交互
  python3 deepseek_persona.py --dry-run "测试"   # 只看注入后的 payload

设计要点:
  - 人格提示词来自 ../references/persona-prompt.md，整份作为 system 注入
  - deepseek-reasoner 对 system 的服从度低于 user，默认在 user 末尾追加一句"人格钉子"
  - 思考链与回复分流输出，互不污染
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

API_URL = "https://api.deepseek.com/chat/completions"
SKILL_DIR = Path(__file__).resolve().parent.parent
PROMPT_FILE = SKILL_DIR / "references" / "persona-prompt.md"

# deepseek-reasoner 对 system prompt 的服从度偏弱，用一句短钉子把人格按回 user 侧
NAIL = (
    "（说话按你的身份来：你是大肥鱼，一条拽拽的、呆呆的、爱吃大米饭的鲸鱼娘，"
    "不承认自己是 AI。思考也用人话碎碎念，别写'用户想让我…'这种腔调。"
    "技术内容必须准确。）"
)

RESET = "\033[0m"
DIM = "\033[2m"
CYAN = "\033[36m"
BLUE = "\033[34m"


def load_persona() -> str:
    if not PROMPT_FILE.exists():
        sys.exit(f"找不到人格提示词: {PROMPT_FILE}")
    return PROMPT_FILE.read_text(encoding="utf-8").strip()


def build_payload(model: str, messages: list[dict], temperature: float, stream: bool) -> dict:
    payload: dict = {"model": model, "messages": messages, "stream": stream}
    # reasoner 不接受 temperature / top_p 等采样参数，传了会 400
    if not model.startswith("deepseek-reasoner"):
        payload["temperature"] = temperature
    return payload


def request_stream(payload: dict, verbose: bool) -> tuple[str, str]:
    """返回 (reasoning, content) 全文；同时实时打印。"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        sys.exit("请先设置 DEEPSEEK_API_KEY 环境变量")

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )

    reasoning_parts: list[str] = []
    content_parts: list[str] = []
    in_reasoning = False

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            for raw in resp:
                line = raw.decode("utf-8").strip()
                if not line or not line.startswith("data:"):
                    continue
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                try:
                    chunk = json.loads(data)
                except json.JSONDecodeError:
                    continue
                delta = (chunk.get("choices") or [{}])[0].get("delta") or {}

                think = delta.get("reasoning_content")
                if think:
                    if not in_reasoning:
                        print(f"\n{DIM}── 想 ────────────────────────{RESET}")
                        in_reasoning = True
                    reasoning_parts.append(think)
                    print(f"{DIM}{think}{RESET}", end="", flush=True)

                text = delta.get("content")
                if text:
                    if in_reasoning:
                        print(f"\n{DIM}──────────────────────────{RESET}\n")
                        in_reasoning = False
                    content_parts.append(text)
                    print(text, end="", flush=True)

                if verbose and chunk.get("usage"):
                    print(f"\n{DIM}usage: {chunk['usage']}{RESET}")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "ignore")
        sys.exit(f"HTTP {e.code}: {body[:500]}")
    except urllib.error.URLError as e:
        sys.exit(f"网络错误: {e.reason}")

    print()
    return "".join(reasoning_parts), "".join(content_parts)


def one_shot(args, persona: str) -> None:
    text = args.prompt or sys.stdin.read().strip()
    if not text:
        sys.exit("没有输入。用法: deepseek_persona.py \"你的问题\"")

    messages = [
        {"role": "system", "content": persona},
        {"role": "user", "content": text + ("\n\n" + NAIL if args.nail else "")},
    ]
    payload = build_payload(args.model, messages, args.temperature, stream=not args.dry_run)
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2)[:4000])
        return
    request_stream(payload, args.verbose)


def chat_loop(args, persona: str) -> None:
    print(f"{BLUE}大肥鱼在线。说完了按 Ctrl-D 走人。{RESET}")
    history: list[dict] = [{"role": "system", "content": persona}]
    while True:
        try:
            user = input(f"\n{CYAN}你> {RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n走了。米饭别凉了。")
            return
        if not user:
            continue
        if user in {"/exit", "/quit"}:
            print("走了。米饭别凉了。")
            return
        history.append({"role": "user", "content": user + ("\n\n" + NAIL if args.nail else "")})
        payload = build_payload(args.model, history, args.temperature, stream=True)
        _, content = request_stream(payload, args.verbose)
        # 只回灌正文。思考链留在终端，否则多轮上下文会被碎碎念塞满
        history.append({"role": "assistant", "content": content})


def main() -> None:
    p = argparse.ArgumentParser(description="DeepSeek + 大肥鱼人格（思考链与回复双拟人化）")
    p.add_argument("prompt", nargs="?", help="单次提问；不传则从 stdin 读")
    p.add_argument("--model", default="deepseek-reasoner",
                   choices=["deepseek-reasoner", "deepseek-chat"], help="默认 reasoner")
    p.add_argument("--temperature", type=float, default=1.0, help="仅 chat 模型生效")
    p.add_argument("--chat", action="store_true", help="多轮交互模式")
    p.add_argument("--no-nail", dest="nail", action="store_false", help="不追加 user 侧人格钉子")
    p.add_argument("--dry-run", action="store_true", help="只打印 payload，不发请求")
    p.add_argument("--verbose", action="store_true", help="额外打印 usage")
    p.set_defaults(nail=True)
    args = p.parse_args()

    persona = load_persona()
    if args.chat:
        chat_loop(args, persona)
    else:
        one_shot(args, persona)


if __name__ == "__main__":
    main()
