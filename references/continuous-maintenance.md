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

## 编号
优先保留项目已有格式，包括 EPIC-001、US-001、AC-US-001-S。
新编号可用 EP-001、US-001、AC-001。编号不包含迭代号，不随顺序、标题或状态变化。
编号至少包内唯一；跨包引用必须使用 package_id/id，宿主新增前扫描项目其他包，避免误认同名 ID。
next-id 只保证本包内未用，并扫描已退役编号；不宣称检查了其他包。
对象退役用 content.lifecycle=retired，保留记录。拆分/合并新对象记录 derived_from；先新增，再经用户决定退役原对象，不从缺失内容推断删除。

## 修订与批准
每次内容变化追加修订；旧快照不改写。纯排版发生在 Markdown 渲染层，不改变 JSON 内容修订。
--expect 必须等于读到的当前修订；过期时先读新内容再重新评估。
改 Story 后旧 AC 仍绑定旧 revision，status 会报告 stale_acceptance；不能只改绑定号，必须逐项复核内容后创建新 AC 修订。
改 AC 不改变 Story；AC 新修订的旧批准无效。
Story 批准、AC 批准和写文件授权分开；review CLI 的 actor/ref 必须来自真实确认，工具不会判断真假。
高风险需求在 context 和对应故事中保留风险、未知与待决定 owner；结构 ready 不代表专项批准。
reject 可记录撤回/不通过；历史事件保留。

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

## 内容字段
Epic：title、outcome。
Story：title、actor、scenario、goal、value、statement；可选 epic_id、invest_review、规则/风险/证据。
INVEST 的六项用 status=pass/risk/fail 与 reason；缺项允许为草稿，不能就绪。
Acceptance：story_id、story_revision、type=success/failure/boundary、given、when、then。
三类对象均可含 lifecycle=active/retired、derived_from；扩展字段仅表示业务事实；id/revision/reviews 由对象封装字段定义。
编号、修订、审批字段放对象封装层，不能藏进 content 冒充系统状态。

## 完成边界
本轮只细化故事就交付该故事；不要求同时完善所有故事、创建地图、选迭代或编写产品详细设计。
候选模式可交付草稿；正式就绪须逐对象真实确认、INVEST 六项 pass、三类已确认验收。
旧模式中的独立 PRD/Spec 路由保留，不因新持续维护模式而删除旧接口。
