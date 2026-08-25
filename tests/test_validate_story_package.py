"""User Story 双文件需求包的一致性回归测试。"""

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures" / "packages"
SCRIPT_PATH = ROOT / "scripts" / "validate_story_package.py"
SPEC = importlib.util.spec_from_file_location("validate_story_package", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class StoryPackageValidatorTests(unittest.TestCase):
    def test_valid_package_passes(self) -> None:
        self.assertEqual(MODULE.validate_story_package(FIXTURES / "valid"), [])

    def test_mismatched_markdown_and_json_ids_fail(self) -> None:
        errors = MODULE.validate_story_package(FIXTURES / "mismatched")
        codes = {item["code"] for item in errors}
        self.assertIn("package_id_mismatch", codes)
        self.assertIn("story_id_mismatch", codes)
        self.assertIn("acceptance_id_mismatch", codes)

    def test_missing_human_file_fails(self) -> None:
        errors = MODULE.validate_story_package(FIXTURES / "missing")
        self.assertTrue(any(item["path"] == "user-story.md" for item in errors))


if __name__ == "__main__":
    unittest.main()
