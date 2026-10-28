"""主 Skill 交互状态机与资源路由的静态合同测试。"""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def instructions(self) -> str:
        """只计入从入口可实际到达的本地说明，防止移动后能力失联。"""
        pending, visited, content = [ROOT / 'SKILL.md'], set(), []
        while pending:
            path = pending.pop().resolve()
            if path in visited:
                continue
            self.assertTrue(path.is_relative_to(ROOT.resolve()))
            self.assertTrue(path.is_file(), str(path))
            visited.add(path)
            text = path.read_text(encoding='utf-8')
            content.append(text)
            for target in re.findall(r'\]\(([^)]+)\)', text):
                target = target.split('#')[0]
                if target.endswith('.md') and '://' not in target:
                    pending.append(path.parent / target)
        return '\n'.join(content)

    def test_entry_leads_with_business_and_conditional_support(self):
        text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        headings = ['## 目标', '## 输入', '## 流程', '## 输出', '## 收口与下一步', '## 按需读取的支持规则']
        positions = [text.index(h) for h in headings]
        self.assertEqual(positions, sorted(positions))
        business = text[:text.index('## 按需读取的支持规则')]
        for term in ('story-workspace.json', 'StoryCard v1/v2', '先恢复，再', '旧版兼容'):
            self.assertNotIn(term, business)
        self.assertIn('指定某条故事时直接处理该故事', text)
        self.assertIn('项目已有旧格式文件', text)

    def test_main_skill_contains_all_three_approval_gates(self) -> None:
        text = self.instructions()
        for phrase in (
            "User Story 修改循环",
            "User Story 明确确认",
            "验收条件修改循环",
            "验收条件明确确认",
            "写入预览",
            "写入批准",
        ):
            self.assertIn(phrase, text)

    def test_main_skill_tells_user_available_edits(self) -> None:
        text = self.instructions()
        for phrase in (
            "修改某一条",
            "拆分某一条",
            "合并两条",
            "增加遗漏 Story",
            "暂缓某一条",
        ):
            self.assertIn(phrase, text)

    def test_plain_language_references_exist_and_are_routed(self) -> None:
        text = self.instructions()
        for name in (
            "how-to-write-user-story.md",
            "user-story-format.md",
            "how-to-save-to-project.md",
        ):
            self.assertTrue((ROOT / "references" / name).is_file())
            self.assertIn(name, text)

    def test_v2_skill_does_not_make_prd_or_story_points_mandatory(self) -> None:
        text = self.instructions()
        self.assertIn("PRD 是可选路径", text)
        self.assertIn("不计算 Story Points", text)
        self.assertNotIn("### 3. 选择首个垂直切片", text)

    def test_v2_routes_and_reset_rule_are_explicit(self) -> None:
        text = self.instructions()
        for route in ("direct_spec", "prd", "backlog", "specialist_review"):
            self.assertIn(route, text)
        self.assertIn("关联验收条件失效", text)

    def test_contract_declares_v2_and_project_write_preview(self) -> None:
        text = (ROOT / "skill.contract.yaml").read_text(encoding="utf-8")
        self.assertIn("version: 0.7.0", text)
        self.assertIn("aef-story-card/v2", text)
        self.assertIn("project_write_preview", text)

    def test_main_skill_has_explicit_output_boundary(self) -> None:
        text = self.instructions()
        self.assertIn("## 输出", text)
        self.assertIn("双文件需求包", text)


if __name__ == "__main__":
    unittest.main()
