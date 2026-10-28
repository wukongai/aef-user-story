# AEF User Story 用户手册与外部文档平台交付测试报告

## 目标

为公开用户提供一份可以从第一步开始照做的中文操作手册，并把同一正文投影到外部文档平台。手册必须使用真实案例说明交互确认和项目落盘，而不是只介绍 User Story 概念。

## 自动检查范围

- 七个渐进步骤：安装、输入模糊需求、确认 Story、确认验收条件、批准写入、选择下一步、替换真实需求。
- 每步包含可复制话术、Agent 行为和用户检查点。
- 三类真实案例：单条模糊需求、Epic 功能清单、过大 Story 重拆。
- 默认双文件路径、INVEST、三类 Acceptance 和四种下游 route。
- 私聊、短链接、群公告三套交付话术。
- 公开文件不得包含外部文档平台 ID、后台 URL 或同步状态。
- 可选环境变量检查公开正文与 Obsidian/外部文档平台投影正文完全一致。

## 验证命令

```bash
python3 -m unittest tests.test_user_manual -v
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/self_test.py
```

外部文档平台投影生成后，额外使用：

```bash
AEF_USER_STORY_PUDDING_MANUAL='<Obsidian 投影路径>' python3 -m unittest tests.test_user_manual -v
```

## 当前结论

手册专项测试已经完成 RED → GREEN，发布前本地验证结果如下：

| 检查 | 结果 |
|---|---|
| 全量 unittest | 25 项通过；默认运行跳过 1 项需要显式投影路径的检查 |
| 带 Obsidian 路径的手册测试 | 6/6 通过，公开正文与投影正文一致 |
| `scripts/self_test.py` | `ok: true` |
| Content Completion Gate | pass，无 finding |
| Production Creation Review | 100/A，四个维度均为 100 |
| Portable Skill Self Test | pass，`target_unchanged: true` |
| 公开内容隐私扫描 | 新增公开文件未包含本机路径或外部文档平台私有字段 |

这些结果证明文档结构、Skill 合同和投影一致性通过确定性检查，不代替独立用户对手册易用性的真实试用。GitHub 与外部文档平台远端状态属于外部发布结果，由交付时的远端检查单独确认。
