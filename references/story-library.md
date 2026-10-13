# 独立故事库：一条 Story 一张卡

0.4.0 新建需求默认使用此结构。已有 StoryCard 或 story-workspace.json 保持可读；迁移需明确预览并选择新目录，不删除旧包。
可以独立使用，不依赖 Definition、地图、迭代或 Task Skill。随时从已知产品背景增加故事，或只完善一张卡。

## 日常看到的结构
```text
用户故事库/
├── index.md
├── stories/
│   ├── US-001.md
│   └── US-002.md
├── .story-library.json
└── .story-data/
    ├── US-001.json
    └── US-002.json
```

index.md 按 Epic 展示故事链接、标题、修订与确认状态，有“未归类”分组；不复制故事全文。
每张 Markdown 卡先用一句“作为……我希望……从而……”呈现故事，再用1、2、3列出当前验收结果；必要的业务约束才追加补充说明。用户、场景、目标、价值不重复拆成字段，AC不逐条铺陈类型和修订。退役验收仅保留在历史数据中。
.story-data 下也是一条故事一个独立文件，存其完整内容历史与审批事件，不再维护集中故事大 JSON。
.story-library.json 只存包身份、背景、Epic 和历史来源；其中旧来源快照只读保留，不是第二套当前故事。
JSON 是可编辑事实源，Markdown 是同一卡的可读投影。用户用自然语言提出改动，Agent 负责更新对应独立数据和卡片，不让用户手工双写。
人工直接编辑过 Markdown 时，先展示差异并整合为新的内容修订，不能直接重生成覆盖。

## 一次局部操作
1. 读索引，定位唯一 Story ID，再读该卡和对应历史；全库只读扫描保证引用与编号唯一。
2. 明确本轮仅新增/修改/确认哪个对象；保留其他卡片。
3. 检查当前修订，提出差异；沿用 Story 与 Acceptance 分别确认的规则。
4. 用 change 生成保存计划；计划仅列实际变化文件。
5. check-plan 对照磁盘基线；保留非空备份后，由宿主按已授权范围应用，未授权先预览。
6. 写后 validate；如果跨文件保存部分失败，列出已写/未写项并保留计划及备份，停止后续操作。由宿主按明确授权恢复，脚本不自动覆盖回滚。
7. 报告目标 ID、修订、验收影响和卡片路径，不要求整库所有故事同时完成。

正常 Story 或 AC 更新只变更对应 .story-data、stories 卡片，以及内容确实变化的 index.md。
Epic 标题/结果更新只影响 Epic 元数据与索引；Story 卡只引用 Epic ID，不复制其可变内容。
换 Epic 时改该 Story 的 epic_id，产生新修订，索引重新归类；卡片文件名保持稳定。
AC 归属保持在原故事；需要替换其业务含义时新增 AC，明确退役旧项，不搬走历史。

## 编号、版本和历史
保留旧 ID 和所有修订，迁移不增加业务修订、不重批已确认内容。
常见 US-001 直接作为文件名；特殊旧 ID 用确定性安全文件名映射，ID 本身原样保留。不能手工把 ID 拼入磁盘路径。
新编号库内唯一且不复用退役编号；跨库引用需要 package_id。
Story 内容改动追加版本，旧 AC 绑定过时修订后显示需复审；只改 AC 不增加 Story 修订。
历史规则、INVEST 与三类验收沿用 [持续维护核心](continuous-maintenance.md)；该页集中包保存方式仅用于0.3兼容模式。
每步保存相邻基线，validate --previous 防止历史丢失或改写，不跨多个未保存操作推断时间线。

## 迭代只引用
工具输出的引用包含：
```json
{
  "package_id": "REQ-001",
  "story_id": "US-001",
  "story_revision": 2,
  "acceptance_refs": [{"id": "AC-001", "revision": 1}],
  "card_path": "stories/US-001.md"
}
```

这是字段示意。实际引用必须从有效故事库生成，不能手填不存在的修订。
card_path 是当前卡的导航；真正读取当时内容用 ID、Story revision、AC revisions 解析历史，不能把当前卡误当历史快照。
resolve 返回指定历史内容并报告 outdated；不修改调用方引用。
退役验收不进入新引用，已有历史引用仍可解析。活动验收仍绑定旧故事修订时不能生成一致的新引用，先复核验收。尚无AC的候选可被引用，但不表示可承诺实施。
引用不会创建迭代文件，不复制完整故事正文，也不自动批准纳入迭代。
Task、产品详细设计和工程设计均在后续阶段；本 Skill 仅交接稳定引用。

## 只读命令
在 Skill 根运行；Python 的 -B 不生成字节码缓存。所有计划只输出 stdout，无自动写入或 --apply。

```bash
python3 -B scripts/story_library.py init --package REQ-001 --context context.json
python3 -B scripts/story_library.py migrate old/story-workspace.json
python3 -B scripts/story_library.py next-id stories-library --kind story
python3 -B scripts/story_library.py change stories-library --operation add --kind story --id US-003 --content story.json --reason "新增用户需求"
python3 -B scripts/story_library.py change stories-library --operation revise --id US-003 --expect 1 --content story.json --reason "完善目标"
python3 -B scripts/story_library.py change stories-library --operation review --id US-003 --expect 2 --decision approved --actor "实际确认人" --ref "实际确认记录"
python3 -B scripts/story_library.py check-plan stories-library --plan proposed-change.json
python3 -B scripts/story_library.py validate stories-library --previous trusted-previous-library
python3 -B scripts/story_library.py reference stories-library --id US-003
python3 -B scripts/story_library.py resolve stories-library --reference iteration-story-ref.json
```

init：创建空库文件候选；migrate：无损拆分现有workspace包，输出新库计划，使用非空目标会被check-plan拒绝。
旧 v2 先显式导入 workspace，再分拆；保留旧包与其批准原文。新模式批准按0.3导入规则处理，不假装自动批准。
change：--content 提供完整新对象内容，先读取旧内容，只改授权字段；--expect 是当前修订；review 只登记真实确认。
check-plan：检查文件路径与磁盘基线；不证明产品批准或计划正文正确。保存后仍需 validate。
validate：结构、跨卡引用、Markdown投影、总索引和历史（指定previous时）校验。
reference/resolve：交接与历史读取；不建立迭代承诺。
退出码0成功，1结构/引用/漂移错误，2读取/用法错误。

## 故障与范围
缺失卡片、重复ID、文件名漂移、符号链接、路径逃逸、人工投影差异或损坏JSON均停止对应写入。
不会把异常库视为空库重建；不会静默删除未知卡片。
没有Python时可人工按同结构整理，明确未执行机器检查，不冒充历史校验通过。
本轮局部完成不等于整库、整个Epic或产品全部交付。故事验收状态与后续任务完成状态分开。
