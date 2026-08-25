# 更新日志

这里记录所有用户可感知的重要变化。

## [0.2.0] - 2026-08-25

### 新增

- User Story 与验收条件各自可修改、可循环、可明确确认的互动流程。
- `aef-story-card/v2`：INVEST 证据、双确认、双文件交付与多项下游路由。
- `validate_story_package.py`，校验 `user-story.md` 与 `story-card.json` 的 ID 和路径一致性。
- 三个完整中文对话案例及其项目落盘输出。

### 变更

- INVEST 成为 Story 质量检查核心，不在本阶段进行工作量点数评估。
- PRD 从唯一交接方向改为可选 route；需求清楚时可直接进入 Spec。
- 默认项目输出改为 `docs/requirements/<slug>/` 下的双文件需求包。

### 兼容

- 新输出统一使用 v2；StoryCard 验证器继续接受 v1，保留旧字段校验行为。

## [0.1.0] - 2026-08-25

### 新增

- 模糊需求摄入，分开保存事实、假设、未知项、约束和方案想法。
- Epic 识别、User Story 拆分和首个范围建议。
- 独立的 Story Review 与 Acceptance Review 门禁。
- success、failure、boundary 三类验收条件。
- 结构化 StoryCard 与 PRD 交接合同。
- 确定性 StoryCard JSON 验证器和回归案例。
