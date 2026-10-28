# User Story 传统双文件需求包格式

本页只约束传统 v1/v2；持续维护模式见 [continuous-maintenance.md](continuous-maintenance.md)。

一个完整需求包只有两个文件：人读的 `user-story.md` 和机器读的 `story-card.json`。两者使用相同的 package、Story、Acceptance ID。

## `user-story.md` 九段结构

1. YAML frontmatter：`schema_version`、`package_id`、`status`。
2. 原始需求：保留用户的直白表达和摘要。
3. 信息边界：facts、assumptions、unknowns、constraints、solution ideas。
4. Epic：Epic ID、标题和它包含的 Story ID。
5. User Stories：每条用 `### US-001：标题`，含标准句式与 INVEST 证据。
6. Acceptance：每条用 `### AC-US-001-S：标题`，含类型和 Given / When / Then。
7. 范围：included、excluded、deferred。
8. 确认记录：Story review、Acceptance review 及修改摘要。
9. 下一步：每条 approved Story 的唯一 route、目标 ID 和建议路径。

Markdown 标题中的 ID 是双文件校验器识别引用的依据，不要把 ID 只放在表格或正文里。

## `story-card.json` 顶层字段

`schema_version` 固定为 `aef-story-card/v2`，`artifact_type` 固定为 `aef-story-card`。

| 字段 | 作用 |
|---|---|
| `package_id` | 双文件共同的需求包 ID |
| `status` | 当前工作流状态 |
| `source` | summary、facts、assumptions、unknowns、constraints |
| `epic` | epic_id、title、status、story_ids |
| `stories` | Story 内容、状态、INVEST、acceptance_ids |
| `acceptance` | 三类 Given / When / Then |
| `scope` | included、excluded |
| `reviews` | Story 与 Acceptance 的独立确认状态 |
| `delivery` | 同目录两个相对文件名 |
| `next_step` | 一条或多条下游路由项 |

## Story 对象

必填 `story_id`、`title`、`actor`、`scenario`、`goal`、`value`、`statement`、`status`、`invest_review`、`acceptance_ids`。

`invest_review` 必须含 `independent`、`negotiable`、`valuable`、`estimable`、`small`、`testable`。每项包含 `status: pass/risk/fail` 和非空 `reason`。

## Acceptance 对象

必填 `acceptance_id`、`story_id`、`type`、`given`、`when`、`then`。类型只能是 `success`、`failure`、`boundary`。

推荐 ID：`AC-US-001-S`、`AC-US-001-F`、`AC-US-001-B`。同类型需要多条时可以追加数字。

## reviews 状态

每个 review 都含 `status`、`confirmation`、`change_summary`。

- Story/Acceptance 可用 `draft`、`awaiting_confirmation`、`approved`、`rejected`。
- Acceptance 不能早于 Story approved。
- approved 时 `confirmation` 必须记录明确确认方式。
- approved Story 被修改时，Story 回到待确认，Acceptance 回到 draft 或 not_started。

## next_step.items

每项必填 `route`、`reason`、`capability`、`story_ids`、`target_id`、`suggested_path`、`required_acceptance_ids`。

`route` 可选 `direct_spec / prd / backlog / specialist_review`。每条 approved Story 必须且只能出现一次。`direct_spec` 一项只能包含一条 Story；`prd` 可以组合多条相关 Story。

## 状态与路由

- `ready_for_spec`：两次确认通过、INVEST 全 pass、三类 Acceptance 齐全且全部走 `direct_spec`。
- `ready_for_prd`：两次确认通过，仍需用 PRD 补跨 Story 业务关系。
- `backlog`：明确暂缓。
- `blocked`：缺用户决定或专项审批。

## v1 到 v2

验证器继续接受 `aef-story-card/v1`，用于读取旧项目。v1 的 `vertical_slice_review`、`selected_story_id`、`prd_handoff` 只在 v1 分支保留。

新输出一律写 v2：用每条 Story 的 INVEST 替代旧切片字段，用 `reviews` 替代单一 review state，用 `next_step.items` 替代只通向 PRD 的 handoff。不要把 v1/v2 字段混写在同一文件。
