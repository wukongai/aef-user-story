#!/usr/bin/env python3
"""运行 aef-user-story 的最小确定性自测。"""

from __future__ import annotations

import json
from pathlib import Path

from validate_story_card import validate_story_card


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    fixtures = skill_root / "tests" / "fixtures"
    valid = json.loads((fixtures / "valid-story-card.json").read_text(encoding="utf-8"))
    invalid = json.loads((fixtures / "invalid-story-card.json").read_text(encoding="utf-8"))

    valid_errors = validate_story_card(valid)
    invalid_errors = validate_story_card(invalid)
    invalid_codes = {item["code"] for item in invalid_errors}
    required_codes = {
        "invalid_enum",
        "illegal_transition",
        "duplicate_id",
        "dangling_reference",
        "missing_coverage",
    }

    checks = {
        "valid_story_card_passes": not valid_errors,
        "invalid_story_card_fails": bool(invalid_errors),
        "invalid_categories_covered": required_codes.issubset(invalid_codes),
        "missing_acceptance_reference_reported": any(
            "AC-MISSING" in item["message"] for item in invalid_errors
        ),
    }
    payload = {"ok": all(checks.values()), "checks": checks}
    print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
