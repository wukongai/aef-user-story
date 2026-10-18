# 共用编号、修订与确认语义

适用于独立故事库及兼容workspace；不规定磁盘保存格式。

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
