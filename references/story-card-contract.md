# StoryCard 合同

## 合同标识

- `schema_version`: `aef-story-card/v1`
- `artifact_type`: `aef-story-card`

StoryCard 同时保存来源边界、候选 Story、两次评审状态和 PRD handoff。它不是正式 PRD。

## 顶层字段

| 字段 | 类型 | 规则 |
|---|---|---|
| `review_state` | object | 含 `story` 与 `acceptance` |
| `source_summary` | non-empty string | 只概括原始需求 |
| `facts` | string array | 不含推断 |
| `assumptions` | string array | 仍需确认 |
| `unknowns` | string array | 影响边界的未知项 |
| `constraints` | string array | 已确认限制 |
| `epic` | object | `epic_id/title/outcome` 非空 |
| `stories` | object array | 至少一条，ID 唯一 |
| `selected_story_id` | string | 引用现有 Story |
| `vertical_slice_review` | object | 布尔值、理由和拒绝的横向拆分 |
| `acceptance` | object array | ID 唯一并引用现有 Story |
| `non_goals` | string array | 当前明确不做 |
| `deferred_story_ids` | string array | 只引用现有 Story |
| `prd_handoff` | object | 状态、approved IDs 和 open questions |

## 评审状态机

Story review：`candidate -> awaiting_confirmation -> approved/rejected`。

Acceptance review：`not_started -> draft -> awaiting_confirmation -> approved/rejected`。

- Story 未 `approved` 时，Acceptance 不能 `approved`。
- Acceptance `approved` 时，每条 approved Story 覆盖 success、failure、boundary。
- 两个 review 均 `approved` 后，`prd_handoff.status` 才能为 `ready`。
- approved Story 被修改时，Story 回到 `awaiting_confirmation`，Acceptance 回到 `draft` 或 `not_started`。

## Story 对象

必填：

- `story_id`：稳定、唯一，推荐 `US-001`；
- `actor`：一个主要用户；
- `scenario`：具体触发场景；
- `goal`：一个用户目标；
- `value`：可感知结果；
- `statement`：标准语义句；
- `status`：`candidate / selected / deferred / approved`；
- `source_refs`：事实或证据引用；
- `acceptance_ids`：该 Story 的 Acceptance ID。

ID 不因表格顺序或标题润色而改变。拆分后创建新 ID，不静默复用旧 ID 表达不同价值。

## Acceptance 对象

必填 `acceptance_id`、`story_id`、`type`、`given`、`when`、`then`。`type` 只能是 `success / failure / boundary`。

推荐 ID：`AC-US-001-S`、`AC-US-001-F`、`AC-US-001-B`。同一类型可以多条，但最低覆盖不能少于三种类型。

“前端完成、API 实现、代码合并、测试通过”不是外部可观察 Acceptance。

## 垂直切片检查

```json
{
  "is_vertical": true,
  "rationale": "用户可以完成一个端到端结果。",
  "rejected_horizontal_splits": ["只实现页面", "只实现 API"]
}
```

`is_vertical` 是 Agent 与用户的产品判断，不由 Python 计算。脚本只验证字段和类型。

## PRD 交接

```json
{
  "status": "draft",
  "approved_story_ids": [],
  "open_questions": []
}
```

`draft` 表示仍在整理，`blocked` 表示缺少确认或专项审批，`ready` 表示两次 review 已 approved。

人类可读 handoff 还包含用户问题、范围、非目标、约束、假设、未知项、依赖、业务规则缺口和唯一下一步。

## 校验

```bash
python3 scripts/validate_story_card.py path/to/story-card.json --json
```

有效示例：`tests/fixtures/valid-story-card.json`。确定性 PASS 只代表结构和引用合法；用户价值、事实真实性、first cut 和风险决定仍需人工评审。
