---
name: aef-user-story
description: 当用户只有模糊需求、口述想法、功能清单、过大的 Epic，或需要把已知需求整理成符合 INVEST、带可观察验收条件的 User Story 时使用。也用于在写 PRD 或 Spec 前完成需求澄清、Story 拆分、双重确认和项目落盘。不用于直接生成正式 PRD、技术 Spec、实施任务、架构或代码。
---

# AEF User Story

把模糊需求变成已确认、可验收、可追踪到后续 PRD 或 Spec 的 User Story 需求包。先确认 User Story，再确认验收条件，最后确认是否写入项目；任何一道门未通过都不能越级。

## 适用场景

- 用户只有一句产品想法、口述需求、截图文字或混杂功能清单。
- 用户问“怎么拆 User Story”“这是 Epic 还是 Story”“第一版先做什么”。
- 现有 Story 混入多个用户、多个结果或前端/后端/数据库等横向任务。
- Story 已经确认，需要补 success、failure、boundary Acceptance Criteria。
- PRD 或 Spec 开始前需要一份结构化、经确认的需求包。

## 不适用场景

- 需求已经确认，用户只要求架构、UI、API、数据模型、Spec、Plan 或代码。
- 用户只要求修复现有 bug。
- 用户要求机械改写现成 PRD，且不要求检查用户价值和边界。
- 输入只有工具、模型、供应商或技术栈；这时先澄清用户问题，不把方案冒充 Story。

## 输入

至少需要一段原始需求。可选读取已有用户反馈、研究证据、范围、非目标、约束和现有需求材料。

先把输入分类为：

- facts：用户明确提供或有证据支持的事实；
- assumptions：为了形成候选而提出、仍需确认的假设；
- unknowns：会影响拆分但当前未知的信息；
- constraints：已知限制；
- solution ideas：功能名、技术方案、工具或供应商建议。

含凭证、隐私或商业敏感原文时，停下来要求脱敏摘要。附件不可读时明确说明，不假装读取。

## 资源路由

- Epic、Story、INVEST 和 Acceptance 写法：读取 [how-to-write-user-story.md](references/how-to-write-user-story.md)。
- `user-story.md`、StoryCard v2 字段、ID、状态和路由：读取 [user-story-format.md](references/user-story-format.md)。
- 项目路径、写入预览、批准、非覆盖写入和下游钩子：读取 [how-to-save-to-project.md](references/how-to-save-to-project.md)。
- 独立使用与未来 AEF 集成：读取 [aef-integration.md](references/aef-integration.md)。
- 用户提供或要求写入需求包时，运行两个确定性校验脚本。

## 工作流

### 1. 需求复述

复述原始需求，不添加未声明的功能。列出 facts、assumptions、unknowns、constraints 和 solution ideas。

如果某个未知项会实质改变用户、场景、目标、价值或 Story 边界，一次只问一个信息增益最高的问题。否则保留 unknown 并继续形成候选。

### 2. 区分 Epic 与 User Story

如果输入包含多个主要用户、多个可独立获得的结果或一组发布目标，先标记为 Epic，再按用户结果拆候选 Story，并分配稳定 ID。

每条 Story 使用这一语义：

> 作为〔主要用户〕，当〔具体场景〕时，我希望〔完成一个用户目标〕，从而〔获得可感知价值〕。

逐条给出 INVEST 证据：Independent、Negotiable、Valuable、Estimable、Small、Testable。`Estimable` 只判断信息是否足以供后续估算，不计算 Story Points。按用户价值拆分，不按前端、后端、模型、数据库或团队职责拆分。

### 3. User Story 修改循环

按“原始需求摘要 → 信息分类 → Epic → 候选 Story → INVEST → 当前范围与暂缓项”展示。明确告诉用户可以：确认全部、修改某一条、拆分某一条、合并两条、增加遗漏 Story、暂缓某一条、调整范围或顺序。

根据反馈重写并再次展示差异；只要还有修改，继续循环，不把沉默或模糊肯定当批准。

### 4. User Story 明确确认

请求用户明确确认当前 Story 集合与范围。确认后把 Story review 标为 `approved`；未确认时保持 `awaiting_confirmation` 并停止。

任何已批准 Story 后续发生角色、场景、目标、价值、范围或 ID 变化时，该 Story 回到待确认，关联验收条件失效，Acceptance review 回到 `draft` 或 `not_started`。

### 5. 生成验收条件

只为已确认 Story 生成外部可观察条件：

- success：主路径成功结果；
- failure：关键失败时用户看到什么以及如何恢复；
- boundary：输入、权限、数量、时间或状态边界改变行为时会怎样。

每条准备进入下游的 Story 至少各有一条 success、failure、boundary。优先使用 Given / When / Then。“接口完成、代码合并、页面写完、测试通过”是技术任务，不是 Acceptance。

### 6. 验收条件修改循环

逐条展示 Acceptance ID、所属 Story、类型和 Given / When / Then。允许用户修改、增加、删除、重排或指出不可观察的条件；每次修改后重新检查三类覆盖和 Story 引用。

### 7. 验收条件明确确认

请求用户明确确认验收条件。确认后 Acceptance review 才能标为 `approved`；未确认时保持 `awaiting_confirmation` 并停止。Story review 未批准时，Acceptance review 不能批准。

### 8. 写入预览

先发现项目现有规范；没有更合适规范时，默认预览：

```text
docs/requirements/<slug>/
├── user-story.md
└── story-card.json
```

展示目标项目、两个完整路径、将创建或更新的文件、内容摘要、冲突情况和校验命令。已有文件绝不静默覆盖。

### 9. 写入批准

明确询问用户是否批准把预览内容写入所示路径。只有收到明确批准才写入；路径不清、文件冲突或用户要求改动时，更新预览并再次等待批准。

### 10. 下游路由

PRD 是可选路径，不是必经阶段。对每条已批准 Story 选择且只选择一个下一步：

- `direct_spec`：单条 Story 的需求与验收已清楚，可直接交给后续 Spec-writing 能力；
- `prd`：多个 Story 仍需共同补业务规则、流程或跨角色关系；
- `backlog`：有价值但明确暂缓；
- `specialist_review`：支付、法律、医疗、金融、隐私、安全、权限、合规或迁移需要专项审批。

这里只写结构化钩子，不实际生成 PRD 或 Spec。`direct_spec` 必须一条 Story 对应一个目标 Spec；`prd` 可以组合多条相关 Story。

## 确定性校验

从 Skill 根目录运行：

```bash
python3 scripts/validate_story_card.py path/to/story-card.json --json
python3 scripts/validate_story_package.py path/to/requirement-directory --json
```

- 退出 0：结构、引用、状态和双文件一致性合法；
- 退出 1：StoryCard 存在确定性错误；
- 退出 2：用法、文件或 JSON 读取错误。

脚本通过只证明结构合法，不证明用户价值、事实真实性或优先级正确。

## 高风险交接

支付、隐私、权限、安全、合规、医疗、法律、金融或数据迁移需求必须在 StoryCard 中标记风险与待确认 owner。Skill 可以整理已知事实和问题，不能替代专业审批或虚构结论。

## 完成条件

一次任务只有在 Story 和 Acceptance 分别明确确认、每条 approved Story 通过 INVEST 并覆盖三类验收、双文件引用一致、写入经过预览与批准或用户选择只在对话交付、每条 Story 恰好有一个下游 route、高风险项有明确 handoff 时完成。

缺少任一确认时，返回当前阶段、已知内容和唯一下一步，不包装为完成。
