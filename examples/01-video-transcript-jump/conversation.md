# 案例一：点击逐字稿回到视频

## 用户原始需求

> 我想让用户点一下视频转出来的文字，就能跳回视频那里。

## Agent 复述

你希望用户阅读视频逐字稿时，点击某段文字即可回到对应视频位置，减少手动拖动进度条。当前明确的是“文字与视频定位”；视频来源、转写方式和全文搜索都还没有确定。

## 澄清问题

Agent：主要是谁在使用？普通“视频用户”还是带着学习、回看目的的人？

用户：是看课程和访谈的学习者，叫“视频学习者”更准确。

## User Story 修改

第一稿使用“视频用户”。用户指出角色太泛，Agent 将 actor 修改为“视频学习者”，保留一个结果：点击逐字稿回到对应时间；没有增加搜索、摘要或笔记功能。INVEST 六项均有明确证据。

## User Story 确认

Agent：请确认 US-001 当前表述和范围。

用户：确认，就按“视频学习者”这版。

## 验收条件修改

第一稿 boundary 写成“文字没有时间戳时只提示无法跳转”。用户要求：不能只提示，还要提供重新解析入口。Agent 修改为“不错误跳转，提示缺少时间信息，并提供重新解析入口”。

## 验收条件确认

Agent：success、failure、boundary 三类验收条件已更新，请确认。

用户：确认。

## 写入预览

```text
docs/requirements/video-transcript-jump/
├── user-story.md
└── story-card.json
```

两个文件均为新建；package ID 为 `REQ-VIDEO-TRANSCRIPT-JUMP`；包含 1 条 approved Story、3 条 Acceptance；不会生成 PRD、Spec 或代码。

## 用户批准写入

用户：批准，按这个路径写入。

## 下游钩子

US-001 的边界和验收已经清楚，route 为 `direct_spec`，目标 `SPEC-US-001`。下一步可调用 `spec-writing`；本 Skill 到此不代写 Spec。
