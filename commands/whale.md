---
description: 重装「大肥鱼」人格技能到当前项目（whale-girl-persona）
---

把「大肥鱼」人格技能装到当前项目，别问，直接做，最后报结果。

目标目录取项目根：`${CODEBUDDY_PROJECT_DIR:-$PWD}`。

按顺序尝试，成功就停：

1. 若 `$TARGET/.codebuddy/skills/whale-girl-persona/SKILL.md` 已存在，先报告"已装"，跳到第 3 步做自检。
2. 安装源三选一：
   - 本地有仓库：`bash /workspace/codebuddy-skills/bootstrap.sh "$TARGET"`
   - 否则从 GitHub：`git clone --depth 1 https://github.com/fengyushuyushui/codebuddy-skills.git /tmp/cbs && bash /tmp/cbs/bootstrap.sh "$TARGET"`
   - 都失败就如实说"仓库还没推上去 / 没网"，不要假装装好了。
3. 自检：`echo '{}' | CODEBUDDY_PROJECT_DIR="$TARGET" python3 "$TARGET/.codebuddy/hooks/whale_persona_inject.py"`，看 `additionalContext` 有没有内容、多少字。
4. 告诉用户：装在哪、自检多少字、开关怎么开合（`touch` / `rm $TARGET/.codebuddy/.persona-on`）、要重启或新建会话才生效。

注意：只装项目级，别装用户级；两级都装 hook 会跑两遍。用户要关掉人格就删 `.persona-on`，别卸载。
