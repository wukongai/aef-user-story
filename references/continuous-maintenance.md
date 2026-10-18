# 独立调用与持续维护

本页仅适用于 aef-story-workspace/v1；旧 StoryCard v1/v2 的流程与校验继续有效。
新模式接收已有背景或一句需求，不依赖其他 Skill；可在任何开发阶段调用。
角色、场景、目标、价值未明确时保留未知，候选字段用明确的待确认描述，不伪造用户事实。

## 调用例
- “从这份产品定义整理 Epic 和候选故事，先不写验收。”
- “只完善 US-003 的失败验收，其他故事不动。”
- “看看 US-003 第 2 版和当前版差在哪里。”
- “把这个过大的故事拆成两条，保留原来的关联。”
- “用户反馈改变了这条故事的目标，检查哪些验收需要重审。”
反例：制作故事地图、安排 Sprint、设计界面和技术接口；只交接已有故事，不扩展执行。

## 最小输入和状态
新包使用 package_id、context、objects。context 记录 source/facts/assumptions/unknowns/constraints/non_goals。
objects 类型为 epic/story/acceptance；每个对象含 id、kind、versions、reviews。
versions 每项包含 revision（从 1 连续递增）、content、reason；reviews 为追加的 decision、revision、actor、ref。
内容和批准分开；当前审阅状态从当前修订的最后一条决定派生，没有决定就是 draft。
概括故事可以没有 AC，工具不会因此拒绝合法草稿。准备交接开发时才检查完整就绪条件。

## 保存与恢复
默认候选目录 docs/requirements/<slug>/，AEF 已有 requirements/<需求名>/story.md 则沿用其人读位置。
持续维护 JSON 为 story-workspace.json；人读文件使用 render 输出。此模式 JSON 为唯一可编辑事实源，Markdown 是投影；不手工双写。
已有 Markdown 先读取人工内容并核对导入，不直接重生覆盖。授权保存前展示对象 diff。
1. 读取磁盘旧包并保留非空备份。
2. 工具输出新 JSON 到候选文件；validate <候选> --previous <备份> 检查追加历史。
3. 再次核对磁盘旧包未变化。按宿主项目的原子写入方式应用候选并重生 Markdown；任一步失败报告状态。
4. 写后校验 JSON，再比较保存的 Markdown 与 render 输出。
脚本本身只读；不能把 stdout 输出误称为已保存。
不自动删除旧 v2。迁移确认后更新项目导航为一个当前入口；原包作为历史快照。
历史 show 支持任意保留修订；撤销内容也以新修订恢复，不能删除历史。
备份回滚属于宿主授权动作，工具不会自动覆盖或删除。

## CLI
所有命令都在 Skill 根运行，结果输出 stdout；由宿主按当前授权保存。

```bash
python3 -B scripts/story_workspace.py init --package REQ-001 --context context.json
python3 -B scripts/story_workspace.py import-v2 old/story-card.json
python3 -B scripts/story_workspace.py next-id story-workspace.json --kind story
python3 -B scripts/story_workspace.py add story-workspace.json --kind story --id US-002 --content story.json --reason "补充遗漏故事"
python3 -B scripts/story_workspace.py revise story-workspace.json --id US-001 --expect 1 --content story.json --reason "用户调整目标"
python3 -B scripts/story_workspace.py review story-workspace.json --id US-001 --expect 2 --decision approved --actor "实际确认人" --ref "实际确认记录"
python3 -B scripts/story_workspace.py status story-workspace.json --id US-001
python3 -B scripts/story_workspace.py show story-workspace.json --id US-001 --revision 1
python3 -B scripts/story_workspace.py validate candidate.json --previous story-workspace.json
python3 -B scripts/story_workspace.py render story-workspace.json
```

--content 是该对象完整的新 content；先读取旧 content，只调整授权字段，避免丢失非目标信息。
--previous 按相邻操作验证：每次 add/revise/review 后保存候选与对应基线，再执行下一步。包含“先批准 r1、再修订 r2”的多步变化不能直接跨过中间状态与最初备份比较；本格式没有可验证的全局时间线。
--previous 必须提供更新前的可信基线；单独 validate 只能验证内部结构，不能证明历史未被篡改。
退出 0 为成功，1 为内容/引用/修订错误，2 为用法或文件读取错误。


## 共用状态语义
编号、修订、确认、内容字段与就绪条件见[共用核心](revision-core.md)；本页仅在workspace兼容模式读取。
