# 案例二：AI 会议助手功能清单

## 用户原始需求

> 做个 AI 会议助手，要录音、转写、总结、自动分配任务、搜索历史会议、分享，还要权限。

## Agent 复述

这不是一条小 Story，而是“让团队从会议内容得到可追踪结果”的 Epic。原始输入混合了会议记录、会后理解、行动管理、检索、协作和权限多个结果。

## 澄清问题

Agent：首版最重要的是个人整理，还是团队会后达成一致并执行？

用户：团队开完会后能拿到准确纪要和待办，任务不能让 AI 直接发出去。

## User Story 修改

Agent 先形成至少六条候选 Story：US-001 录音转写、US-002 发言人区分、US-003 会议摘要、US-004 行动项确认发布、US-005 历史会议搜索、US-006 分享与权限。

用户把原始“自动分配任务”修改为“AI 提议行动项，组织者确认后发布”，避免错误任务直接影响成员。首版范围选择 US-001、US-003、US-004；US-002、US-005、US-006 暂缓，但 ID 与原因保留。

## User Story 确认

Agent：请确认当前六条 Story，以及首版批准 US-001/US-003/US-004、其余 deferred。

用户：确认。

## 验收条件修改

用户补充：US-004 的 failure 不能只是“发布失败”，还要保留组织者已编辑内容，避免重填。Agent 更新失败验收，并检查三条 approved Story 都覆盖 success、failure、boundary。

## 验收条件确认

Agent：三条首版 Story 的九条验收条件已更新，请确认。

用户：确认。

## 写入预览

```text
docs/requirements/ai-meeting-assistant/
├── user-story.md
└── story-card.json
```

包含 6 条 Story，其中 3 条 approved、3 条 deferred；9 条 Acceptance；两个文件均为新建。

## 用户批准写入

用户：批准写入预览路径。

## 下游钩子

三条首版 Story 共享“会议结束 → 摘要 → 组织者确认任务”的业务流程，需要先补统一规则，因此合并进入一个 `prd` route，目标为 `PRD-MEETING-V1`。PRD 是可选路径，本 Skill 只交接钩子。
