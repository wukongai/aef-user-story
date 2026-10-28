"""三个公开案例的对话和双文件输出回归测试。"""

import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_SCRIPT = ROOT / "scripts" / "validate_story_package.py"
SPEC = importlib.util.spec_from_file_location("validate_story_package", PACKAGE_SCRIPT)
PACKAGE_MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(PACKAGE_MODULE)

CASES = {
    "01-video-transcript-jump": "direct_spec",
    "02-ai-meeting-assistant": "prd",
    "03-ai-content-workflow": "direct_spec",
}


class ExampleTests(unittest.TestCase):
    def test_every_conversation_contains_interaction_and_write_approval(self) -> None:
        markers = (
            "## 用户原始需求",
            "## Agent 复述",
            "## 澄清问题",
            "## User Story 修改",
            "## User Story 确认",
            "## 验收条件修改",
            "## 验收条件确认",
            "## 写入预览",
            "## 用户批准写入",
            "## 下游钩子",
        )
        for case in CASES:
            text = (ROOT / "examples" / case / "conversation.md").read_text(
                encoding="utf-8"
            )
            for marker in markers:
                self.assertIn(marker, text, (case, marker))

    def test_every_project_output_is_a_valid_package(self) -> None:
        for case in CASES:
            requirements = (
                ROOT / "examples" / case / "project-output" / "docs" / "requirements"
            )
            packages = list(requirements.iterdir())
            self.assertEqual(len(packages), 1)
            self.assertEqual(PACKAGE_MODULE.validate_story_package(packages[0]), [])

    def test_expected_route_is_present(self) -> None:
        for case, route in CASES.items():
            card = next((ROOT / "examples" / case / "project-output").rglob("story-card.json"))
            payload = json.loads(card.read_text(encoding="utf-8"))
            self.assertIn(route, {item["route"] for item in payload["next_step"]["items"]})

    def test_each_case_demonstrates_its_key_correction(self) -> None:
        expected = {
            "01-video-transcript-jump": ("视频学习者", "重新解析入口"),
            "02-ai-meeting-assistant": ("至少六条候选 Story", "组织者确认后发布"),
            "03-ai-content-workflow": ("I/E/S/T 不通过", "没有独立审核者"),
        }
        for case, phrases in expected.items():
            text = (ROOT / "examples" / case / "conversation.md").read_text(
                encoding="utf-8"
            )
            for phrase in phrases:
                self.assertIn(phrase, text, (case, phrase))


if __name__ == "__main__":
    unittest.main()
