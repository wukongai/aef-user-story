---
schema_version: aef-story-card/v2
package_id: REQ-VIDEO-TRANSCRIPT-JUMP
status: ready_for_spec
---

# 点击逐字稿回到视频

## 原始需求

用户希望点击视频转出的文字，跳到对应视频位置。

## 信息边界

- facts：需要文字到视频时间位置的跳转。
- assumptions：首版主要用户是视频学习者，已由用户确认。
- unknowns：首版支持哪些视频来源。
- constraints：不锁定转写技术。

## Epic

EPIC-001：提升长视频学习和回看效率；包含 US-001。

## User Stories

### US-001：点击逐字稿跳转视频

作为视频学习者，当我阅读带时间信息的逐字稿时，我希望点击文字跳到对应视频位置，从而快速回看相关原始内容。

INVEST：六项通过；单一用户结果、未锁定实现、范围可估算并有三类验收。

## Acceptance

### AC-US-001-S：成功跳转

- Given 视频已有带时间信息的逐字稿
- When 用户点击任意一句文字
- Then 视频跳转并播放该句对应的位置

### AC-US-001-F：解析失败

- Given 视频逐字稿解析失败
- When 用户打开逐字稿区域
- Then 系统显示失败原因和重新解析入口

### AC-US-001-B：文字缺少时间信息

- Given 某句文字没有有效时间信息
- When 用户点击该句文字
- Then 系统不改变播放位置，说明无法定位并提供重新解析入口

## 范围

- included：点击逐字稿定位视频。
- excluded：全文搜索、摘要、翻译和学习笔记。

## 确认记录

- Story：approved；角色由“视频用户”修改为“视频学习者”后明确确认。
- Acceptance：approved；boundary 增加重新解析入口后明确确认。

## 下一步

US-001 → `direct_spec` → `SPEC-US-001` → `docs/specs/SPEC-US-001.md`。
