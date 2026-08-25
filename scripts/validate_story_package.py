#!/usr/bin/env python3
"""校验 User Story 人读文档与 StoryCard JSON 的双文件一致性。"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any


FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
STORY_PATTERN = re.compile(r"^###\s+(US-\d+)[:：]", re.MULTILINE)
ACCEPTANCE_PATTERN = re.compile(
    r"^###\s+(AC-US-\d+-(?:S|F|B)\d*)[:：]", re.MULTILINE
)
SCRIPT_DIR = Path(__file__).resolve().parent
CARD_SCRIPT = SCRIPT_DIR / "validate_story_card.py"
CARD_SPEC = importlib.util.spec_from_file_location("aef_validate_story_card", CARD_SCRIPT)
CARD_MODULE = importlib.util.module_from_spec(CARD_SPEC)
assert CARD_SPEC and CARD_SPEC.loader
CARD_SPEC.loader.exec_module(CARD_MODULE)
validate_story_card = CARD_MODULE.validate_story_card


def _add(errors: list[dict[str, str]], code: str, path: str, message: str) -> None:
    errors.append({"code": code, "path": path, "message": message})


def _parse_frontmatter(text: str) -> dict[str, str]:
    """解析当前合同所需的简单标量 frontmatter。"""

    match = FRONTMATTER_PATTERN.search(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def validate_story_package(package_dir: Path) -> list[dict[str, str]]:
    """返回双文件需求包的结构化错误；空列表表示通过。"""

    errors: list[dict[str, str]] = []
    human_path = package_dir / "user-story.md"
    machine_path = package_dir / "story-card.json"
    if not human_path.is_file():
        _add(errors, "missing_file", "user-story.md", "缺少人读需求文档")
    if not machine_path.is_file():
        _add(errors, "missing_file", "story-card.json", "缺少机器可读 StoryCard")
    if errors:
        return errors

    try:
        human_text = human_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        return [{"code": "input_error", "path": "user-story.md", "message": str(error)}]
    try:
        payload = json.loads(machine_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        return [{"code": "input_error", "path": "story-card.json", "message": str(error)}]

    errors.extend(validate_story_card(payload))
    if not isinstance(payload, dict):
        return errors

    frontmatter = _parse_frontmatter(human_text)
    if not frontmatter:
        _add(errors, "missing_frontmatter", "user-story.md", "缺少 YAML frontmatter")
    markdown_package_id = frontmatter.get("package_id")
    json_package_id = payload.get("package_id")
    if markdown_package_id != json_package_id:
        _add(
            errors,
            "package_id_mismatch",
            "package_id",
            f"Markdown={markdown_package_id!r}，JSON={json_package_id!r}",
        )

    markdown_story_ids = set(STORY_PATTERN.findall(human_text))
    json_story_ids = {
        item.get("story_id")
        for item in payload.get("stories", [])
        if isinstance(item, dict) and isinstance(item.get("story_id"), str)
    }
    if markdown_story_ids != json_story_ids:
        _add(
            errors,
            "story_id_mismatch",
            "stories",
            f"Markdown={sorted(markdown_story_ids)}，JSON={sorted(json_story_ids)}",
        )

    markdown_acceptance_ids = set(ACCEPTANCE_PATTERN.findall(human_text))
    json_acceptance_ids = {
        item.get("acceptance_id")
        for item in payload.get("acceptance", [])
        if isinstance(item, dict) and isinstance(item.get("acceptance_id"), str)
    }
    if markdown_acceptance_ids != json_acceptance_ids:
        _add(
            errors,
            "acceptance_id_mismatch",
            "acceptance",
            f"Markdown={sorted(markdown_acceptance_ids)}，JSON={sorted(json_acceptance_ids)}",
        )

    delivery = payload.get("delivery")
    if isinstance(delivery, dict):
        expected = {
            "human_file": "./user-story.md",
            "machine_file": "./story-card.json",
        }
        for key, expected_value in expected.items():
            if delivery.get(key) != expected_value:
                _add(
                    errors,
                    "invalid_delivery_path",
                    f"delivery.{key}",
                    f"必须是 {expected_value}",
                )
    return errors


def _emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload.get("valid"):
        print("PASS User Story package valid")
        return
    for error in payload.get("errors", []):
        print(f"FAIL {error['path']} [{error['code']}] {error['message']}")


def main(argv: list[str] | None = None) -> int:
    """校验一个双文件需求包目录并返回稳定退出码。"""

    args = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in args
    args = [item for item in args if item != "--json"]
    if len(args) != 1:
        errors = [
            {
                "code": "usage",
                "path": "$",
                "message": "用法: validate_story_package.py <directory> [--json]",
            }
        ]
        _emit({"valid": False, "errors": errors}, as_json)
        return 2

    errors = validate_story_package(Path(args[0]))
    _emit({"valid": not errors, "errors": errors}, as_json)
    if any(item["code"] == "input_error" for item in errors):
        return 2
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
