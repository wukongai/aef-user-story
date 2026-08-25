# 案例三：AI 内容工作流大 Story 重拆

## 用户原始需求

> 作为自媒体作者，我希望 AI 帮我找选题、写文章、配图、审核并发布，这样我可以全自动做内容。

## Agent 复述

句式完整，但一次包含五个独立结果和“全自动”方案假设，更像 Epic。当前真正目标是减少从选题到发布的重复工作，同时保留发布质量控制。

## 澄清问题

Agent：审核是由独立审核者完成，还是作者本人在发布前确认？

用户：没有独立审核者，就是我本人确认后发布。

## User Story 修改

原 Story 的 INVEST 初评：I/E/S/T 不通过，V 有风险，N 也因“全自动”锁定方案。Agent 先拆为选题、写作、配图、审核、发布五条候选 Story。

用户说明没有独立审核者后，移除审核 Story；“作者本人发布前确认内容与素材”进入发布 Story 的 Acceptance，而不是虚构一个审核角色。最终保留 US-001 选题、US-002 写作、US-003 配图、US-004 确认并发布。

## User Story 确认

Agent：请确认删除独立审核 Story 后的四条 Story 和范围。

用户：确认。

## 验收条件修改

用户要求发布 boundary 明确：正文或配图仍有未确认项时不得发布。Agent 增加阻断条件，并为四条 Story 分别补齐 success、failure、boundary。

## 验收条件确认

Agent：十二条验收条件已更新，请确认。

用户：确认。

## 写入预览

```text
docs/requirements/ai-content-workflow/
├── user-story.md
└── story-card.json
```

包含 4 条 approved Story、12 条 Acceptance；两个文件均为新建，不生成开发 Task。

## 用户批准写入

用户：批准写入。

## 下游钩子

四条 Story 的边界可以独立讨论和实现，分别进入四个 `direct_spec` item：`SPEC-US-001` 至 `SPEC-US-004`。后续 Task 如何按工程方式拆分由 Spec 阶段负责。
