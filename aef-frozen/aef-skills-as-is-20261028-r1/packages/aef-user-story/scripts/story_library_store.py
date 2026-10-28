"""独立故事库序列化与只读加载；沿用原对象修订和审批语义。"""
from copy import deepcopy
import json
from pathlib import Path

from story_workspace_validation import SCHEMA, current, require_valid, validate_workspace
from story_library_render import card_path, render_card, render_index, stem

LIBRARY_SCHEMA = "aef-story-library/v1"
CARD_SCHEMA = "aef-story-card-file/v1"
META = ".story-library.json"


def json_text(value):
    """稳定编码，不加入时间戳以保持未改卡片字节一致。"""
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def ensure_fixed_owners(data):
    """一张独立卡保存本故事所有 AC 历史，AC 不跨卡移动。"""
    for obj in data["objects"]:
        if obj["kind"] == "acceptance":
            if len({v["content"]["story_id"] for v in obj["versions"]}) != 1:
                raise ValueError("验收归属曾跨故事变化，需先人工整理，不自动搬移卡片")


def export_library(data):
    """无损拆分旧持续维护包，不修改原数据或磁盘。"""
    require_valid(data)
    ensure_fixed_owners(data)
    metadata = {"schema_version": LIBRARY_SCHEMA,
                "workspace": {k: deepcopy(v) for k, v in data.items() if k not in ("schema_version", "objects")},
                "epics": [deepcopy(o) for o in data["objects"] if o["kind"] == "epic"]}
    files = {META: json_text(metadata), "index.md": render_index(data)}
    for story in sorted((o for o in data["objects"] if o["kind"] == "story"), key=lambda o: o["id"]):
        acs = [deepcopy(o) for o in data["objects"] if o["kind"] == "acceptance" and current(o)["content"]["story_id"] == story["id"]]
        packet = {"schema_version": CARD_SCHEMA, "package_id": data["package_id"],
                  "story": deepcopy(story), "acceptance": acs}
        files[".story-data/" + stem(story["id"]) + ".json"] = json_text(packet)
        files[card_path(story["id"])] = render_card(data, story["id"])
    return files


def safe_file(root, relative):
    """只读取库内普通文件，拒绝符号链接及路径逃逸。"""
    root = Path(root)
    path = root / relative
    if root.is_symlink():
        raise ValueError("故事库根不能是符号链接")
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError("路径必须位于故事库内")
    for part in [path, *path.parents]:
        if part == root.parent:
            break
        if part.is_symlink():
            raise ValueError("故事库文件和目录不能是符号链接")
    if not path.is_file():
        raise ValueError("缺少普通文件: " + relative)
    return path


def read_json(root, relative):
    """读取对象数据，解析失败不返回空包。"""
    return json.loads(safe_file(root, relative).read_text(encoding="utf-8"))


def read_library(root):
    """读取各独立卡，在内存组合后复用既有完整校验；不保存大文档。"""
    root = Path(root)
    meta = read_json(root, META)
    if not isinstance(meta, dict) or meta.get("schema_version") != LIBRARY_SCHEMA:
        raise ValueError("故事库元数据无效")
    context = meta.get("workspace")
    epics = meta.get("epics")
    if not isinstance(context, dict) or "objects" in context or "schema_version" in context or not isinstance(epics, list):
        raise ValueError("故事库背景或 Epic 集合无效")
    if any(not isinstance(o, dict) or o.get("kind") != "epic" for o in epics):
        raise ValueError("元数据只能存 Epic 对象")
    data = {"schema_version": SCHEMA, **deepcopy(context), "objects": deepcopy(epics)}
    directory = root / ".story-data"
    if directory.is_symlink():
        raise ValueError("独立数据目录不能是符号链接")
    if directory.exists() and not directory.is_dir():
        raise ValueError("独立数据位置不是目录")
    for path in sorted(directory.iterdir()) if directory.exists() else []:
        relative = ".story-data/" + path.name
        if path.suffix != ".json":
            raise ValueError("数据目录含未知文件: " + relative)
        packet = read_json(root, relative)
        if not isinstance(packet, dict) or packet.get("schema_version") != CARD_SCHEMA or packet.get("package_id") != data.get("package_id"):
            raise ValueError("独立故事数据合同或包身份错误")
        story, acs = packet.get("story"), packet.get("acceptance")
        if not isinstance(story, dict) or story.get("kind") != "story" or not isinstance(story.get("id"), str) or not isinstance(acs, list):
            raise ValueError("独立卡缺少 Story 或验收数组")
        if path.name != stem(story["id"]) + ".json":
            raise ValueError("文件名与稳定故事ID不符")
        for ac in acs:
            if not isinstance(ac, dict) or ac.get("kind") != "acceptance":
                raise ValueError("独立卡包含非验收对象")
            versions = ac.get("versions")
            if not isinstance(versions, list) or any(not isinstance(v, dict) or not isinstance(v.get("content"), dict) or v["content"].get("story_id") != story["id"] for v in versions):
                raise ValueError("验收必须始终属于当前卡片")
        data["objects"] += [story, *acs]
    require_valid(data)
    ensure_fixed_owners(data)
    return data


def managed_snapshot(root):
    """采集受管理区域；未知卡片也纳入漂移检查而不静默清理。"""
    root = Path(root)
    snapshot = {}
    for relative in (META, "index.md"):
        snapshot[relative] = safe_file(root, relative).read_text(encoding="utf-8")
    for folder in (".story-data", "stories"):
        directory = root / folder
        if directory.is_symlink():
            raise ValueError("库目录不能是符号链接")
        if directory.exists():
            if not directory.is_dir():
                raise ValueError("库目录格式错误")
            for path in sorted(directory.iterdir()):
                relative = folder + "/" + path.name
                snapshot[relative] = safe_file(root, relative).read_text(encoding="utf-8")
    return snapshot


def validate_library(root, previous=None):
    """校验卡片/索引与源数据一致及相邻历史；从不自动修复人工差异。"""
    try:
        data = read_library(root)
        errors = validate_workspace(data, previous)
        actual, expected = managed_snapshot(root), export_library(data)
        for path in sorted(set(actual) | set(expected)):
            if actual.get(path) != expected.get(path):
                errors.append("独立卡片或索引与数据不一致: " + path)
        return errors
    except (OSError, UnicodeError, ValueError, TypeError, KeyError) as error:
        return ["故事库读取或校验失败: " + str(error)]
