"""持续维护包纯函数：追加修订与审批，不覆盖文件，不执行外部操作。"""
from copy import deepcopy
import re

from story_workspace_validation import (
    SCHEMA, current, decision, positive, require_valid, text, validate_workspace,
)
from validate_story_card import validate_story_card


def create_workspace(package_id, context=None):
    """建立独立包；允许先收集背景再逐条增加对象。"""
    return require_valid({"schema_version": SCHEMA, "package_id": package_id,
                          "context": deepcopy(context or {}), "objects": []})


def _object(data, ident):
    """按稳定 ID 定位对象。"""
    for obj in data["objects"]:
        if obj["id"] == ident:
            return obj
    raise ValueError("未知对象: " + str(ident))


def _finish(new, old):
    """确保操作保持历史，不就地修改调用者数据。"""
    errors = validate_workspace(new, old)
    if errors:
        raise ValueError("; ".join(errors))
    return new


def add_object(data, kind, ident, content, reason):
    """新增编号，退役对象仍占用原编号。"""
    require_valid(data)
    if any(o["id"] == ident for o in data["objects"]):
        raise ValueError("编号已存在，不能复用")
    new = deepcopy(data)
    new["objects"].append({"id": ident, "kind": kind,
                           "versions": [{"revision": 1, "content": deepcopy(content), "reason": reason}],
                           "reviews": []})
    return _finish(new, data)


def revise_object(data, ident, expected, content, reason):
    """乐观并发检查后追加内容，旧审批只适用于旧修订。"""
    require_valid(data)
    new = deepcopy(data)
    obj = _object(new, ident)
    if not positive(expected) or current(obj)["revision"] != expected:
        raise ValueError("基线修订已过期，请重新读取")
    if content == current(obj)["content"]:
        raise ValueError("没有内容变化，不增加修订")
    obj["versions"].append({"revision": expected + 1, "content": deepcopy(content), "reason": reason})
    return _finish(new, data)


def review_object(data, ident, expected, outcome, actor, ref):
    """记录宿主提供的实际人工决定；不能验证其真实性或代用户决定。"""
    require_valid(data)
    new = deepcopy(data)
    obj = _object(new, ident)
    if not positive(expected) or current(obj)["revision"] != expected:
        raise ValueError("不能批准过期修订")
    content = current(obj)["content"]
    if outcome == "approved" and content.get("lifecycle") == "retired":
        raise ValueError("退役内容不能批准就绪")
    if obj["kind"] == "acceptance" and outcome == "approved":
        story = _object(new, content["story_id"])
        if current(story)["revision"] != content["story_revision"] or decision(story) != "approved":
            raise ValueError("先确认 AC 所绑定的当前 Story 修订")
        if current(story)["content"].get("lifecycle") == "retired":
            raise ValueError("不能批准退役故事的验收")
    obj["reviews"].append({"revision": expected, "decision": outcome, "actor": actor, "ref": ref})
    return _finish(new, data)


def next_id(data, kind):
    """在包内建议未用编号；多包项目仍须由宿主扫描项目级重复。"""
    require_valid(data)
    prefixes = {"epic": "EP", "story": "US", "acceptance": "AC"}
    if kind not in prefixes:
        raise ValueError("未知对象类型")
    prefix = prefixes[kind]
    used = {o["id"] for o in data["objects"]}
    numbers = [int(m.group(1)) for ident in used if (m := re.fullmatch(prefix + r"-(\d+)", ident))]
    number = max(numbers, default=0) + 1
    while f"{prefix}-{number:03d}" in used:
        number += 1
    return f"{prefix}-{number:03d}"


def import_v2(card):
    """读取旧 v2 并保留原卡快照；新对象审批不伪造迁移授权。"""
    if not isinstance(card, dict) or card.get("schema_version") != "aef-story-card/v2":
        raise ValueError("只导入已通过原验证器的 v2；v1 继续使用原工具")
    try:
        errors = validate_story_card(card)
    except (TypeError, KeyError, AttributeError) as error:
        raise ValueError("旧卡包含损坏字段类型") from error
    if errors:
        raise ValueError("旧卡未通过验证: " + str(errors))
    data = create_workspace(card["package_id"], {"source": card["source"], "scope": card["scope"]})
    epic = card["epic"]
    data = add_object(data, "epic", epic["epic_id"],
                      {"title": epic["title"], "outcome": epic.get("outcome") or epic["title"]}, "导入已有 Epic")
    for story in card["stories"]:
        content = {k: deepcopy(v) for k, v in story.items() if k not in ("story_id", "status", "acceptance_ids")}
        content["epic_id"] = epic["epic_id"]
        content["selection"] = story["status"]
        data = add_object(data, "story", story["story_id"], content, "导入已有 Story；新模式待确认")
    for ac in card["acceptance"]:
        content = {k: v for k, v in ac.items() if k != "acceptance_id"}
        content["story_revision"] = 1
        data = add_object(data, "acceptance", ac["acceptance_id"], content, "导入已有验收；保留原文")
    data["origin"] = {"schema_version": card["schema_version"], "card": deepcopy(card)}
    return require_valid(data)
