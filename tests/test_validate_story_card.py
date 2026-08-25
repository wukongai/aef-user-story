"""StoryCard 校验器的确定性回归测试。"""

import importlib.util
import json
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_ROOT / "scripts" / "validate_story_card.py"
SPEC = importlib.util.spec_from_file_location("validate_story_card", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class StoryCardValidatorTests(unittest.TestCase):
    def test_duplicate_story_does_not_hide_missing_acceptance_reference(self) -> None:
        payload = json.loads(
            (SKILL_ROOT / "tests" / "fixtures" / "invalid-story-card.json").read_text(
                encoding="utf-8"
            )
        )

        errors = MODULE.validate_story_card(payload)

        self.assertTrue(
            any("AC-MISSING" in error["message"] for error in errors),
            errors,
        )


if __name__ == "__main__":
    unittest.main()
