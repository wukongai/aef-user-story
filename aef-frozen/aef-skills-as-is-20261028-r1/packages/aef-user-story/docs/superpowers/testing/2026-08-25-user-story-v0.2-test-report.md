# aef-user-story 0.2.0 测试报告

## 结论

0.2.0 本地候选已通过结构、回归、内容、安全和可移植自测门禁，可以进入 Git 合并、tag 与公开推送阶段。

本结论只证明结构 readiness 与设计行为回归，不宣称已经通过独立用户效用验证。

## 测试对象

- 分支：`codex/user-story-v0.2`
- schema：新输出 `aef-story-card/v2`，读取兼容 `aef-story-card/v1`
- 交付：`user-story.md` + `story-card.json`
- 案例：视频逐字稿、AI 会议助手、AI 内容工作流

## 确定性回归

| 范围 | 命令 | 结果 |
|---|---|---|
| v1/v2 StoryCard | `python3 tests/test_validate_story_card.py -v` | 5/5 通过 |
| 双文件需求包 | `python3 tests/test_validate_story_package.py -v` | 3/3 通过 |
| 主 Skill 互动合同 | `python3 tests/test_skill_contract.py -v` | 7/7 通过 |
| 三个公开案例 | `python3 tests/test_examples.py -v` | 4/4 通过 |
| 聚合自测 | `python3 scripts/self_test.py` | `ok: true` |

共 19 个 unittest 通过。

## 兼容与合同证据

- v1 有效 fixture 继续通过；v1 的旧字段仍由独立分支校验。
- 未知 schema 返回 `unsupported_schema`，不伪装成 v1。
- v2 覆盖六项 INVEST、两次确认、三类 Acceptance、引用完整性和下游 route 唯一性。
- 双文件校验覆盖 package ID、Story ID、Acceptance ID 和相对 delivery 路径。

## 案例证据

- 案例一完成 actor 与 boundary Acceptance 的两轮修改，最终 `direct_spec`。
- 案例二把功能清单识别为 Epic，保留六条 Story，批准三条并暂缓三条，最终 `prd`。
- 案例三记录原大 Story 的 INVEST 失败，移除虚构审核角色，四条 Story 分别 `direct_spec`。
- 三个案例的项目输出均通过 `validate_story_package.py`。

## Skill Engineering 门禁

| 门禁 | 结果 |
|---|---|
| Content Completion Gate | pass，无 finding |
| Production Creation Review | 100/A，四个维度均 100 |
| Portable Self Test | pass |
| Portable target unchanged | true |
| 脚本编译 | pass |
| 公开内容扫描 | 零命中 |

本机没有安装 `skill-engineering` CLI，因此没有伪造维护计划 ID。实施使用 Git worktree 作为独立候选，按显式提交保存 RED、实现、案例、文档与验证历史；可通过 Git 提交安全恢复。

## 安全与副作用

- 两个校验脚本默认只读；无参数时稳定退出 2。
- 项目写入必须经过路径与内容预览、明确批准；已有文件禁止静默覆盖。
- Portable Self Test 在临时副本运行，并确认候选目录运行前后未变化。
- 公开内容扫描未发现本机绝对路径、课程绑定、点数建议字段或占位语料。

## 未覆盖与诚实边界

- 三个案例由作者上下文编写，只能证明预设行为和落盘合同，不是独立 fresh-context rollout。
- `tests/baseline.json` 保持 `baseline_pending` 与 `utility: false`。
- 外部 Agent 真实安装与独立用户试用证据尚未形成，不影响 0.2.0 作为公开候选发布，但不能据此宣称效用已被普遍验证。
