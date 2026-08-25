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


def load_fixture(name: str) -> dict:
    return json.loads(
        (SKILL_ROOT / "tests" / "fixtures" / name).read_text(encoding="utf-8")
    )


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


class StoryCardV2Tests(unittest.TestCase):
    def test_v1_valid_fixture_remains_supported(self) -> None:
        self.assertEqual(MODULE.validate_story_card(load_fixture("valid-story-card.json")), [])

    def test_v2_valid_fixture_passes(self) -> None:
        self.assertEqual(
            MODULE.validate_story_card(load_fixture("valid-story-card-v2.json")), []
        )

    def test_v2_invalid_fixture_reports_all_new_contract_failures(self) -> None:
        errors = MODULE.validate_story_card(load_fixture("invalid-story-card-v2.json"))
        codes = {item["code"] for item in errors}
        self.assertTrue(
            {
                "missing_invest",
                "required_text",
                "illegal_transition",
                "missing_coverage",
                "dangling_reference",
                "duplicate_route",
            }.issubset(codes),
            errors,
        )

    def test_unknown_schema_is_rejected_without_falling_back_to_v1(self) -> None:
        payload = load_fixture("valid-story-card-v2.json")
        payload["schema_version"] = "aef-story-card/v999"
        errors = MODULE.validate_story_card(payload)
        self.assertEqual(errors[0]["code"], "unsupported_schema")


if __name__ == "__main__":
    unittest.main()
