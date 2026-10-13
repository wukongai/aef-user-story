"""只输出固定版本的引用，后续迭代无需复制故事正文。"""
from copy import deepcopy
from story_workspace_validation import current, positive, require_valid
from story_library_render import card_path


def make_reference(data, story_id):
    """固定当前 Story 与全部相关 AC 的版本，引用不代表批准实施。"""
    require_valid(data)
    story = next((o for o in data["objects"] if o["kind"] == "story" and o["id"] == story_id), None)
    if not story:
        raise ValueError("未知故事")
    acs = sorted((o for o in data["objects"] if o["kind"] == "acceptance" and current(o)["content"]["story_id"] == story_id and current(o)["content"].get("lifecycle") != "retired"), key=lambda o: o["id"])
    reference = {"package_id": data["package_id"], "story_id": story_id,
            "story_revision": current(story)["revision"],
            "acceptance_refs": [{"id": o["id"], "revision": current(o)["revision"]} for o in acs],
            "card_path": card_path(story_id)}
    resolve_reference(data, reference)
    return reference


def resolve_reference(data, reference):
    """回读指定历史版本；当前版改变只报告差异，不改引用。"""
    require_valid(data)
    if not isinstance(reference, dict) or reference.get("package_id") != data["package_id"]:
        raise ValueError("引用不属于当前故事库")
    objects = {o["id"]: o for o in data["objects"]}
    ident, revision = reference.get("story_id"), reference.get("story_revision")
    story = objects.get(ident) if isinstance(ident, str) else None
    if not story or story["kind"] != "story" or not positive(revision) or revision > len(story["versions"]):
        raise ValueError("故事引用或修订不存在")
    if reference.get("card_path") != card_path(ident):
        raise ValueError("卡片路径与稳定编号不符")
    refs = reference.get("acceptance_refs")
    if not isinstance(refs, list):
        raise ValueError("缺少验收修订引用")
    ac_versions, seen = [], set()
    outdated = revision != current(story)["revision"]
    for ref in refs:
        if not isinstance(ref, dict):
            raise ValueError("验收引用格式错误")
        ac_id, ac_revision = ref.get("id"), ref.get("revision")
        ac = objects.get(ac_id) if isinstance(ac_id, str) else None
        if not ac or ac["kind"] != "acceptance" or ac_id in seen or not positive(ac_revision) or ac_revision > len(ac["versions"]):
            raise ValueError("验收引用重复或不存在")
        version = ac["versions"][ac_revision - 1]
        if version["content"]["story_id"] != ident or version["content"]["story_revision"] != revision:
            raise ValueError("验收绑定与引用的故事修订不符，需复审")
        seen.add(ac_id)
        ac_versions.append(deepcopy(version))
        outdated = outdated or ac_revision != current(ac)["revision"]
    current_ids = {o["id"] for o in data["objects"] if o["kind"] == "acceptance" and current(o)["content"]["story_id"] == ident and current(o)["content"].get("lifecycle") != "retired"}
    outdated = outdated or seen != current_ids
    return {"story": deepcopy(story["versions"][revision - 1]), "acceptance": ac_versions,
            "outdated": outdated, "reference": deepcopy(reference)}
