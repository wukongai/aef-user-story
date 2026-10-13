# AEF User Story

0.4.0：将产品定义、口述需求和持续反馈整理为可持续维护的故事库。一条 Story 一张独立卡片，一个总索引按 Epic 归类。

## 直接使用

读取 SKILL.md 后，可以直接说：

- “根据这份产品定义建立故事库，先列全貌。”
- “增加一条故事，归入 EPIC-001。”
- “只完善 US-003 的边界验收，其他卡片不变。”
- “修改 US-003 的目标，保留编号和版本历史。”
- “输出 US-003 当前版本的引用，供后续迭代选择。”

可以独立调用，不要求先运行 Definition。新增故事不自动承诺进入迭代；本 Skill 不制作地图、迭代计划、产品详细设计、技术设计或代码。

## 文件结构

```text
故事库/
├── index.md                 # Epic 分组、故事链接和状态
├── stories/
│   ├── US-001.md            # 一句话故事＋1、2、3条验收
│   └── US-002.md
├── .story-data/
│   ├── US-001.json          # 此故事的完整修订与确认历史
│   └── US-002.json
└── .story-library.json       # 库身份、背景和 Epic
```

用户阅读 Markdown 卡片：标题、一句话故事、1、2、3条验收条件；不铺陈确认、修订和内部字段。Agent 同步维护独立数据文件，其中保留完整版本、确认记录与验收ID。索引不复制故事全文。新增或修改只改变对应卡片、数据和必要的索引；无关卡片不重写。

编号不变，内容修订追加，确认绑定具体版本。只改验收不增加 Story 修订；Story 改动后旧验收需要复审。迭代只记录 Story/AC 的 ID 与版本，通过历史读取恢复当时内容。

查看[故事库使用说明](references/story-library.md)、[实际总索引](examples/05-story-library/library/index.md)、[一张故事卡](examples/05-story-library/library/stories/US-001.md)和[局部修改示例](examples/05-story-library/README.md)。

## 兼容与验证

旧 user-story.md + story-card.json（v1/v2）和 0.3 集中 workspace 保留原能力。迁移预览新目录，保留旧包与编号、历史、确认记录，不偷偷迁移。

```bash
python3 -B -m unittest discover -s tests -p 'test_*.py'
python3 -B scripts/self_test.py
python3 -B scripts/story_library.py validate examples/05-story-library/library --previous examples/05-story-library/before
```

第一条运行全部回归；第二条检查旧格式；第三条验证故事库及历史保留。工具仅使用 Python 标准库，无网络调用；CLI 输出候选计划，不自动写项目。验证不证明产品价值或人工批准真实性。

[0.3 持续维护核心](references/continuous-maintenance.md)、[旧版中文手册](docs/tutorials/aef-user-story-user-manual.zh-CN.md)和[旧版交付话术](docs/guides/user-delivery-messages.zh-CN.md)仍保留。本文为新版入口，旧手册的集中包保存方式仅用于兼容模式。

本版对应 v0.4.0，变化与验证见 [发布说明](docs/releases/v0.4.0.md)。父包快照和已有安装不会自动升级。MIT 许可保留。
