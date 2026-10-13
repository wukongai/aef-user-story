#!/usr/bin/env python3
"""只读用户故事持续维护 CLI：所有候选写到 stdout，由宿主按授权保存。"""
import argparse
import json
from pathlib import Path

from story_workspace_model import (
    add_object, create_workspace, import_v2, next_id, revise_object, review_object,
)
from story_workspace_validation import (
    current, decision, readiness, require_valid, validate_workspace,
)


from story_workspace_render import render


def _read(path):
    """严格读取 JSON 数据，不执行文件内容。"""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv=None):
    """提供独立调用入口，退出 1 为内容错误，2 为读取或用法错误。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("init", "import-v2", "validate", "add", "revise", "review", "next-id", "show", "render", "status"))
    parser.add_argument("path", nargs="?")
    parser.add_argument("--package")
    parser.add_argument("--context")
    parser.add_argument("--previous")
    parser.add_argument("--kind", choices=("epic", "story", "acceptance"))
    parser.add_argument("--id")
    parser.add_argument("--content")
    parser.add_argument("--reason")
    parser.add_argument("--expect", type=int)
    parser.add_argument("--revision", type=int)
    parser.add_argument("--decision", choices=("approved", "rejected"))
    parser.add_argument("--actor")
    parser.add_argument("--ref")
    args = parser.parse_args(argv)
    try:
        if args.command == "init":
            result = create_workspace(args.package, _read(args.context) if args.context else {})
        else:
            if not args.path:
                parser.error("此命令需要 path")
            data = _read(args.path)
            if args.command == "validate":
                errors = validate_workspace(data, _read(args.previous) if args.previous else None)
                print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False))
                return 1 if errors else 0
            if args.command == "import-v2":
                result = import_v2(data)
            else:
                require_valid(data)
                if args.command in ("add", "revise"):
                    if not args.content:
                        parser.error("add/revise 需要 --content")
                    content = _read(args.content)
                    result = (add_object(data, args.kind, args.id, content, args.reason) if args.command == "add"
                              else revise_object(data, args.id, args.expect, content, args.reason))
                elif args.command == "review":
                    result = review_object(data, args.id, args.expect, args.decision, args.actor, args.ref)
                elif args.command == "next-id":
                    result = {"next_id": next_id(data, args.kind)}
                elif args.command == "status":
                    result = readiness(data, args.id)
                elif args.command == "show":
                    obj = next((o for o in data["objects"] if o["id"] == args.id), None)
                    if not obj:
                        raise ValueError("未知对象")
                    result = next((v for v in obj["versions"] if v["revision"] == args.revision), None) if args.revision is not None else current(obj)
                    if result is None:
                        raise ValueError("未知修订")
                else:
                    print(render(data), end="")
                    return 0
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        print(json.dumps({"valid": False, "errors": [str(error)]}, ensure_ascii=False))
        return 2
    except ValueError as error:
        print(json.dumps({"valid": False, "errors": [str(error)]}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
