<div align="center">

# 老板.skill

> *"不是把老板变成聊天机器人，而是把他判断项目的脑回路、批评方式和向上管理规则沉淀下来。"*

你的老板开会总爱追着问 impact、风险和 owner？  
他一句“这个先别做”背后其实有一整套判断标准？  
你总感觉自己不是不会做事，而是不知道该怎么向上同步、怎么报风险、怎么要资源？

**把老板的聊天记录、会议纪要、批注和项目材料蒸馏成 Skill。**

它不仅像老板一样说话，还会：

- 用老板的标准评判项目、方案和执行
- 复现老板开会、评审、追进度时的风格
- 教你如何向上汇报、如何提方案、如何要资源、如何报坏消息

[数据来源](#支持的数据来源) · [安装](#安装) · [使用](#使用) · [效果示例](#效果示例) · [结构](#生成的-skill-结构) · [详细安装说明](INSTALL.md) · [English](README_EN.md)

</div>

---

## 支持的数据来源

| 来源 | 聊天记录 | 文档/批注 | 会议纪要 | 备注 |
|------|:-------:|:---------:|:-------:|------|
| 微信聊天记录 | ✅ | — | — | 导出 txt/html/csv |
| 飞书消息导出 | ✅ | ✅ | ✅ | JSON/txt/复制文本 |
| 邮件 `.eml` / `.mbox` | ✅ | ✅ | — | 可提取老板邮件风格 |
| Markdown / 文本 | ✅ | ✅ | ✅ | 会议纪要、项目复盘、批注 |
| PDF / 图片截图 | ✅ | ✅ | ✅ | 手动上传 |
| 直接粘贴文字 | ✅ | ✅ | ✅ | 复制会议记录、IM 对话、评审意见 |

---

## 安装

### Claude Code

```bash
# 安装到当前项目（在 git 仓库根目录执行）
mkdir -p .claude/skills
git clone https://github.com/vogtsw/boss-skills.git .claude/skills/create-boss

# 或安装到全局
git clone https://github.com/vogtsw/boss-skills.git ~/.claude/skills/create-boss
```

### OpenClaw

```bash
git clone https://github.com/vogtsw/boss-skills.git ~/.openclaw/workspace/skills/create-boss
```

### 依赖

```bash
pip3 install -r requirements.txt
```

---

## 使用

在 Claude Code 中输入：

```text
/create-boss
```

按提示输入老板称呼、基本信息、管理风格，再导入聊天记录、邮件、纪要或文档材料。

完成后可用：

| 命令 | 说明 |
|------|------|
| `/list-bosses` | 列出所有老板 Skill |
| `/{slug}` | 调用完整 Skill |
| `/{slug}-judgment` | 仅老板的项目评判逻辑 |
| `/{slug}-management` | 仅向上管理建议 |
| `/{slug}-persona` | 仅老板的说话与行为风格 |
| `/boss-rollback {slug} {version}` | 回滚历史版本 |
| `/delete-boss {slug}` | 删除 |

---

## 效果示例

> 输入：`某大厂 技术总监 我的直属老板 追结果 重 owner 控风险 先结论后背景`

**场景一：项目评审**

```text
用户       > 帮我看看这个新项目方案

老板.skill > 先说结论，这个项目到底解决什么问题？
          > 如果这个季度不做，损失是什么？
          > owner 是谁？风险怎么兜？这三件事不清楚，方案不能过。
```

**场景二：报坏消息**

```text
用户       > 项目延期了，我怎么跟老板说

老板.skill > 不要先解释困难，先讲事实。
          > 你应该这样说：
          > 1. 现在延期了多少
          > 2. 影响范围是什么
          > 3. 你已经做了什么补救
          > 4. 你需要我拍板什么
```

**场景三：争资源**

```text
用户       > 我想多要一个前端和一个测试

老板.skill > 不要说“人手不够”。
          > 你要讲关键链路卡在哪，不补人会影响哪个结果，为什么这个季度必须做。
```

---

## 生成的 Skill 结构

每个老板 Skill 由三部分组成：

| 部分 | 内容 |
|------|------|
| **Part A — Boss Judgment** | 他如何评判项目、方案、进度、风险、资源和人 |
| **Part B — Managing Up** | 你应如何向上同步、报风险、提方案、争资源、争优先级 |
| **Part C — Persona** | 他的表达风格、情绪逻辑、管理姿态、压力状态 |

运行逻辑：

`收到问题 -> Persona 判断语气与姿态 -> Judgment 评项目 -> Management 给出向上管理动作 -> 用老板的风格输出`

---

## 适用场景

- 项目评审前，先让 Skill 模拟老板会挑什么问题
- 周报/汇报前，先检查信息是不是老板关心的格式
- 资源申请前，先判断怎样说更容易拿到支持
- 出现延期/风险时，先练习怎么向上报坏消息
- 学习老板的管理风格与决策模式

---

## 目录结构

```text
boss-skills/
├── SKILL.md
├── prompts/
│   ├── intake.md
│   ├── judgment_analyzer.md
│   ├── management_analyzer.md
│   ├── persona_analyzer.md
│   ├── judgment_builder.md
│   ├── management_builder.md
│   ├── persona_builder.md
│   ├── merger.md
│   └── correction_handler.md
├── tools/
│   ├── generic_chat_parser.py
│   ├── wechat_parser.py
│   ├── feishu_parser.py
│   ├── email_parser.py
│   ├── skill_writer.py
│   └── version_manager.py
├── bosses/
│   └── example-laozhou/
├── requirements.txt
└── INSTALL.md
```

---

## 注意事项

- 原材料质量决定 Skill 质量：老板真实聊天记录、评审意见、会议纪要越多越好
- 最有价值的材料通常是：他批评项目的时候、问问题的时候、做取舍的时候
- 如果只给语气，没有项目材料，Skill 会更像“会说话”，不一定像“会判断”
- 这是第一版骨架，后续可以再补企业 IM 自动采集、会议纪要结构化抽取等能力
