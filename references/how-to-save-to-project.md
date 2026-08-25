# 如何把 User Story 保存到项目

## 先发现项目已有规范

按以下顺序只读检查：项目根 Agent 规则；`docs/README.md`、constitution 和结构说明；现有 requirements、stories、product、specs 目录；当前任务的 spec、plan、sprint、daily log 或 handoff。

项目已有明确需求目录时，适配它并说明映射；不要为了本 Skill 平行创建第二套事实源。

## 默认目录

没有现成规范时使用：

```text
docs/requirements/<slug>/
├── user-story.md
└── story-card.json
```

`slug` 使用稳定、简短的英文小写连字符名称。两个文件必须位于同一目录。

## 写入预览

写入前展示目标项目根、需求包目录、两个完整路径、文件是新建还是已存在、package ID、Story/Acceptance 数量、当前状态、下游路由和校验命令。同时给出两个文件的完整候选内容或足以逐项确认的差异。

## 明确批准与冲突停止

用户明确批准当前路径和内容后才能写入。目标路径改变、已有文件内容不同、Story 或 Acceptance 又被修改、项目规则冲突、写入范围不清时，必须停止并重新预览。

不得静默覆盖、合并或删除已有需求文件。若确需更新，展示差异和恢复方式，再单独取得批准。

## 写后校验

```bash
python3 scripts/validate_story_card.py <需求目录>/story-card.json --json
python3 scripts/validate_story_package.py <需求目录> --json
```

第一个检查 JSON 结构、引用、评审和路由；第二个检查双文件存在、package ID、Story ID、Acceptance ID 和 delivery 路径一致。两者都退出 0 才能报告落盘成功。

## 四种下游 route

| route | 何时使用 | 下游钩子 |
|---|---|---|
| `direct_spec` | 单条 Story 和验收已足够清楚 | `spec-writing` |
| `prd` | 多条 Story 还需统一流程、业务规则或角色关系 | `prd-writing` |
| `backlog` | 有价值但本期暂缓 | `backlog-management` |
| `specialist_review` | 需要法律、医疗、金融、隐私、安全、权限、合规、支付或迁移审批 | 对应专项能力 |

PRD 是可选路径。Story 可以直接进入 Spec，但本 Skill 只写下游钩子，不生成下游文档。每条 approved Story 恰好进入一个 route，Acceptance ID 必须随路由传递。

## 对外交付说明

向用户报告需求包路径、包含的 Story、两次确认状态、校验结果、每条 Story 的下一步。结构校验通过不代表业务事实或优先级一定正确；仍存在的 assumption、unknown 和专项风险必须保留。
