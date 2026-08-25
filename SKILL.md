---
name: aef-user-story
description: 当用户只有模糊产品想法、混杂功能清单、过大的 Epic、不明确的首版范围，或者已确认的 Story 需要补充可观察的 Acceptance Criteria 时使用。也用于拆分 User Story、识别首个垂直价值切片，或在撰写 PRD 前整理需求。不用于直接生成架构、UI、Spec、实施计划、缺陷修复或代码。
---

# AEF User Story

把模糊需求塑形成可确认、可追踪、可验收的用户价值切片。核心原则是：先确认 Story 正面，再确认 Acceptance 背面；没有确认就不越级。

## 适用场景

- 用户只有一句产品想法、口述需求、截图文字或混杂功能清单。
- 用户问“怎么拆 User Story”“这是 Epic 还是 Story”“第一版先做哪一刀”。
- 现有 Story 混入多个用户、多个结果或前端/后端/数据库等横向任务。
- Story 已经确认，需要补 success、failure、boundary Acceptance Criteria。
- PRD 开始前需要一份结构化、经确认的需求 handoff。

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

- Intake、Epic、垂直拆分、INVEST 和 first cut：读取 [story-shaping-standard.md](references/story-shaping-standard.md)。
- StoryCard 字段、ID、状态和 PRD handoff：读取 [story-card-contract.md](references/story-card-contract.md)。
- 独立使用与未来 AEF 集成：读取 [aef-integration.md](references/aef-integration.md)。
- 用户提供或要求写入 StoryCard JSON 时，运行 `scripts/validate_story_card.py`。

## 工作流

### 1. 需求摄入

复述原始需求，不添加未声明的功能。列出 facts、assumptions、unknowns、constraints 和 solution ideas。

如果某个未知项会实质改变用户、场景、Story 边界或 first cut，一次只问一个信息增益最高的问题。否则保留 unknown 并继续形成候选。

### 2. 需求塑形

识别 Epic，或说明原始需求已经足够小。按端到端用户结果拆候选 Story，并分配稳定 ID。

每条 Story 使用这一语义：

> 作为〔主要用户〕，当〔具体场景〕时，我希望〔完成一个用户目标〕，从而〔获得可感知价值〕。

用 INVEST 诊断候选，不把 INVEST 当机械评分。按用户价值拆分，不按前端、后端、模型、数据库或团队职责拆分。

### 3. 选择首个垂直切片

检查每条 Story 是否能让用户体验到一个完整结果。推荐一个 first cut，并说明为什么它最先验证核心价值、哪些 Story 暂缓、当前非目标和仍待确认的假设。

推荐不等于批准。最终范围与优先级由用户决定。

### 4. User Story 评审门

按以下顺序展示：

1. 原始需求摘要；
2. facts / assumptions / unknowns / constraints / solution ideas；
3. Epic；
4. 候选 Story；
5. 垂直切片检查；
6. first cut、暂缓项和非目标；
7. 请求用户明确确认或修改。

**停止。** 用户没有明确确认 Story 集合前，Story 状态保持 `candidate` 或 `awaiting_confirmation`，不生成正式 Acceptance，不把 PRD handoff 标记为 ready。

### 5. 验收条件

只为已确认 Story 生成外部可观察条件：

- success：主路径成功结果；
- failure：关键失败时用户看到什么；
- boundary：输入、权限、数量、时间或状态边界改变行为时会怎样。

优先使用 Given / When / Then。不得把“接口完成、代码合并、页面写完、测试通过”当成 Acceptance。

### 6. 验收条件评审门

展示每条 Acceptance 的 ID、Story 引用、类型和可观察结果，同时列出仍未解决的问题。

**再次停止。** 用户没有明确确认 Acceptance 前，状态保持 `draft` 或 `awaiting_confirmation`，PRD handoff 不得 ready，不生成正式 PRD、Spec 或代码。

### 7. PRD 交接

两次确认都通过后，输出用户、问题和证据摘要；approved Stories 与 Acceptance；first cut、范围、非目标和 deferred Stories；constraints、assumptions、unknowns、依赖、业务规则缺口、稳定 ID 和唯一下一步。

Handoff 是下游输入，不是正式 PRD。

## 确定性校验

从 Skill 根目录运行：

```bash
python3 scripts/validate_story_card.py path/to/story-card.json --json
```

- 退出 0：结构、引用和状态合法；
- 退出 1：StoryCard 存在确定性错误；
- 退出 2：用法、文件或 JSON 读取错误。

脚本通过只证明结构合法，不证明用户价值、事实真实性或优先级正确。

## 高风险交接

支付、隐私、权限、安全、合规、医疗、法律、金融或数据迁移需求必须在 StoryCard 中标记风险与待确认 owner。Skill 可以整理已知事实和问题，不能替代专业审批或虚构结论。

## 完成条件

一次任务只有在 Story 集合和 Acceptance 分别明确确认、StoryCard 引用一致、PRD handoff 未越级、未确认事实仍标记为 assumption/unknown、高风险项有明确 handoff 时完成。

缺少任一确认时，返回当前阶段、已知内容和唯一下一步，不包装为完成。
