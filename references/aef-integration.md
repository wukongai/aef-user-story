# AEF 集成边界

## v0.1 事实源

公开仓库 `wukongai/aef-user-story` 是 v0.1 的事实源。普通用户可以单独安装并直接说“帮我拆 User Story”，不需要启动完整 AEF 生命周期。

v0.1 首发不修改 AEF 根 Skill、CLI 或 lifecycle manifest。

## AEF 后续接入方式

AEF 后续集成必须：

1. 固定一个已验证的公开版本或不可变 commit；
2. 复用同一 `SKILL.md`、references、validator 和行为案例；
3. 由 AEF adapter 提供项目上下文、目标路径、gate event 和 manifest 写入；
4. 保留 `user-story-review` 与 `acceptance-review` 两个独立决定；
5. 保存来源版本与验证证据，证明没有手工分叉。

AEF 不得复制 Story 规则到另一个根 Skill。总入口只路由和管理项目状态。

## 职责归属

| 层级 | 负责内容 |
|---|---|
| `aef-user-story` | Story shaping、StoryCard、Acceptance、PRD handoff、结构校验 |
| AEF adapter | 项目事实读取、目标路径、gate 登记、manifest、next stage |
| Target project | facts、Story IDs、Acceptance、评审证据和派生产物 |
| Training content | 教学解释、练习和评审方法 |

训练营天数、课程编号和文章措辞不得进入项目 requirement ID 或 Skill 状态机。

## 交接到 PRD

User Story 表达“谁在什么场景，希望完成什么，并获得什么价值”，Acceptance 表达“外部怎样观察到完成”。Spec 表达系统如何满足已确认需求及其工程约束。

本 Skill 只交付 PRD handoff。正式 PRD、技术/UI 评审、Spec、Plan、TDD 和实现由后续阶段负责。

## 集成门禁

AEF 接入前必须有公开仓库 URL、版本和不可变来源；本版本结构门禁与真实试用证据；独立调用与 AEF 调用差异矩阵；adapter 非覆盖写入和 gate 回归；内容一致性校验；回滚到前一固定版本的路径。

缺少任一项时保持 integration pending，不伪装成已集成。
