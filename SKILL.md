---
name: aef-user-story
description: 当用户要从产品定义或原始需求梳理 Epic、用户故事与验收条件，或独立完善某条故事、局部修改验收、维护编号和修订历史时使用。支持故事全貌、按需细化和持续反馈，不要求先运行 AEF 其他 Skill。不用于故事地图、迭代排期、产品详细设计、PRD、技术设计或编码。
---

# AEF User Story

把需求整理成可讨论、可确认、可持续维护的故事。可以独立使用，也可由 AEF 调用；不依赖地图、Sprint 或完整生命周期安装。

## 先恢复，再确定本轮范围

先读已有 Definition/需求包和项目规范，只用相关背景，不重做产品定义。
识别本轮是建立全貌、细化指定故事、只补验收、局部修改、拆分合并或恢复进度。一次只追问会改变结果的关键未知，不让用户重述已知信息。

输入可以是一句话、可读附件、产品定义或已有故事。区分 facts、assumptions、unknowns、constraints、solution ideas；未知不冒充事实，技术方案不冒充用户价值。
编号不明先定位对应对象；读取失败说明未读，含敏感资料时使用脱敏摘要。

## 两种交付模式

- **持续维护模式**：用户要求独立/局部完善、编号版本管理，或已有 story-workspace.json 时使用。先读 [持续维护](references/continuous-maintenance.md)，以对象修订为单位工作。
- **传统双文件模式**：已有 StoryCard v1/v2，且只需原流程时保留原能力；读 [格式](references/user-story-format.md) 与 [项目保存](references/how-to-save-to-project.md)。双文件需求包仍为 user-story.md 与 story-card.json。不得把新模式内容冒充 v2，也不擅自迁移旧包。

旧包切换持续维护模式先预览导入；保留原包，只维护一个当前入口。旧审批保留在来源快照，新模式确认需用户明确认可对应 ID 与修订。

## 输出

本轮范围内的 Epic、Story、INVEST 检查、规则与验收条件、版本差异、确认状态和待决问题。
持续维护模式可先交付概括故事；“草稿已整理”不等于“已满足开发条件”。
对话可作为交付；项目保存时输出 JSON 历史与人读 Markdown 投影，路径遵循项目规范。
不生成故事地图、迭代计划、产品详细设计、正式 PRD、Spec、Plan、Task、架构或代码。

## Story 与验收工作流

### 1. 需求复述与 Epic/Story

方法见 [故事写法](references/how-to-write-user-story.md)。
大目标形成 Epic；按完整用户结果拆 Story，不按前端/后端/数据库拆分。
句式：作为〔用户〕，当〔场景〕时，我希望〔目标〕，从而〔价值〕。
每条故事检查 INVEST 的六项证据；信息不足标 risk，不计算 Story Points。
业务规则、非功能约束和证据单列关联；保留全部候选，不代替用户选择首版。

### 2. User Story 修改循环

展示目标 ID、当前修订、当前内容和候选差异。
允许修改某一条、拆分某一条、合并两条、增加遗漏 Story、暂缓某一条。
只改授权对象；相关项先报告影响。拆分/合并保留旧 ID 历史，新对象记录 derived_from，不擅自删除旧故事。
只要求概括故事时可在此交付草稿，不强制补所有验收。

### 3. User Story 明确确认

用户确认绑定具体 Story ID 和修订；局部确认不批准整个包。记录真实 actor/ref，不把沉默、保存授权或示例记录当批准。
故事语义变化追加修订，旧批准不复用；关联验收条件失效，保留原内容并标待复审。
持续维护工具通过绑定旧 story_revision 识别失效，不静默重写其他对象。

### 4. 验收条件修改循环

只对已确认故事细化 success、failure、boundary，采用 Given/When/Then 表达外部可观察结果。
每个 AC 有独立 ID 与修订，绑定 Story ID 和具体 story_revision。
只改 AC 时，Story 本身的修订和批准不变；该 AC 新修订需要重新确认。
“接口写完、代码合并、测试通过”不是用户验收。

### 5. 验收条件明确确认

验收确认与故事确认独立。批准 AC 前，其绑定的当前 Story 必须已经明确批准。
就绪条件：Story 当前修订批准、INVEST 全 pass、三类验收齐全且当前有效 AC 均批准，无过时或待确认项。
高风险约束仍需所要求的专项判断；结构就绪不等于专业批准。

### 6. 写入预览与写入批准

预览实际路径、对象级 diff、历史保留方式、关联影响和验证结果。
按本轮已有授权保存，不为已授权同一动作重复追问；范围不清或覆盖冲突时先明确。
只读工具不写文件。宿主保存时先保留旧文件，生成新候选并用 --previous 校验；重读磁盘基线防并发修改，再按项目规则原子替换并重生 Markdown。
保存失败报告具体已写/未写文件，不声称完整落盘。不自动安装、commit、push 或发布。

### 7. 下游交接

PRD 是可选路径。传统模式保留 direct_spec、prd、backlog、specialist_review 的结构化路由与原校验。
持续维护模式交接 Story/AC 的 ID、修订、确认记录、规则、未知和风险，不为了“完成本轮局部修改”强制生成下游文档或排期。
AEF 生命周期状态仍由宿主拥有，见 [集成边界](references/aef-integration.md)。

## 校验与完成

持续维护：python3 -B scripts/story_workspace.py validate <新包> --previous <旧包>。
传统模式：python3 scripts/validate_story_card.py <story-card.json> --json 与 python3 scripts/validate_story_package.py <需求目录> --json。
完整回归：python3 -B -m unittest discover -s tests -p 'test_*.py'。
工具仅验证结构和历史，不验证用户批准真实性或业务价值；没有 Python 时声明未做机器检查。

本轮交付应报告目标对象、差异、修订、验收状态、保存位置和唯一下一步。
局部修改/候选整理不要求整个产品需求全部批准；只有满足就绪条件的故事才能称为“已就绪”。
Skill 自身版本由 CHANGELOG 管理；产品资料 revision 独立于 Skill 版本。
