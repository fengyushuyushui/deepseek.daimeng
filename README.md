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

# 推荐：装成项目级（随项目走，云电脑新对话不丢）
bash codebuddy-skills/bootstrap.sh /path/to/your/project

# 新环境、手里只有网络（需要仓库已公开）
curl -fsSL https://raw.githubusercontent.com/fengyushuyushui/codebuddy-skills/main/bootstrap.sh | bash -s -- /path/to/your/project

# 或者：装成用户级（所有项目生效，但沙箱 HOME 可能被销毁）
cp -r codebuddy-skills/skills/whale-girl-persona ~/.codebuddy/skills/
```

`bootstrap.sh` 会连技能、hook、`settings.json`、开关一起装好，最后自检注入字数。装完项目里还有个 `/whale` 斜杠命令，以后重装就一句话。

也可以只解压 `whale-girl-persona.skill`（zip 格式）到 `.codebuddy/skills/` 或 `~/.codebuddy/skills/` 下。

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

#### 用法四：WorkBuddy 里每轮自动带人格（hook）

不想每次手动喊"用大肥鱼说话"，就把它挂到 `UserPromptSubmit` 上——每轮往上下文塞一张 970 字的压缩人格卡，成本可以忽略。

**要装在项目里，不是 HOME 里**（云电脑的 `~/.codebuddy` 会随实例没）：

```bash
bash install-to-project.sh            # 装进当前项目的 .codebuddy/（推荐）
bash install-to-project.sh --user     # 或装到 ~/.codebuddy，所有项目生效
bash install-to-project.sh /path/to/proj

touch .codebuddy/.persona-on          # 开
rm .codebuddy/.persona-on             # 关
```

装完要**重启 WorkBuddy 或新建会话**（`settings.json` 不热加载）。别项目级和用户级都装——hook 是叠加的，会注入两遍。

#### 云电脑里新开对话会丢吗

会，如果你装在 HOME 里。三层是这么分的：

| 层 | 位置 | 新对话还在吗 | 说明 |
|---|---|---|---|
| 项目级 | `<项目>/.codebuddy/` | ✅ 同一个项目就在 | 推荐，随项目走，优先级高于用户级 |
| 用户级 | `~/.codebuddy/` | ⚠️ 看实例 | 沙箱/云电脑 HOME 可能被销毁 |
| GitHub | 仓库本身 | ✅ 永远 | 真理源，新环境 clone 一次就回来 |

恢复只要一条：

```bash
git clone https://github.com/fengyushuyushui/codebuddy-skills.git
bash codebuddy-skills/install-to-project.sh /path/to/project
```

换到**另一个项目目录**时，项目级配置不在那儿，重跑一次 install 就行。

最省心的其实是 WorkBuddy 账号级的「给 WorkBuddy 的指令」：跟沙箱无关，把 `persona-compact.md` 整段粘进去，所有对话自动带。缺点是全局，干活时得手动改回来。

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
