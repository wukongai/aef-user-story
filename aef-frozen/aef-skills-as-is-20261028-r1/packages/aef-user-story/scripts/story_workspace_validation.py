"""持续维护包的只读结构、引用、历史与就绪校验。"""
from copy import deepcopy
import re

SCHEMA = "aef-story-workspace/v1"
KINDS = {"epic", "story", "acceptance"}
TYPES = {"success", "failure", "boundary"}
INVEST = {"independent", "negotiable", "valuable", "estimable", "small", "testable"}


def text(value):
    """判断非空文本。"""
    return isinstance(value, str) and bool(value.strip())


def positive(value):
    """拒绝布尔值冒充修订号。"""
    return type(value) is int and value > 0


def current(obj):
    """读取最新内容快照。"""
    return obj["versions"][-1]


def decision(obj, revision=None):
    """只读取与指定内容修订匹配的最新决定。"""
    revision = revision or current(obj)["revision"]
    events = [r for r in obj["reviews"] if r["revision"] == revision]
    return events[-1]["decision"] if events else "draft"


def _shape(data):
    """先检查形状，保证后续关联检查不会因损坏输入崩溃。"""
    errors = []
    if not isinstance(data, dict):
        return ["顶层必须是对象"]
    if data.get("schema_version") != SCHEMA or not text(data.get("package_id")):
        errors.append("合同版本或 package_id 无效")
    if not isinstance(data.get("context"), dict):
        errors.append("context 必须是对象")
    objects = data.get("objects")
    if not isinstance(objects, list):
        return errors + ["objects 必须是数组"]
    ids = set()
    for obj in objects:
        if not isinstance(obj, dict):
            errors.append("对象必须是字典")
            continue
        ident = obj.get("id")
        if not text(ident) or any(ord(ch) < 32 for ch in ident):
            errors.append("ID 必须为安全非空编号")
        elif ident in ids:
            errors.append("编号重复: " + ident)
        else:
            ids.add(ident)
        if obj.get("kind") not in ("epic", "story", "acceptance"):
            errors.append("对象类型无效")
        versions = obj.get("versions")
        if not isinstance(versions, list) or not versions:
            errors.append("versions 必须是非空数组")
            continue
        for number, version in enumerate(versions, 1):
            if not isinstance(version, dict):
                errors.append("修订必须是对象")
                continue
            if not positive(version.get("revision")) or version["revision"] != number:
                errors.append("修订必须从 1 连续递增")
            if not isinstance(version.get("content"), dict) or not text(version.get("reason")):
                errors.append("修订必须含 content 与非空 reason")
        reviews = obj.get("reviews")
        if not isinstance(reviews, list):
            errors.append("reviews 必须是数组")
            continue
        for review in reviews:
            if not isinstance(review, dict):
                errors.append("审批必须是对象")
                continue
            if not positive(review.get("revision")) or review["revision"] > len(versions):
                errors.append("审批修订无效")
            if review.get("decision") not in ("approved", "rejected"):
                errors.append("审批决定无效")
            if not text(review.get("actor")) or not text(review.get("ref")):
                errors.append("审批缺少 actor 或真实记录 ref")
    return errors


def _contents(data):
    """检查所有历史内容与对象引用，允许旧 AC 保留旧故事绑定。"""
    errors = []
    objects = {o["id"]: o for o in data["objects"]}
    for obj in objects.values():
        kind = obj["kind"]
        for version in obj["versions"]:
            content = version["content"]
            required = {"epic": ("title", "outcome"),
                        "story": ("title", "actor", "scenario", "goal", "value", "statement"),
                        "acceptance": ("story_id", "type", "given", "when", "then")}[kind]
            if any(not text(content.get(k)) for k in required):
                errors.append(obj["id"] + " 缺少必需内容")
            if "title" in content and not text(content["title"]):
                errors.append(obj["id"] + " title 必须是非空文本")
            if content.get("lifecycle", "active") not in ("active", "retired"):
                errors.append(obj["id"] + " lifecycle 无效")
            if kind == "story":
                epic = content.get("epic_id")
                if epic is not None and (not isinstance(epic, str) or epic not in objects or objects[epic]["kind"] != "epic"):
                    errors.append(obj["id"] + " Epic 引用无效")
                invest = content.get("invest_review", {})
                if not isinstance(invest, dict):
                    errors.append(obj["id"] + " INVEST 必须是对象")
                else:
                    for key, item in invest.items():
                        if key not in INVEST or not isinstance(item, dict) or item.get("status") not in ("pass", "risk", "fail") or not text(item.get("reason")):
                            errors.append(obj["id"] + " INVEST 证据无效")
            if kind == "acceptance":
                story_id, revision = content.get("story_id"), content.get("story_revision")
                story = objects.get(story_id) if isinstance(story_id, str) else None
                if not story or story["kind"] != "story" or not positive(revision) or revision > len(story["versions"]):
                    errors.append(obj["id"] + " Story 修订引用无效")
                if content.get("type") not in ("success", "failure", "boundary"):
                    errors.append(obj["id"] + " 验收类型无效")
            links = content.get("derived_from", [])
            if not isinstance(links, list) or any(not isinstance(x, str) or x == obj["id"] or x not in objects for x in links):
                errors.append(obj["id"] + " 来源关联无效")
        if kind == "acceptance":
            for review in obj["reviews"]:
                if review["decision"] != "approved":
                    continue
                content = obj["versions"][review["revision"] - 1]["content"]
                story = objects.get(content.get("story_id")) if isinstance(content.get("story_id"), str) else None
                if not story or not any(r["decision"] == "approved" and r["revision"] == content.get("story_revision") for r in story["reviews"]):
                    errors.append(obj["id"] + " 验收批准缺少对应 Story 批准")
    return errors


def validate_workspace(data, previous=None):
    """返回错误列表；previous 用于防止既有历史被改写或丢失。"""
    errors = _shape(data)
    if errors:
        return errors
    errors += _contents(data)
    if errors:
        return errors
    if previous is not None:
        if validate_workspace(previous):
            return errors + ["历史基线损坏"]
        for key in ("schema_version", "package_id", "context", "origin"):
            if data.get(key) != previous.get(key):
                errors.append("不得在局部操作中改写包身份或来源: " + key)
        objects = {o["id"]: o for o in data["objects"]}
        for old in previous["objects"]:
            new = objects.get(old["id"])
            if not new or new["kind"] != old["kind"]:
                errors.append("历史对象丢失或类型改变: " + old["id"])
                continue
            for key in ("versions", "reviews"):
                if new[key][:len(old[key])] != old[key]:
                    errors.append("历史被改写: " + old["id"] + "." + key)
        old_objects = {o["id"]: o for o in previous["objects"]}
        for obj in data["objects"]:
            old_count = len(old_objects.get(obj["id"], {}).get("reviews", []))
            for review in obj["reviews"][old_count:]:
                if review["revision"] != current(obj)["revision"]:
                    errors.append("新增审批不能绑定旧修订: " + obj["id"])
                if review["decision"] != "approved":
                    continue
                content = current(obj)["content"]
                if content.get("lifecycle") == "retired":
                    errors.append("不能批准退役内容: " + obj["id"])
                if obj["kind"] == "acceptance":
                    story = objects.get(content.get("story_id"))
                    if not story or current(story)["revision"] != content.get("story_revision") or decision(story) != "approved" or current(story)["content"].get("lifecycle") == "retired":
                        errors.append("新增验收批准必须绑定当前已确认故事: " + obj["id"])
    return errors


def require_valid(data):
    """拒绝损坏包，返回调用者可安全复制的数据。"""
    errors = validate_workspace(data)
    if errors:
        raise ValueError("; ".join(errors))
    return data


def readiness(data, story_id):
    """派生就绪状态；不是用户批准或真实业务价值验证。"""
    require_valid(data)
    objects = {o["id"]: o for o in data["objects"]}
    story = objects.get(story_id)
    if not story or story["kind"] != "story":
        raise ValueError("未找到 Story")
    revision, content = current(story)["revision"], current(story)["content"]
    coverage, stale, pending = set(), [], []
    for obj in objects.values():
        ac = current(obj)["content"]
        if obj["kind"] != "acceptance" or ac["story_id"] != story_id or ac.get("lifecycle") == "retired":
            continue
        if ac["story_revision"] != revision:
            stale.append(obj["id"])
        elif decision(obj) == "approved":
            coverage.add(ac["type"])
        else:
            pending.append(obj["id"])
    invest = content.get("invest_review", {})
    invest_ok = all(invest.get(k, {}).get("status") == "pass" for k in INVEST)
    ready = (decision(story) == "approved" and invest_ok and coverage == TYPES
             and not stale and not pending and content.get("lifecycle") != "retired")
    return {"story_id": story_id, "revision": revision, "ready": ready,
            "story_review": decision(story), "invest_pass": invest_ok,
            "missing_types": sorted(TYPES - coverage),
            "stale_acceptance": stale, "pending_acceptance": pending}
