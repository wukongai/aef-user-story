#!/usr/bin/env python3
"""确定性校验 AEF StoryCard JSON 的结构、引用和评审状态。"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


STORY_STATUSES = {"candidate", "selected", "deferred", "approved"}
STORY_REVIEW_STATES = {"candidate", "awaiting_confirmation", "approved", "rejected"}
ACCEPTANCE_REVIEW_STATES = {
    "not_started",
    "draft",
    "awaiting_confirmation",
    "approved",
    "rejected",
}
ACCEPTANCE_TYPES = {"success", "failure", "boundary"}


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _add(errors: list[dict[str, str]], code: str, path: str, message: str) -> None:
    errors.append({"code": code, "path": path, "message": message})


def _require_text(
    value: Any,
    path: str,
    errors: list[dict[str, str]],
    code: str = "required_text",
) -> None:
    if not _is_text(value):
        _add(errors, code, path, "必须是非空字符串")


def _require_list(
    value: Any,
    path: str,
    errors: list[dict[str, str]],
) -> list[Any]:
    if not isinstance(value, list):
        _add(errors, "invalid_type", path, "必须是数组")
        return []
    return value


def validate_story_card(payload: dict) -> list[dict[str, str]]:
    """返回结构化错误；空列表表示 StoryCard 通过确定性校验。"""

    errors: list[dict[str, str]] = []
    if not isinstance(payload, dict):
        return [{"code": "invalid_type", "path": "$", "message": "顶层必须是对象"}]

    required_top = {
        "schema_version",
        "artifact_type",
        "review_state",
        "source_summary",
        "facts",
        "assumptions",
        "unknowns",
        "constraints",
        "epic",
        "stories",
        "selected_story_id",
        "vertical_slice_review",
        "acceptance",
        "non_goals",
        "deferred_story_ids",
        "prd_handoff",
    }
    for key in sorted(required_top):
        if key not in payload:
            _add(errors, "missing_field", key, "缺少顶层字段")

    if payload.get("schema_version") != "aef-story-card/v1":
        _add(errors, "invalid_enum", "schema_version", "必须是 aef-story-card/v1")
    if payload.get("artifact_type") != "aef-story-card":
        _add(errors, "invalid_enum", "artifact_type", "必须是 aef-story-card")
    _require_text(payload.get("source_summary"), "source_summary", errors)

    for key in ("facts", "assumptions", "unknowns", "constraints", "non_goals"):
        _require_list(payload.get(key), key, errors)

    review_state = payload.get("review_state")
    if not isinstance(review_state, dict):
        _add(errors, "invalid_type", "review_state", "必须是对象")
        review_state = {}
    story_review = review_state.get("story")
    acceptance_review = review_state.get("acceptance")
    if story_review not in STORY_REVIEW_STATES:
        _add(errors, "invalid_enum", "review_state.story", "Story 评审状态无效")
    if acceptance_review not in ACCEPTANCE_REVIEW_STATES:
        _add(errors, "invalid_enum", "review_state.acceptance", "Acceptance 评审状态无效")
    if acceptance_review == "approved" and story_review != "approved":
        _add(
            errors,
            "illegal_transition",
            "review_state",
            "Story 未 approved 时 Acceptance 不能 approved",
        )

    epic = payload.get("epic")
    if not isinstance(epic, dict):
        _add(errors, "invalid_type", "epic", "必须是对象")
        epic = {}
    for key in ("epic_id", "title", "outcome"):
        _require_text(epic.get(key), f"epic.{key}", errors)

    stories = _require_list(payload.get("stories"), "stories", errors)
    if not stories:
        _add(errors, "empty_collection", "stories", "至少需要一条 Story")

    story_ids: set[str] = set()
    story_statuses: dict[str, str] = {}
    story_acceptance_refs: dict[str, set[str]] = {}
    for index, story in enumerate(stories):
        base = f"stories[{index}]"
        if not isinstance(story, dict):
            _add(errors, "invalid_type", base, "Story 必须是对象")
            continue
        for key in ("story_id", "actor", "scenario", "goal", "value", "statement"):
            _require_text(story.get(key), f"{base}.{key}", errors)
        story_id = story.get("story_id")
        if _is_text(story_id):
            if story_id in story_ids:
                _add(errors, "duplicate_id", f"{base}.story_id", f"重复 Story ID: {story_id}")
            story_ids.add(story_id)
            story_statuses[story_id] = str(story.get("status", ""))
        status = story.get("status")
        if status not in STORY_STATUSES:
            _add(errors, "invalid_enum", f"{base}.status", "Story 状态无效")
        _require_list(story.get("source_refs"), f"{base}.source_refs", errors)
        refs = _require_list(story.get("acceptance_ids"), f"{base}.acceptance_ids", errors)
        if _is_text(story_id):
            story_acceptance_refs.setdefault(story_id, set()).update(
                item for item in refs if _is_text(item)
            )

    selected_story_id = payload.get("selected_story_id")
    _require_text(selected_story_id, "selected_story_id", errors)
    if _is_text(selected_story_id) and selected_story_id not in story_ids:
        _add(errors, "dangling_reference", "selected_story_id", "未引用现有 Story")

    deferred_ids = _require_list(payload.get("deferred_story_ids"), "deferred_story_ids", errors)
    for index, story_id in enumerate(deferred_ids):
        if not _is_text(story_id) or story_id not in story_ids:
            _add(
                errors,
                "dangling_reference",
                f"deferred_story_ids[{index}]",
                "未引用现有 Story",
            )

    slice_review = payload.get("vertical_slice_review")
    if not isinstance(slice_review, dict):
        _add(errors, "invalid_type", "vertical_slice_review", "必须是对象")
        slice_review = {}
    if not isinstance(slice_review.get("is_vertical"), bool):
        _add(errors, "invalid_type", "vertical_slice_review.is_vertical", "必须是布尔值")
    _require_text(slice_review.get("rationale"), "vertical_slice_review.rationale", errors)
    _require_list(
        slice_review.get("rejected_horizontal_splits"),
        "vertical_slice_review.rejected_horizontal_splits",
        errors,
    )

    acceptance = _require_list(payload.get("acceptance"), "acceptance", errors)
    acceptance_ids: set[str] = set()
    coverage: dict[str, set[str]] = {}
    for index, item in enumerate(acceptance):
        base = f"acceptance[{index}]"
        if not isinstance(item, dict):
            _add(errors, "invalid_type", base, "Acceptance 必须是对象")
            continue
        for key in ("acceptance_id", "story_id", "given", "when", "then"):
            _require_text(item.get(key), f"{base}.{key}", errors)
        acceptance_id = item.get("acceptance_id")
        story_id = item.get("story_id")
        acceptance_type = item.get("type")
        if _is_text(acceptance_id):
            if acceptance_id in acceptance_ids:
                _add(errors, "duplicate_id", f"{base}.acceptance_id", f"重复 Acceptance ID: {acceptance_id}")
            acceptance_ids.add(acceptance_id)
        if not _is_text(story_id) or story_id not in story_ids:
            _add(errors, "dangling_reference", f"{base}.story_id", "未引用现有 Story")
        if acceptance_type not in ACCEPTANCE_TYPES:
            _add(errors, "invalid_enum", f"{base}.type", "Acceptance 类型无效")
        if _is_text(story_id) and acceptance_type in ACCEPTANCE_TYPES:
            coverage.setdefault(story_id, set()).add(acceptance_type)

    for story_id, refs in story_acceptance_refs.items():
        for acceptance_id in refs:
            if acceptance_id not in acceptance_ids:
                _add(
                    errors,
                    "dangling_reference",
                    f"story:{story_id}.acceptance_ids",
                    f"未找到 Acceptance: {acceptance_id}",
                )

    if acceptance_review == "approved":
        required_types = ACCEPTANCE_TYPES
        for story_id, status in story_statuses.items():
            if status == "approved":
                missing = sorted(required_types - coverage.get(story_id, set()))
                if missing:
                    _add(
                        errors,
                        "missing_coverage",
                        f"story:{story_id}.acceptance",
                        f"缺少 Acceptance 类型: {', '.join(missing)}",
                    )

    handoff = payload.get("prd_handoff")
    if not isinstance(handoff, dict):
        _add(errors, "invalid_type", "prd_handoff", "必须是对象")
        handoff = {}
    handoff_status = handoff.get("status")
    if handoff_status not in {"draft", "blocked", "ready"}:
        _add(errors, "invalid_enum", "prd_handoff.status", "handoff 状态无效")
    approved_ids = _require_list(
        handoff.get("approved_story_ids"),
        "prd_handoff.approved_story_ids",
        errors,
    )
    _require_list(handoff.get("open_questions"), "prd_handoff.open_questions", errors)
    for index, story_id in enumerate(approved_ids):
        if story_id not in story_ids or story_statuses.get(story_id) != "approved":
            _add(
                errors,
                "dangling_reference",
                f"prd_handoff.approved_story_ids[{index}]",
                "必须引用 approved Story",
            )
    if handoff_status == "ready" and (
        story_review != "approved" or acceptance_review != "approved"
    ):
        _add(
            errors,
            "illegal_transition",
            "prd_handoff.status",
            "两个评审均 approved 后 handoff 才能 ready",
        )

    return errors


def _emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True))
        return
    if payload.get("valid"):
        print("PASS StoryCard valid")
        return
    for error in payload.get("errors", []):
        print(f"FAIL {error['path']} [{error['code']}] {error['message']}")


def main(argv: list[str] | None = None) -> int:
    """校验单个 StoryCard 文件，返回稳定退出码。"""

    args = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in args
    args = [item for item in args if item != "--json"]
    if len(args) != 1:
        _emit(
            {
                "valid": False,
                "errors": [
                    {
                        "code": "usage",
                        "path": "$",
                        "message": "用法: validate_story_card.py <story-card.json> [--json]",
                    }
                ],
            },
            as_json,
        )
        return 2

    path = Path(args[0])
    try:
        raw = path.read_text(encoding="utf-8")
        payload = json.loads(raw)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        _emit(
            {
                "valid": False,
                "errors": [{"code": "input_error", "path": str(path), "message": str(error)}],
            },
            as_json,
        )
        return 2

    errors = validate_story_card(payload)
    _emit({"valid": not errors, "errors": errors}, as_json)
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
