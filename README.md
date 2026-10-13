# AEF User Story

基于原 0.2.0 完善的 0.3.0：把产品定义、口述需求或持续反馈整理为 Epic、用户故事和验收条件，并维护局部修改与修订历史。

## 直接使用
读取本目录 SKILL.md 后，告诉 Agent：
- “把这份产品定义整理成 Epic 和用户故事，先给全貌。”
- “只完善 US-003 的边界验收，其他内容不变。”
- “修改 US-003 的目标，保留旧版本并检查验收影响。”

无需先运行 Definition、地图或迭代 Skill。已有背景会复用，只追问本轮必要信息。
本包不制作故事地图、Sprint、产品详细设计、PRD、技术设计或代码。

## 持续产品开发中的位置
随时新增／完善故事 → 迭代规划选择故事 → 细化并确认故事与验收 → 对应的产品详细设计。
本 Skill 维护故事与验收；进入迭代是后续规划决定，不会因新增故事就自动承诺开发。

## 本次新增
- 按 ID 局部操作，其他对象保持原样。
- Epic、Story、验收条件各有稳定 ID 与独立 revision。
- 追加内容快照与确认记录；支持回读旧版、检测过期修改与历史改写。
- 修改故事后旧验收显示待复审；只改验收不重置故事批准。
- 候选故事可先概括，按需细化；就绪故事保留 INVEST 与成功/失败/边界三类验收。

## 两种格式
传统 user-story.md + story-card.json 和 v1/v2 校验保持兼容。
持续维护使用 story-workspace.json + 渲染的 Markdown；迁移需明确选择，新批准不从旧包自动生成。
详见 [持续维护方法与命令](references/continuous-maintenance.md) 和 [局部修改完整案例](examples/04-local-revision/README.md)。

## 验证
```bash
python3 -B -m unittest discover -s tests -p 'test_*.py'
python3 -B scripts/self_test.py
python3 -B scripts/story_workspace.py validate examples/04-local-revision/story-workspace.json
```

工具均为本地 Python 标准库，无网络调用，CLI 只向 stdout 输出候选，不写项目。
校验通过只证明结构/引用/历史规则合法，不证明真实产品效果或人工批准真实性。

## 旧版资料与安装边界
[旧版中文手册](docs/tutorials/aef-user-story-user-manual.zh-CN.md) 的安装与传统双文件流程仍可参考。
使用 `npx skills add wukongai/aef-user-story` 安装仓库版本，安装时选择所需 Agent 与范围。需要固定版本时使用仓库 `v0.3.0` 标签对应内容；父包快照与已有安装不会自动升级。
[旧版交付话术](docs/guides/user-delivery-messages.zh-CN.md) 同样保留。
许可证 MIT，原始许可随包保留。
