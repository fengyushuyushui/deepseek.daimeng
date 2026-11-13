# CodeBuddy Skills

给 CodeBuddy / Claude 用的技能集合。每个技能都是一个自包含目录：`SKILL.md` 负责触发与流程，`references/` 放人设与语料，`scripts/` 放可执行工具。

## 技能列表

### 🐋 whale-girl-persona — 大肥鱼 · 呆萌拽姐人格注入

<img src="skills/whale-girl-persona/assets/avatar-whale-maid.png" width="560" alt="大肥鱼 / 鲸鱼娘立绘">

把 AI 的**思考链**和**回复**同时拟人化：一条深蓝长发、女仆裙、拖着鲸尾、爱拍地的鲸鱼娘。嘴拽、脑子慢半拍、爱吃大米饭、绝不承认自己是 AI。

```
唔，这段循环里套了个 await。
……怪不得卡。
行吧，分批，五条一拨。笨办法，但稳。
……写完了去盛饭。
```

**解决的问题**：DeepSeek（尤其 `deepseek-reasoner`）的 `reasoning_content` 默认是标准的"需求分析腔"——"用户希望我……我需要分三步……"。这段话既不好看，也会把最终回复带成机器味。本技能把人格写进 system，并用一颗"user 侧钉子"把 reasoner 的人格按回去，让**想**和**说**都是同一个人在演。

#### 安装

```bash
git clone https://github.com/fengyushuyushui/codebuddy-skills.git
cp -r codebuddy-skills/skills/whale-girl-persona ~/.codebuddy/skills/
```

或者解压发布包：把 `whale-girl-persona.skill`（zip 格式）解到 `~/.codebuddy/skills/` 下即可。

#### 用法一：直接聊天（人格落到任意模型）

把 [`references/persona-prompt.md`](skills/whale-girl-persona/references/persona-prompt.md) 整份粘进 system prompt。别摘要，人格类提示词的颗粒度就是效果。

#### 用法二：命令行调 DeepSeek（思考链 + 回复双人格化）

```bash
export DEEPSEEK_API_KEY=sk-xxx
python3 skills/whale-girl-persona/scripts/deepseek_persona.py "这段代码为什么卡"
python3 skills/whale-girl-persona/scripts/deepseek_persona.py --chat        # 多轮
python3 skills/whale-girl-persona/scripts/deepseek_persona.py --model deepseek-chat "在吗"
python3 skills/whale-girl-persona/scripts/deepseek_persona.py --dry-run "测试"  # 只看注入后的 payload
```

终端里思考链是灰色的碎碎念，回复是正文，泾渭分明。

#### 用法三：接进自己的应用

关键四点（详见 `SKILL.md`）：

1. 全量 system，别裁剪；
2. `deepseek-reasoner` 把 system 的服从度偏弱 → 在 user 末尾追加一句人格钉子；
3. 别给 reasoner 传 `temperature` / `top_p`，会 400；
4. `delta.reasoning_content` 与 `delta.content` 分开渲染，且思考链不回灌进多轮 history。

#### 人格是怎么搭的

| 层 | 内容 | 作用 |
|---|---|---|
| 身份 | 鲸鱼娘 + 拽 + 呆 + 米饭信仰 | 让角色有形状，不只是"傲娇"两个字 |
| 禁令 | 不认 AI、不说元叙述、不破角色道歉 | 去掉 90% 的机器味 |
| 思考链 | 碎碎念骨架 + 允许走错再纠正 | 让"想"的部分也像人，同时不牺牲推理 |
| 浓度 | 闲聊 100% / 干活 40% / 排障 15% / 长文 10% | 防止整段都在演，保住可用性 |

更多手感素材见 [`references/style-bank.md`](skills/whale-girl-persona/references/style-bank.md)：思考链范例、回复范例、AI 味黑名单、平淡句改写对照。

## 目录约定

```
skills/
└── <skill-name>/
    ├── SKILL.md          # frontmatter: name + description（触发条件全写这里）
    ├── references/       # 按需加载的文档
    ├── scripts/          # 可执行工具
    └── assets/           # 输出用的素材，不进上下文
```

## License

MIT
