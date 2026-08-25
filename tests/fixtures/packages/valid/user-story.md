---
schema_version: aef-story-card/v2
package_id: REQ-PKG-001
status: ready_for_spec
---

# 点击逐字稿跳转视频

### US-001：点击逐字稿跳转视频

作为视频学习者，当我阅读逐字稿时，我希望点击文字跳到对应视频位置，从而快速回看相关内容。

### AC-US-001-S：成功路径

- Given 已有带时间戳逐字稿
- When 点击文字
- Then 跳到对应时间

### AC-US-001-F：失败路径

- Given 解析失败
- When 打开逐字稿
- Then 显示失败和重试入口

### AC-US-001-B：边界路径

- Given 文字无时间戳
- When 点击文字
- Then 不错误跳转并提示
