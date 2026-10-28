---
schema_version: aef-story-card/v2
package_id: REQ-AI-MEETING-ASSISTANT
status: ready_for_prd
---

# AI 会议助手首版

## 原始需求

录音、转写、总结、任务、搜索、分享和权限混合需求。

## 信息边界

- facts：团队需要会后纪要和待办；任务必须由组织者确认。
- assumptions：首版先服务内部团队会议。
- unknowns：支持的平台和保留时长。
- constraints：AI 不能未经确认直接发布任务。

## Epic

EPIC-001：让团队从会议内容得到可追踪结果；包含 US-001 至 US-006。

## User Stories

### US-001：获得会议逐字稿

作为会议参与者，当会议结束时，我希望获得可阅读的逐字稿，从而回看讨论原文。状态：approved。

### US-002：区分发言人

作为会议参与者，当多人发言时，我希望看出每段内容是谁说的，从而理解上下文。状态：deferred。

### US-003：获得会议摘要

作为会议参与者，当逐字稿可用时，我希望查看关键结论摘要，从而快速理解会议结果。状态：approved。

### US-004：确认并发布行动项

作为会议组织者，当 AI 提议行动项时，我希望编辑确认后再发布，从而让成员收到准确任务。状态：approved。

### US-005：搜索历史会议

作为团队成员，当我需要回顾旧决定时，我希望搜索历史会议，从而找到相关依据。状态：deferred。

### US-006：按权限分享会议结果

作为会议组织者，当我分享会议结果时，我希望控制访问范围，从而避免信息泄露。状态：deferred。

## Acceptance

### AC-US-001-S：成功生成逐字稿
- Given 会议录音完整；When 会议结束；Then 参与者可阅读按时间顺序生成的逐字稿。

### AC-US-001-F：转写失败
- Given 转写服务失败；When 参与者打开会议结果；Then 显示失败状态和重试入口。

### AC-US-001-B：无有效语音
- Given 录音中没有可识别语音；When 转写结束；Then 明确说明未识别到内容且不生成伪造文本。

### AC-US-003-S：成功生成摘要
- Given 逐字稿可用；When 参与者打开摘要；Then 显示关键结论和未决事项。

### AC-US-003-F：摘要失败
- Given 摘要处理失败；When 参与者打开摘要；Then 保留逐字稿并提供重新生成入口。

### AC-US-003-B：内容过短
- Given 有效逐字稿过短；When 请求摘要；Then 说明内容不足而不编造结论。

### AC-US-004-S：确认后发布任务
- Given AI 已提议行动项；When 组织者编辑并确认发布；Then 成员收到最终行动项。

### AC-US-004-F：发布失败保留编辑
- Given 发布服务失败；When 组织者确认发布；Then 显示失败并保留组织者已编辑内容。

### AC-US-004-B：缺少负责人
- Given 某行动项没有负责人；When 组织者尝试发布；Then 标记缺失并要求确认，不自动分配。

## 范围

- included：US-001、US-003、US-004。
- excluded：未经确认自动发布任务。
- deferred：US-002、US-005、US-006。

## 确认记录

- Story：approved；自动分配改为组织者确认后发布，首版范围明确确认。
- Acceptance：approved；发布失败时保留编辑内容后明确确认。

## 下一步

US-001/US-003/US-004 → `prd` → `PRD-MEETING-V1` → `docs/product/PRD-MEETING-V1.md`。
