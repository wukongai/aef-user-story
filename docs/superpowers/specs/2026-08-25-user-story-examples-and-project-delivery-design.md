---
title: "User Story 完整案例与项目落盘设计"
type: design
status: approved_for_plan
created: 2026-08-25
updated: 2026-08-25
target_version: 0.2.0
tags: [user-story, invest, acceptance, examples, project-delivery]
---

# User Story 完整案例与项目落盘设计

## 1. 目标

把 `aef-user-story` 从“能整理 StoryCard 的 Skill”扩展为一个完整、可演示、可落盘、可检查的需求工作流：

1. 从一句模糊需求、混杂功能清单或不合格 Story 开始；
2. 通过与用户的对话形成候选 User Story；
3. 使用 INVEST 检查 Story 质量；
4. 让用户修改并明确确认 Story；
5. 生成 success、failure、boundary 三类验收条件；
6. 让用户修改并明确确认验收条件；
7. 预览项目写入路径，经用户批准后生成双文件需求包；
8. 通过稳定 ID 把每条 Story 和 Acceptance 交给 PRD、Spec、backlog 或专项评审。

## 2. 本次不做

- 不评估 Story Points。
- 不生成正式 PRD。
- 不生成技术 Spec、架构、实施 Plan、开发 Task 或代码。
- 不把完整真实聊天记录默认写入项目。
- 不自动覆盖项目已有文件。
- 不把训练营课次或文章结构写进 Skill 状态机。

`E—Estimable` 只检查需求是否清楚到后续能够估算，不在本 Skill 中产生点数。估算、技术方案和 Task 拆分属于后续 Spec/Plan 阶段。

## 3. 方法论边界

### 3.1 User Story 使用 3C 与 INVEST

User Story 的工作过程遵循：

- Card：简洁、稳定 ID 的 Story 表达；
- Conversation：Agent 与用户围绕用户、场景、目标、价值和范围反复修改；
- Confirmation：用已确认的验收条件定义可观察的完成标准。

每条准备进入下游的 Story 使用 INVEST 检查：

| 字母 | 含义 | 本 Skill 的判断 |
|---|---|---|
| I | Independent | 与其他 Story 尽量不重叠，可以独立排序 |
| N | Negotiable | 表达目标与价值，不锁死技术实现 |
| V | Valuable | 用户或客户能获得明确价值 |
| E | Estimable | 信息足够让后续工程阶段估算 |
| S | Small | 范围不再是 Epic，能够作为一个清晰增量讨论 |
| T | Testable | 能形成明确、可观察的验收条件 |

每一项必须包含 `status` 和判断理由。脚本只能验证字段、枚举和引用，不能替代产品判断。

### 3.2 垂直切片不是主检查项

v2 不再输出独立的 `vertical_slice_review`。避免按前端、后端、数据库拆 Story，作为 `Valuable` 和 `Independent` 的辅助说明保留，不作为另一套主方法论。

### 3.3 Story 与 Task 分开

- User Story 使用 INVEST；
- 后续开发 Task 可以由 Task/Plan Skill 使用 SMART；
- 本 Skill 只提供 Story、Acceptance 和稳定下游引用，不生成 Task。

参考来源：

- Bill Wake, [INVEST in Good Stories, and SMART Tasks](https://xp123.com/invest-in-good-stories-and-smart-tasks/)
- Agile Alliance, [User Stories](https://agilealliance.org/glossary/user-stories/)

## 4. 文件架构

### 4.1 Skill 仓库

```text
aef-user-story/
├── SKILL.md
├── references/
│   ├── how-to-write-user-story.md
│   ├── user-story-format.md
│   ├── how-to-save-to-project.md
│   └── aef-integration.md
├── examples/
│   ├── 01-video-transcript-jump/
│   ├── 02-ai-meeting-assistant/
│   └── 03-ai-content-workflow/
├── scripts/
└── tests/
```

职责：

| 文件 | 回答的问题 |
|---|---|
| `SKILL.md` | Agent 必须如何与用户互动，在哪里停止确认 |
| `how-to-write-user-story.md` | 如何识别 Epic、形成 Story、用 INVEST 检查、写验收条件 |
| `user-story-format.md` | 人类文档和机器 JSON 必须有哪些字段与状态 |
| `how-to-save-to-project.md` | 如何选择目录、预览、批准、非覆盖写入和交接下游 |
| `examples/*/conversation.md` | 完整对话怎样实际发生 |
| `examples/*/project-output/` | 对话完成后项目目录中应该出现什么 |

现有 `story-shaping-standard.md` 的有效内容迁入 `how-to-write-user-story.md`；现有 `story-card-contract.md` 演进为 `user-story-format.md`。重命名必须在维护计划中显式列出，不能依靠候选缺失推断删除。

### 4.2 目标项目

项目已有需求目录时优先适配其规范；没有可识别规范时使用：

```text
docs/requirements/<requirement-slug>/
├── user-story.md
└── story-card.json
```

一个需求包可以包含一个 Epic 和多条 Story。每条 approved Story 使用独立 `story_id`，并在 `next_step` 中对应一个建议 Spec ID。

## 5. 主 Skill 交互流程

### 5.1 强制流程

```text
理解并复述需求
→ 区分事实、假设、未知项和约束
→ 判断 Epic 或 Story
→ 生成候选 Story 与 INVEST 检查
→ Story 修改循环
→ Story 明确确认
→ 生成三类验收条件
→ Acceptance 修改循环
→ Acceptance 明确确认
→ 预览项目路径和双文件
→ 用户批准写入
→ 写入并校验
→ 输出下游钩子
```

### 5.2 澄清规则

- 只有未知项会实质改变用户、场景、目标、价值或 Story 边界时才提问；
- 一次只问一个信息增益最高的问题；
- 不影响当前候选的未知项保留在输出中，不为完成流程而追问；
- 不把 Agent 建议的功能冒充为用户事实。

### 5.3 Story 修改循环

候选 Story 展示后，Agent 必须明确告诉用户可以：

- 确认全部；
- 修改某一条；
- 拆分某一条；
- 合并两条；
- 增加遗漏 Story；
- 暂缓某一条；
- 调整当前范围和优先顺序。

任一 Story 被修改后，该 Story 回到 `awaiting_confirmation`，相关 Acceptance 回到 `draft` 或 `not_started`，不能沿用旧确认。

### 5.4 Acceptance 修改循环

只为已确认 Story 生成验收条件，最低覆盖：

- `success`：主路径成功结果；
- `failure`：关键失败时用户可观察的行为；
- `boundary`：输入、权限、数量、时间或状态边界。

Agent 必须告诉用户可以修改、增加、删除或把条件提升为新 Story。修改后再次展示完整条件并等待确认。

### 5.5 写入门禁

写入前必须展示：

- 目标目录；
- 将创建或修改的文件；
- Story、Acceptance 和 next step 摘要；
- 已有文件冲突。

没有明确写入批准时，只返回可复制内容。目标文件存在时停止，不静默覆盖。

## 6. 人类可读文件合同

`user-story.md` 固定包含：

1. Frontmatter：artifact、schema、package ID、状态、机器文件引用；
2. 原始需求摘要；
3. 事实、假设、未知项、约束；
4. Epic；
5. 每条 Story 的 ID、状态、标准句式与 INVEST 证据；
6. 每条 Story 的 success、failure、boundary Acceptance；
7. 当前范围与非目标；
8. Story 和 Acceptance 确认结果及必要修改摘要；
9. 每条 Story 的下游路由、建议 Spec ID 和 Acceptance 引用。

真实项目默认不保存完整对话，只保存形成当前结果所需的确认与修改摘要。

## 7. 机器文件合同

`story-card.json` 使用 `aef-story-card/v2`，顶层包含：

- `schema_version`
- `artifact_type`
- `package_id`
- `status`
- `source`
- `epic`
- `stories`
- `acceptance`
- `scope`
- `reviews`
- `delivery`
- `next_step`

每条 Story 包含：

- `story_id`
- `title`
- `actor`
- `scenario`
- `goal`
- `value`
- `statement`
- `status`
- `invest_review`
- `acceptance_ids`

`invest_review` 六项均使用：

```json
{
  "status": "pass",
  "reason": "范围和验收边界已经足够清楚"
}
```

v2 不包含 Story Points，不包含 `vertical_slice_review`，不把 PRD 作为唯一出口。

## 8. 状态和硬门禁

### 8.1 状态

```text
candidate
→ awaiting_story_confirmation
→ story_approved
→ acceptance_draft
→ awaiting_acceptance_confirmation
→ ready_for_delivery
→ ready_for_spec | routed_to_prd | backlog | specialist_review
```

### 8.2 `ready_for_spec`

只有同时满足以下条件才能出现：

- 目标对象不是未拆分 Epic；
- Story 六项 INVEST 均为 `pass`；
- Story 已明确确认；
- success、failure、boundary 三类 Acceptance 齐全；
- Acceptance 已明确确认；
- Story、Acceptance 和 next step 引用一致；
- 没有阻断型未知项或专项风险。

## 9. 下游路由

PRD 是可选展开层，不是必经审批。

| `route` | 使用条件 |
|---|---|
| `direct_spec` | Story、规则和 Acceptance 已足够清楚，可以直接设计实现 |
| `prd` | 多角色、多流程或业务规则仍需集中展开 |
| `backlog` | Story 已确认，但暂不进入开发 |
| `specialist_review` | 隐私、安全、合规、支付等专项问题尚未批准 |

`next_step` 必须包含 route、reason、capability、目标 ID/路径以及必须继承的 Story/Acceptance ID。它只提供能力钩子，不假设某个下游 Skill 已安装。

## 10. 三个完整案例

### 10.1 一句话模糊需求

主题：视频逐字稿点击跳转。

重点：澄清主要用户、修改 actor、修改 failure/boundary Acceptance、两次确认、直接进入 Spec。

### 10.2 混杂功能 Epic

主题：AI 会议助手，包含录音、转写、总结、任务、搜索、分享和权限。

重点：识别 Epic、拆多条 Story、用户选择当前范围、修改任务确认规则、暂缓其他 Story、路由到 PRD。

### 10.3 句式正确但范围过大

主题：AI 内容系统，包含选题、写作、配图、审核和发布。

重点：INVEST 明确失败项、区分多个角色与结果、用户删除独立审核者假设、拆成多条 Story、每条 Story 分别挂接 Spec。

### 10.4 每个案例的文件

```text
examples/<case>/
├── conversation.md
└── project-output/
    └── docs/requirements/<slug>/
        ├── user-story.md
        └── story-card.json
```

每个 `conversation.md` 必须包含原始需求、复述、澄清、Epic/Story 判断、候选 Story、INVEST、Story 修改、第一次确认、Acceptance 草稿、Acceptance 修改、第二次确认、路径预览、写入批准、写入结果和下游钩子。

## 11. 校验器与兼容性

这是公开 v0.1.0 的演进，不静默破坏已有 StoryCard：

- 新输出只生成 `aef-story-card/v2`；
- `validate_story_card.py` 在 0.2.0 继续接受 v1 和 v2；
- v1 的 `vertical_slice_review` 和 `prd_handoff` 只在 v1 校验分支保留；
- v2 使用 `invest_review`、`reviews`、`delivery` 和 `next_step`；
- 增加双文件需求包校验，检查两个文件存在、package/story/acceptance ID 一致；
- CHANGELOG 明确迁移关系，不把 v1 字段悄悄改义。

## 12. 错误处理

- 需求不足以判断用户或价值：停在澄清，不伪造 Story；
- INVEST 不通过：返回失败项和唯一下一步，不标记 ready；
- 用户修改已确认 Story：撤销相关 Acceptance 的确认状态；
- 验收条件只是技术任务：退回并改写为外部可观察结果；
- 项目目录规则不明确：展示候选路径，让用户选择；
- 目标文件已存在：停止并展示冲突，不覆盖；
- 下游 Skill 不存在：保留 capability hook，不伪装调用成功；
- 高风险输入：脱敏并路由专项确认。

## 13. 测试设计

按 Skill TDD 执行，先用 v0.1 运行三个新场景并记录缺口，再修改 Skill。

确定性测试至少覆盖：

1. v2 有效 StoryCard 通过；
2. v1 fixture 继续通过；
3. 缺 INVEST 项或 reason 失败；
4. 未确认 Story/Acceptance 却标记 `ready_for_spec` 失败；
5. 缺 success、failure、boundary 任一类型失败；
6. Epic 直接 `ready_for_spec` 失败；
7. `next_step` 悬空 Story/Acceptance 引用失败；
8. 双文件 ID 不一致失败；
9. 三个案例均包含两次确认和写入批准；
10. Skill 不输出 Story Points、正式 PRD、Spec、Task 或代码。

真实行为测试分别验证模糊需求、Epic 和过大 Story。没有独立新鲜上下文时，作者试用必须标记为 non-independent，不声称已经证明泛化能力。

## 14. 发布结果

目标版本为 `0.2.0`。发布前必须完成：

- 设计与实施计划确认；
- RED/GREEN 回归证据；
- 三个完整案例与双文件输出；
- v1/v2 校验兼容；
- production Content Gate、Creation Review 和 Portable Self Test；
- 本地 commit 与工作区干净；
- 用户确认本地检查后再 push；
- 远程文件与安装结果验证。
