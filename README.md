# AEF User Story

`aef-user-story` 帮助 AI 编程 Agent 通过可修改、可确认的对话，把模糊产品需求整理成符合 INVEST、带可观察验收条件的 User Story，并安全保存到项目。

## 安装

```bash
npx skills add wukongai/aef-user-story
```

安装器会让你选择目标 Agent，以及项目级或全局安装范围。首次试用建议选择项目级安装，影响范围更小。

## 使用方式

- “我想让用户点击逐字稿就跳回视频，但还没想清楚细节。”
- “录音、转写、总结、任务、搜索、分享这些功能怎么拆成 User Story？”
- “这条 AI 内容工作流 Story 太大了，帮我按 INVEST 重拆。”

本 Skill 会区分事实、假设、未知项、约束和方案建议，识别 Epic，并用 Independent、Negotiable、Valuable、Estimable、Small、Testable 六项证据检查每条 Story。

## 对话与确认

1. Agent 复述需求并给出 Epic、候选 Story 和 INVEST 证据。
2. 用户可以修改、拆分、合并、补充、暂缓或调整 Story；修改完成后明确确认。
3. Agent 只为已确认 Story 生成 success、failure、boundary 三类验收条件。
4. 用户继续修改验收条件，完成后再次明确确认。
5. 写入项目前，Agent 预览路径和两个文件；只有用户明确批准后才写入。

Story 发生变化时，关联验收条件会失效并重新确认。沉默、模糊肯定和前一轮批准都不能替代当前确认。

## 项目交付格式

项目没有既有规范时，默认生成：

```text
docs/requirements/<slug>/
├── user-story.md
└── story-card.json
```

- `user-story.md`：给人阅读和评审。
- `story-card.json`：`aef-story-card/v2` 机器合同，保存 INVEST、两次确认、Acceptance 和下游路由。

已有项目规范优先；已有文件不会被静默覆盖。

## PRD 与下一步

PRD 是可选路径。边界清楚的单条 Story 可以直接进入 Spec；多条 Story 仍需补统一业务流程或规则时再进入 PRD。

每条已批准 Story 恰好选择一个 route：

- `direct_spec`：直接交给后续 Spec 能力；
- `prd`：先补跨 Story 的业务关系；
- `backlog`：明确暂缓；
- `specialist_review`：进入法律、安全、隐私、合规等专项评审。

## 能力边界

本 Skill 不生成正式 PRD、技术 Spec、架构、UI 设计、实施计划、开发 Task、测试代码或业务代码。

## 环境要求

- 支持目录型 Agent Skill 的宿主。
- 推荐使用 Python 3 对 StoryCard JSON 做确定性校验。
- 如果环境没有 Python，Agent 必须明确说明已跳过结构校验。

## 确定性校验

```bash
python3 scripts/validate_story_card.py path/to/story-card.json --json
python3 scripts/validate_story_package.py path/to/requirement-directory --json
```

第一个命令检查 JSON 合同；第二个命令检查人读文档与 JSON 的 package、Story、Acceptance ID 一致。通过只代表结构合法，不代表业务事实和优先级已经被独立验证。

## 完整案例

- [案例一：点击逐字稿回到视频](examples/01-video-transcript-jump/conversation.md)
- [案例二：AI 会议助手功能清单](examples/02-ai-meeting-assistant/conversation.md)
- [案例三：AI 内容工作流大 Story 重拆](examples/03-ai-content-workflow/conversation.md)

每个案例都包含完整对话，以及 `project-output/docs/requirements/...` 下可直接参考的双文件需求包。

## 卸载

使用 Skill 安装器移除 `aef-user-story`，或删除项目级安装链接或目录。不要删除同一配置中的其他 Skill。

## 开源协议

MIT
