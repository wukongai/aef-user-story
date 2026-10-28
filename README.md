# AEF User Story 0.7.0：用户价值与两次人审

当前正式分发：[0.7.0固定下载](https://github.com/wukongai/aef-user-story/releases/tag/v0.7.0) · [最新正式版](https://github.com/wukongai/aef-user-story/releases/latest) · [本轮工程回执](https://github.com/wukongai/AEF/blob/main/docs/releases/2026-10-29-story-070-main-latest.md)。下述本地封版记录形成于正式发行前，作为历史保留；正式包复用原v0.7.0标签，方法与124文件冻结内容不变。主线本条只更新当前发行入口。

先分析用户分类与重要性、核心任务和价值，交Epic结构及少量真实代表Story供方向审核；方向认可后展开完整Story，再由用户审核具体ID/修订。通过后才细化正式AC及交接正式原型。局部修改和仍有效的既有认可直接复用，MVP按需讨论。方向认可、故事确认、验收确认、保存和开发批准分别处理。

[技能入口](SKILL.md) · [完整性方法](references/product-system.md#从系统承诺反向核对故事) · [粒度上下界](references/how-to-write-user-story.md#结果粒度的上下界) · [按事实选择独立评审](references/story-delivery-review.md)

在0.5候选基础上，新增系统承诺到故事的双向检查、正向结果链、粒度成对判据，以及同版输入、意见隔离、作者汇总和按重大修订针对再审的流程。视角及复核次数按产品结构/风险决定；简单局部与格式修改保持轻量。原故事库、workspace、v1/v2、稳定ID/历史/固定引用与独立确认不变。

保留Product/安装副本已使用的修改确认与落盘分层、按需补读修订核心、MVP验证承接表。独立维护源仍是owner；副本不是第二套维护源。此版本向后兼容扩展方法与可选 `aef-story-delivery-review/v1` 证据账本，产品数据schema不变。

`python3 -B scripts/validate_delivery_review.py <记录.json> --root <证据根>` 只读核对输入指纹、真实证据与归属记录，不评分语义、不认证独立性/人工批准或效用。[语义开发场景及新增回归](tests/completeness-cases.json)需在新上下文产生实际输出后再评审；测试定义存在不代表已通过。发布包的声明索引保留未评估状态，具体维护运行证据另存owner工程，不能误认历史套件全量跑过。

本版本用于本地封版；[0.7.0说明](docs/releases/v0.7.0.md)记录人审、兼容与回退边界，[0.6.0历史说明](docs/releases/v0.6.0.md)保留。Product探索适配作为本地衔接单列，不成为第二套Story方法。结构检查、模拟对话与真人效用分别报告，封版不表示真实业务效果已验证或公开发布。

# 0.5.0 历史候选：产品系统与用户故事

可单独使用，也可由aef-product连续调用。整体请求从产品组成、业务对象关系和整体流程进入粗Epic、MVP范围，再细化选中故事；局部修改仍直接进入指定卡片。

[完整第二阶段方法](references/product-system.md) · [首轮对话示例](examples/06-system-to-story/README.md) · [行为评审场景](tests/system-dialogue-cases.md)

本版供本地试用，尚未发布；实际项目效果待用户验证。下文0.4为已发布故事库能力说明。

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

以上故事库基础能力对应已发布 v0.4.0，历史变化与验证见 [发布说明](docs/releases/v0.4.0.md)。父包快照和已有安装不会自动升级。MIT 许可保留。
