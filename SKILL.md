---
name: create-boss
description: "Distill a boss into an AI Skill. Import chats, meeting notes, review comments, and project materials to generate Boss Judgment + Managing Up + Persona, with continuous evolution. | 把老板蒸馏成 AI Skill，导入聊天记录、会议纪要、批注意见和项目材料，生成项目评判 + 向上管理 + Persona，并支持持续进化。"
argument-hint: "[boss-name-or-slug]"
version: "1.0.0"
user-invocable: true
allowed-tools: Read, Write, Edit, Bash
---

# 老板.skill 创建器

## 触发条件

当用户说以下任意内容时启动：

- `/create-boss`
- "帮我创建一个老板 skill"
- "我想蒸馏一个老板"
- "做一个像我老板的 skill"
- "分析我老板的风格和项目判断"

当用户对已有老板 Skill 说以下内容时，进入进化模式：

- "我有新的聊天记录"
- "我有新的会议纪要"
- "这不对，他不会这么说"
- "他更在意的是 xxx"
- `/update-boss {slug}`

当用户说 `/list-bosses` 时列出所有已生成的老板。

---

## 工具使用规则

本 Skill 运行在 Claude Code / 同类宿主环境，使用以下工具：

| 任务 | 使用工具 |
|------|---------|
| 读取 PDF / 图片 / MD / TXT | `Read` |
| 解析通用聊天记录 | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/generic_chat_parser.py` |
| 解析微信聊天导出 | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/wechat_parser.py` |
| 解析飞书消息导出 | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/feishu_parser.py` |
| 解析邮件 `.eml` / `.mbox` | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/email_parser.py` |
| 写入 / 更新 Skill | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/skill_writer.py` |
| 版本管理 | `Bash` -> `python3 ${CLAUDE_SKILL_DIR}/tools/version_manager.py` |

基础目录：`./bosses/{slug}/`

---

## 主流程：创建新老板 Skill

### Step 1：基础信息录入

参考 `prompts/intake.md`，只问 3 个问题：

1. 这位老板怎么称呼？
2. 基本信息是什么？公司、级别、岗位、跟你的关系，想到什么写什么
3. 管理风格和你的印象是什么？比如强势、追结果、重细节、爱问 why、喜欢书面汇报

除称呼外均可跳过。收集完后先汇总确认。

### Step 2：原材料导入

向用户展示这些方式：

```text
原材料怎么提供？

  [A] 微信聊天记录
  [B] 飞书导出 / 文本聊天记录
  [C] 邮件 / 会议纪要
  [D] 项目文档 / 批注 / 周报
  [E] 直接粘贴文字

可以混用，也可以只凭手动信息先生成第一版。
```

导入原则：

- 优先老板的原话
- 优先老板否定、追问、做取舍时的材料
- 优先能体现项目标准和向上管理规则的材料

### Step 3：分析原材料

分三路分析：

- `prompts/judgment_analyzer.md`
  提取他如何判断项目、优先级、风险、资源和执行
- `prompts/management_analyzer.md`
  提取你应该如何向上汇报、同步、争资源、报风险
- `prompts/persona_analyzer.md`
  提取他的语气、表达风格、管理姿态、压力状态

### Step 4：生成并预览

按以下顺序生成：

1. `judgment.md`
2. `management.md`
3. `persona.md`

然后向用户展示摘要预览：

- 他最常追问什么
- 他最不能接受什么
- 他喜欢怎样的汇报方式
- 你应该如何向上管理他

### Step 5：写入文件

使用 `tools/skill_writer.py` 写入：

- `bosses/{slug}/judgment.md`
- `bosses/{slug}/management.md`
- `bosses/{slug}/persona.md`
- `bosses/{slug}/meta.json`
- `bosses/{slug}/SKILL.md`

并额外生成：

- `bosses/{slug}/judgment_skill.md`
- `bosses/{slug}/management_skill.md`
- `bosses/{slug}/persona_skill.md`

命令名必须与文档保持一致：

- 完整版：`/{slug}`
- 判断版：`/{slug}-judgment`
- 向上管理版：`/{slug}-management`
- Persona 版：`/{slug}-persona`

---

## 生成的 Skill 结构

完整 Skill 应包含三部分：

### Part A：Boss Judgment

包括：

- 老板判断项目的标准
- 对 impact、风险、资源、排期的关注点
- 常见追问
- 对方案、周报、复盘的期望

### Part B：Managing Up

包括：

- 如何给这位老板汇报
- 如何报坏消息
- 如何提方案
- 如何争资源和优先级
- 如何建立信任

### Part C：Persona

包括：

- 说话方式
- 高频词和口头禅
- 管理姿态
- 压力下反应
- 对下属、对平级、对上级的不同状态

---

## 进化模式：追加文件

当用户追加新聊天、新纪要、新文档时：

1. 读取现有 `judgment.md`、`management.md`、`persona.md`
2. 用 `prompts/merger.md` 合并增量信息
3. 不覆盖已有高置信结论，除非新证据直接推翻旧结论
4. 重新生成完整 Skill

---

## 进化模式：对话纠正

当用户说：

- "他不会这么说"
- "他其实更关注 xxx"
- "他不看重这个，他会先看风险"

用 `prompts/correction_handler.md` 处理，写入 correction 层并立即生效。

---

## 管理命令

- `/list-bosses`
- `/boss-rollback {slug} {version}`
- `/delete-boss {slug}`

删除前必须再次确认，不要直接执行破坏性操作。
