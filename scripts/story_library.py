#!/usr/bin/env python3
"""故事库只读 CLI：独立卡片、总索引和带基线摘要的局部保存计划。"""
import argparse
import hashlib
import json
from pathlib import Path

from story_workspace_model import add_object, create_workspace, revise_object, review_object, next_id
from story_workspace_validation import current, require_valid, validate_workspace
from story_library_store import (
    export_library, read_library, validate_library, managed_snapshot, json_text,
)
from story_library_references import make_reference, resolve_reference

PLAN_SCHEMA = "aef-story-library-plan/v1"


def sha(text):
    """内容摘要用于保存前检查，不作为审批凭证。"""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def make_plan(before, after):
    """只列真正变化的文件；此接口不安排删除。"""
    if set(before) - set(after):
        raise ValueError("计划会移除已有故事数据，必须保留历史或另行迁移")
    return {"schema_version": PLAN_SCHEMA,
            "base_hashes": {p: sha(v) for p, v in before.items()},
            "files": [{"path": p, "before_sha256": sha(before[p]) if p in before else None,
                       "content": after[p]} for p in sorted(after) if before.get(p) != after[p]]}


def plan_change(root, operation, ident, *, kind=None, content=None, expected=None,
                reason=None, outcome=None, actor=None, ref=None):
    """只改变指定对象，并输出该故事卡及索引的最小文件差异。"""
    errors = validate_library(root)
    if errors:
        raise ValueError("; ".join(errors))
    before = managed_snapshot(root)
    data = read_library(root)
    if operation == "add":
        new = add_object(data, kind, ident, content, reason)
    elif operation == "revise":
        obj = next((o for o in data["objects"] if o["id"] == ident), None)
        if not obj:
            raise ValueError("未知对象")
        if obj["kind"] == "acceptance" and isinstance(content, dict) and content.get("story_id") != current(obj)["content"]["story_id"]:
            raise ValueError("验收不能跨故事移动；请新增验收并明确退役旧项")
        new = revise_object(data, ident, expected, content, reason)
    elif operation == "review":
        new = review_object(data, ident, expected, outcome, actor, ref)
    else:
        raise ValueError("未知操作")
    return make_plan(before, export_library(new))


def check_plan(root, plan):
    """只核对路径与可信磁盘基线；候选语义须在保存后完整校验。"""
    try:
        if not isinstance(plan, dict) or plan.get("schema_version") != PLAN_SCHEMA:
            return ["变更计划格式错误"]
        bases, changes = plan.get("base_hashes"), plan.get("files")
        if not isinstance(bases, dict) or not isinstance(changes, list):
            return ["变更计划缺少基线或文件数组"]
        root = Path(root)
        if root.is_symlink():
            return ["故事库目标不得为符号链接"]
        if not bases:
            if root.exists() and (not root.is_dir() or any(root.iterdir())):
                return ["新库目标非空，不允许覆盖迁移"]
            actual = {}
        else:
            actual = managed_snapshot(root)
        if {p: sha(v) for p, v in actual.items()} != bases:
            return ["磁盘基线已变化，重新读取并生成计划"]
        seen = set()
        for item in changes:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str) or not isinstance(item.get("content"), str):
                return ["变更文件格式错误"]
            path = item["path"]
            parts = Path(path).parts
            allowed = path in (".story-library.json", "index.md") or (
                len(parts) == 2 and parts[0] in (".story-data", "stories")
                and Path(path).suffix == (".json" if parts[0] == ".story-data" else ".md"))
            if not allowed or Path(path).is_absolute() or ".." in parts or path in seen or Path(path).as_posix() != path or "\\" in path:
                return ["变更路径无效或重复"]
            seen.add(path)
            expected_hash = sha(actual[path]) if path in actual else None
            if item.get("before_sha256") != expected_hash:
                return ["文件基线摘要不匹配"]
        return []
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        return ["基线校验失败: " + str(error)]


def read_json(path):
    """命令参数文件仅作为数据解析。"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv=None):
    """输出候选或查询结果；始终不写故事库文件。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "migrate", "validate", "change", "reference", "resolve", "next-id", "check-plan"))
    parser.add_argument("path", nargs="?")
    parser.add_argument("--package")
    parser.add_argument("--context")
    parser.add_argument("--previous")
    parser.add_argument("--operation", choices=("add", "revise", "review"))
    parser.add_argument("--kind", choices=("epic", "story", "acceptance"))
    parser.add_argument("--id")
    parser.add_argument("--content")
    parser.add_argument("--expect", type=int)
    parser.add_argument("--reason")
    parser.add_argument("--decision", choices=("approved", "rejected"))
    parser.add_argument("--actor")
    parser.add_argument("--ref")
    parser.add_argument("--reference")
    parser.add_argument("--plan")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            data = create_workspace(args.package, read_json(args.context) if args.context else {})
            result = make_plan({}, export_library(data))
        else:
            if not args.path:
                parser.error("此命令需要故事库目录或迁移输入路径")
            if args.command == "migrate":
                result = make_plan({}, export_library(read_json(args.path)))
            elif args.command == "validate":
                errors = validate_library(args.path, read_library(args.previous) if args.previous else None)
                print(json_text({"valid": not errors, "errors": errors}), end="")
                return 1 if errors else 0
            elif args.command == "check-plan":
                if not args.plan:
                    parser.error("check-plan 需要 --plan")
                errors = check_plan(args.path, read_json(args.plan))
                print(json_text({"valid": not errors, "errors": errors}), end="")
                return 1 if errors else 0
            elif args.command == "change":
                result = plan_change(args.path, args.operation, args.id, kind=args.kind,
                                     content=read_json(args.content) if args.content else None,
                                     expected=args.expect, reason=args.reason, outcome=args.decision,
                                     actor=args.actor, ref=args.ref)
            else:
                errors = validate_library(args.path)
                if errors:
                    raise ValueError("; ".join(errors))
                data = read_library(args.path)
                if args.command == "reference":
                    result = make_reference(data, args.id)
                    resolve_reference(data, result)
                elif args.command == "resolve":
                    if not args.reference:
                        parser.error("resolve 需要 --reference")
                    result = resolve_reference(data, read_json(args.reference))
                else:
                    result = {"next_id": next_id(data, args.kind)}
        print(json_text(result), end="")
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(json_text({"valid": False, "errors": [str(error)]}), end="")
        return 2
    except (ValueError, TypeError, KeyError) as error:
        print(json_text({"valid": False, "errors": [str(error)]}), end="")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
