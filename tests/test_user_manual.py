import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "docs" / "tutorials" / "aef-user-story-user-manual.zh-CN.md"
DELIVERY = ROOT / "docs" / "guides" / "user-delivery-messages.zh-CN.md"


def strip_frontmatter(text: str) -> str:
    """移除 Obsidian/Pudding 投影文件的 YAML 元数据。"""
    if not text.startswith("---\n"):
        return text.strip()
    end = text.find("\n---\n", 4)
    if end == -1:
        return text.strip()
    return text[end + 5 :].strip()


class UserManualTests(unittest.TestCase):
    def test_manual_and_delivery_guide_exist_and_are_linked(self):
        self.assertTrue(MANUAL.is_file())
        self.assertTrue(DELIVERY.is_file())
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("docs/tutorials/aef-user-story-user-manual.zh-CN.md", readme)
        self.assertIn("docs/guides/user-delivery-messages.zh-CN.md", readme)

    def test_manual_is_a_progressive_user_walkthrough(self):
        text = MANUAL.read_text(encoding="utf-8")
        required_headings = [
            "第一步：把 Skill 交给 Agent",
            "第二步：说出一句模糊需求",
            "第三步：修改并确认 User Story",
            "第四步：修改并确认验收条件",
            "第五步：批准写入项目",
            "第六步：选择下一步",
            "第七步：换成你自己的需求",
        ]
        for heading in required_headings:
            self.assertIn(heading, text)

        self.assertGreaterEqual(text.count("你可以直接对 Agent 说"), 7)
        self.assertGreaterEqual(len(re.findall(r"```text\n", text)), 10)
        self.assertIn("Agent 会做什么", text)
        self.assertIn("你要检查什么", text)

    def test_manual_contains_three_real_cases_and_project_output(self):
        text = MANUAL.read_text(encoding="utf-8")
        for case in [
            "案例一：一句模糊需求变成一条 Story",
            "案例二：一堆功能拆成 Epic 和多条 Story",
            "案例三：一句完整但过大的 Story 重新拆分",
        ]:
            self.assertIn(case, text)

        for term in [
            "INVEST",
            "success、failure、boundary",
            "docs/requirements/<slug>/",
            "user-story.md",
            "story-card.json",
            "direct_spec",
            "prd",
            "backlog",
            "specialist_review",
        ]:
            self.assertIn(term, text)

        self.assertIn("确认 User Story", text)
        self.assertIn("确认验收条件", text)
        self.assertIn("批准写入", text)

    def test_delivery_guide_contains_three_copyable_variants(self):
        text = DELIVERY.read_text(encoding="utf-8")
        for section in ["私聊交付版", "极简链接版", "群公告版"]:
            self.assertIn(section, text)
        self.assertGreaterEqual(len(re.findall(r"```text\n", text)), 3)
        self.assertIn("https://github.com/wukongai/aef-user-story", text)

    def test_public_files_do_not_leak_pudding_private_metadata(self):
        forbidden = ["pudding_id:", "pudding_url:", "pudding_synced:"]
        for path in [MANUAL, DELIVERY, ROOT / "README.md"]:
            text = path.read_text(encoding="utf-8")
            for marker in forbidden:
                self.assertNotIn(marker, text)

    def test_optional_pudding_projection_matches_public_manual(self):
        projected_path = os.environ.get("AEF_USER_STORY_PUDDING_MANUAL")
        if not projected_path:
            self.skipTest("未提供布丁投影路径")
        public_body = MANUAL.read_text(encoding="utf-8").strip()
        projected_body = strip_frontmatter(
            Path(projected_path).read_text(encoding="utf-8")
        )
        self.assertEqual(public_body, projected_body)


if __name__ == "__main__":
    unittest.main()
