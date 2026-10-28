# 旧格式兼容

仅在已有文件属于下述格式或用户明确要求迁移时读取。

### 旧格式兼容

- **0.3 集中包兼容模式**：已有 story-workspace.json 且未选择迁移时，按 [持续维护](continuous-maintenance.md) 保留原能力。转换故事库先预览新目录，保留旧包，不并行维护两个当前入口。
- **传统双文件模式**：已有 StoryCard v1/v2，且只需原流程时保留原能力；读 [格式](user-story-format.md) 与 [项目保存](how-to-save-to-project.md)。双文件需求包仍为 user-story.md 与 story-card.json。不得把新模式内容冒充 v2，也不擅自迁移旧包。

旧 StoryCard v1/v2 切换持续维护模式先预览导入；保留原包，只维护一个当前入口。旧审批保留在来源快照，新模式确认需用户明确认可对应 ID 与修订。


0.3 兼容：python3 -B scripts/story_workspace.py validate <新包> --previous <旧包>。
传统模式：python3 scripts/validate_story_card.py <story-card.json> --json 与 python3 scripts/validate_story_package.py <需求目录> --json。
