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
INVEST_KEYS = {
    "independent",
    "negotiable",
    "valuable",
    "estimable",
    "small",
    "testable",
}
INVEST_STATUSES = {"pass", "risk", "fail"}
ROUTES = {"direct_spec", "prd", "backlog", "specialist_review"}


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


def _validate_v1(payload: dict[str, Any]) -> list[dict[str, str]]:
    """校验 aef-story-card/v1；保留 0.1.0 行为。"""

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


def _validate_invest(
    review: object,
    base: str,
    errors: list[dict[str, str]],
) -> bool:
    """校验六项 INVEST，并返回是否全部通过。"""

    if not isinstance(review, dict):
        _add(errors, "invalid_type", base, "必须是对象")
        return False
    all_pass = True
    for key in sorted(INVEST_KEYS):
        if key not in review:
            _add(errors, "missing_invest", f"{base}.{key}", "缺少 INVEST 项")
            all_pass = False
            continue
        item = review[key]
        if not isinstance(item, dict):
            _add(errors, "invalid_type", f"{base}.{key}", "必须是对象")
            all_pass = False
            continue
        status = item.get("status")
        if status not in INVEST_STATUSES:
            _add(errors, "invalid_enum", f"{base}.{key}.status", "INVEST 状态无效")
            all_pass = False
        elif status != "pass":
            all_pass = False
        _require_text(item.get("reason"), f"{base}.{key}.reason", errors)
    return all_pass


def _validate_v2(payload: dict[str, Any]) -> list[dict[str, str]]:
    """校验 aef-story-card/v2 的结构、确认状态、覆盖和路由。"""

    errors: list[dict[str, str]] = []
    required_top = {
        "schema_version",
        "artifact_type",
        "package_id",
        "status",
        "source",
        "epic",
        "stories",
        "acceptance",
        "scope",
        "reviews",
        "delivery",
        "next_step",
    }
    for key in sorted(required_top):
        if key not in payload:
            _add(errors, "missing_field", key, "缺少顶层字段")

    if payload.get("artifact_type") != "aef-story-card":
        _add(errors, "invalid_enum", "artifact_type", "必须是 aef-story-card")
    _require_text(payload.get("package_id"), "package_id", errors)
    status = payload.get("status")
    if status not in {"draft", "awaiting_story_confirmation", "awaiting_acceptance_confirmation", "ready_for_spec", "ready_for_prd", "backlog", "blocked"}:
        _add(errors, "invalid_enum", "status", "StoryCard 状态无效")

    source = payload.get("source")
    if not isinstance(source, dict):
        _add(errors, "invalid_type", "source", "必须是对象")
        source = {}
    _require_text(source.get("summary"), "source.summary", errors)
    for key in ("facts", "assumptions", "unknowns", "constraints"):
        _require_list(source.get(key), f"source.{key}", errors)

    epic = payload.get("epic")
    if not isinstance(epic, dict):
        _add(errors, "invalid_type", "epic", "必须是对象")
        epic = {}
    for key in ("epic_id", "title", "status"):
        _require_text(epic.get(key), f"epic.{key}", errors)
    epic_story_ids = _require_list(epic.get("story_ids"), "epic.story_ids", errors)

    stories = _require_list(payload.get("stories"), "stories", errors)
    if not stories:
        _add(errors, "empty_collection", "stories", "至少需要一条 Story")
    story_ids: set[str] = set()
    approved_story_ids: set[str] = set()
    story_acceptance_refs: dict[str, set[str]] = {}
    invest_pass: dict[str, bool] = {}
    for index, story in enumerate(stories):
        base = f"stories[{index}]"
        if not isinstance(story, dict):
            _add(errors, "invalid_type", base, "Story 必须是对象")
            continue
        for key in ("story_id", "title", "actor", "scenario", "goal", "value", "statement"):
            _require_text(story.get(key), f"{base}.{key}", errors)
        story_id = story.get("story_id")
        if _is_text(story_id):
            if story_id in story_ids:
                _add(errors, "duplicate_id", f"{base}.story_id", f"重复 Story ID: {story_id}")
            story_ids.add(story_id)
            if story.get("status") == "approved":
                approved_story_ids.add(story_id)
            invest_pass[story_id] = _validate_invest(
                story.get("invest_review"), f"{base}.invest_review", errors
            )
        elif "invest_review" in story:
            _validate_invest(story.get("invest_review"), f"{base}.invest_review", errors)
        if story.get("status") not in STORY_STATUSES:
            _add(errors, "invalid_enum", f"{base}.status", "Story 状态无效")
        refs = _require_list(story.get("acceptance_ids"), f"{base}.acceptance_ids", errors)
        if _is_text(story_id):
            story_acceptance_refs[story_id] = {item for item in refs if _is_text(item)}

    for index, story_id in enumerate(epic_story_ids):
        if not _is_text(story_id) or story_id not in story_ids:
            _add(errors, "dangling_reference", f"epic.story_ids[{index}]", "未引用现有 Story")

    acceptance = _require_list(payload.get("acceptance"), "acceptance", errors)
    acceptance_ids: set[str] = set()
    acceptance_owner: dict[str, str] = {}
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
            if _is_text(story_id):
                acceptance_owner[acceptance_id] = story_id
        if not _is_text(story_id) or story_id not in story_ids:
            _add(errors, "dangling_reference", f"{base}.story_id", "未引用现有 Story")
        if acceptance_type not in ACCEPTANCE_TYPES:
            _add(errors, "invalid_enum", f"{base}.type", "Acceptance 类型无效")
        if _is_text(story_id) and acceptance_type in ACCEPTANCE_TYPES:
            coverage.setdefault(story_id, set()).add(acceptance_type)

    for story_id, refs in story_acceptance_refs.items():
        for acceptance_id in sorted(refs):
            if acceptance_id not in acceptance_ids:
                _add(errors, "dangling_reference", f"story:{story_id}.acceptance_ids", f"未找到 Acceptance: {acceptance_id}")
            elif acceptance_owner.get(acceptance_id) != story_id:
                _add(errors, "dangling_reference", f"story:{story_id}.acceptance_ids", f"Acceptance 不属于该 Story: {acceptance_id}")

    for story_id in sorted(approved_story_ids):
        missing = sorted(ACCEPTANCE_TYPES - coverage.get(story_id, set()))
        if missing:
            _add(errors, "missing_coverage", f"story:{story_id}.acceptance", f"缺少 Acceptance 类型: {', '.join(missing)}")

    scope = payload.get("scope")
    if not isinstance(scope, dict):
        _add(errors, "invalid_type", "scope", "必须是对象")
        scope = {}
    _require_list(scope.get("included"), "scope.included", errors)
    _require_list(scope.get("excluded"), "scope.excluded", errors)

    reviews = payload.get("reviews")
    if not isinstance(reviews, dict):
        _add(errors, "invalid_type", "reviews", "必须是对象")
        reviews = {}
    review_statuses: dict[str, object] = {}
    for review_name in ("story", "acceptance"):
        review = reviews.get(review_name)
        base = f"reviews.{review_name}"
        if not isinstance(review, dict):
            _add(errors, "invalid_type", base, "必须是对象")
            review = {}
        review_statuses[review_name] = review.get("status")
        if review.get("status") not in {"draft", "awaiting_confirmation", "approved", "rejected"}:
            _add(errors, "invalid_enum", f"{base}.status", "评审状态无效")
        if review.get("status") == "approved":
            _require_text(review.get("confirmation"), f"{base}.confirmation", errors)
        _require_list(review.get("change_summary"), f"{base}.change_summary", errors)
    if review_statuses.get("acceptance") == "approved" and review_statuses.get("story") != "approved":
        _add(errors, "illegal_transition", "reviews", "Story 未 approved 时 Acceptance 不能 approved")

    delivery = payload.get("delivery")
    if not isinstance(delivery, dict):
        _add(errors, "invalid_type", "delivery", "必须是对象")
        delivery = {}
    _require_text(delivery.get("human_file"), "delivery.human_file", errors)
    _require_text(delivery.get("machine_file"), "delivery.machine_file", errors)

    next_step = payload.get("next_step")
    if not isinstance(next_step, dict):
        _add(errors, "invalid_type", "next_step", "必须是对象")
        next_step = {}
    items = _require_list(next_step.get("items"), "next_step.items", errors)
    routed_counts: dict[str, int] = {}
    all_routes: list[str] = []
    for index, item in enumerate(items):
        base = f"next_step.items[{index}]"
        if not isinstance(item, dict):
            _add(errors, "invalid_type", base, "路由项必须是对象")
            continue
        route = item.get("route")
        all_routes.append(str(route))
        if route not in ROUTES:
            _add(errors, "invalid_enum", f"{base}.route", "下游路由无效")
        for key in ("reason", "capability", "target_id", "suggested_path"):
            _require_text(item.get(key), f"{base}.{key}", errors)
        route_story_ids = _require_list(item.get("story_ids"), f"{base}.story_ids", errors)
        route_acceptance_ids = _require_list(item.get("required_acceptance_ids"), f"{base}.required_acceptance_ids", errors)
        if route == "direct_spec" and len(route_story_ids) != 1:
            _add(errors, "illegal_transition", f"{base}.story_ids", "direct_spec 必须且只能引用一条 Story")
        item_story_set = {story_id for story_id in route_story_ids if _is_text(story_id)}
        for position, story_id in enumerate(route_story_ids):
            if not _is_text(story_id) or story_id not in approved_story_ids:
                _add(errors, "dangling_reference", f"{base}.story_ids[{position}]", "必须引用 approved Story")
                continue
            routed_counts[story_id] = routed_counts.get(story_id, 0) + 1
        for position, acceptance_id in enumerate(route_acceptance_ids):
            if not _is_text(acceptance_id) or acceptance_id not in acceptance_ids:
                _add(errors, "dangling_reference", f"{base}.required_acceptance_ids[{position}]", "未引用现有 Acceptance")
            elif acceptance_owner.get(acceptance_id) not in item_story_set:
                _add(errors, "dangling_reference", f"{base}.required_acceptance_ids[{position}]", "Acceptance 不属于本路由 Story")

    for story_id in sorted(approved_story_ids):
        count = routed_counts.get(story_id, 0)
        if count == 0:
            _add(errors, "missing_route", f"story:{story_id}.next_step", "approved Story 必须进入一个下游路由")
        elif count > 1:
            _add(errors, "duplicate_route", f"story:{story_id}.next_step", "approved Story 只能进入一个下游路由")

    if status == "ready_for_spec":
        if review_statuses.get("story") != "approved" or review_statuses.get("acceptance") != "approved":
            _add(errors, "illegal_transition", "status", "Story 和 Acceptance 均确认后才能 ready_for_spec")
        if any(not invest_pass.get(story_id, False) for story_id in approved_story_ids):
            _add(errors, "illegal_transition", "status", "所有 approved Story 的 INVEST 均通过后才能 ready_for_spec")
        if any(route != "direct_spec" for route in all_routes):
            _add(errors, "illegal_transition", "status", "ready_for_spec 只能使用 direct_spec 路由")

    return errors


def validate_story_card(payload: object) -> list[dict[str, str]]:
    """按 schema 版本分发校验；空列表表示 StoryCard 有效。"""

    if not isinstance(payload, dict):
        return [{"code": "invalid_type", "path": "$", "message": "顶层必须是对象"}]
    version = payload.get("schema_version")
    if version == "aef-story-card/v1":
        return _validate_v1(payload)
    if version == "aef-story-card/v2":
        return _validate_v2(payload)
    return [
        {
            "code": "unsupported_schema",
            "path": "schema_version",
            "message": "只支持 aef-story-card/v1 或 aef-story-card/v2",
        }
    ]


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
