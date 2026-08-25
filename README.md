# AEF User Story

`aef-user-story` 帮助 AI 编程 Agent 把模糊产品需求整理成可评审的 User Story，避免在需求尚未确认时直接进入 PRD、Spec 或代码。

## 安装

```bash
npx skills add wukongai/aef-user-story
```

安装器会让你选择目标 Agent，以及项目级或全局安装范围。首次试用建议选择项目级安装，影响范围更小。

## 使用方式

- “我有个模糊的产品想法，帮我整理成 User Story。”
- “这些功能应该怎样拆成用户故事？”
- “帮我判断第一版应该先做哪一刀。”
- “给已确认的 Story 补充 Acceptance Criteria。”

本 Skill 会区分事实、假设、未知项、约束和方案建议，识别 Epic，形成垂直 User Story，并推荐首个价值切片。

## 两次确认门禁

1. **User Story 评审：**确认 Epic、候选 Story、首个切片、暂缓项和非目标。
2. **验收条件评审：**确认已批准 Story 的成功、失败和边界条件。

只有两次确认都通过后，Skill 才会生成结构化的 PRD 交接材料。

## 能力边界

本 Skill 不生成正式 PRD、技术 Spec、架构、UI 设计、实施计划、测试代码或业务代码。

## 环境要求

- 支持目录型 Agent Skill 的宿主。
- 推荐使用 Python 3 对 StoryCard JSON 做确定性校验。
- 如果环境没有 Python，Agent 必须明确说明已跳过结构校验。

## 校验 StoryCard

```bash
python3 scripts/validate_story_card.py path/to/story-card.json --json
```

## 卸载

使用 Skill 安装器移除 `aef-user-story`，或删除项目级安装链接或目录。不要删除同一配置中的其他 Skill。

## 开源协议

MIT
