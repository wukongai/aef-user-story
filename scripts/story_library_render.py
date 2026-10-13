"""独立故事卡与按 Epic 分组的总索引；不生成迭代正文。"""
import hashlib
import re
from urllib.parse import quote

from story_workspace_validation import current, decision, readiness, require_valid
from story_workspace_render import STATES


def stem(ident):
    """常见编号保持可读；其他编号映射为稳定安全文件名。"""
    if re.fullmatch(r"US-[0-9]{1,100}", ident):
        return ident
    return "story-" + hashlib.sha256(ident.encode("utf-8")).hexdigest()


def card_path(ident):
    """只返回库内相对路径，不把任意旧ID当文件路径。"""
    return "stories/" + stem(ident) + ".md"


def escape(value):
    """使索引单元格中的标题保持一行，防止表格和链接结构破坏。"""
    return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", " ").replace("|", "&#124;").replace("[", "&#91;").replace("]", "&#93;")


def render_index(data):
    """索引仅记录归类、标题、版本和状态，不复制故事正文。"""
    require_valid(data)
    epics = sorted((o for o in data["objects"] if o["kind"] == "epic"), key=lambda o: o["id"])
    stories = sorted((o for o in data["objects"] if o["kind"] == "story"), key=lambda o: o["id"])
    lines = ["# 用户故事库 " + escape(data["package_id"]), "",
             "> 按史诗故事查看独立卡片；迭代只引用故事与验收修订，不复制正文。", ""]
    for epic in epics + [None]:
        ident = epic["id"] if epic else None
        group = [o for o in stories if current(o)["content"].get("epic_id") == ident]
        if epic:
            v = current(epic)
            lines += ["## " + escape(ident) + "@r" + str(v["revision"]) + " · " + escape(v["content"]["title"]),
                      "", escape(v["content"]["outcome"]), ""]
        else:
            lines += ["## 未归类", ""]
        lines += ["| 故事 | 标题 | 故事确认 | 验收修订 | 结构就绪 | 状态 |",
                  "|---|---|---|---|---|---|"]
        for story in group:
            version = current(story)
            acs = sorted((o for o in data["objects"] if o["kind"] == "acceptance" and current(o)["content"]["story_id"] == story["id"]), key=lambda o: o["id"])
            ac_summary = "、".join(escape(o["id"]) + "@r" + str(current(o)["revision"]) + " " + STATES[decision(o)] for o in acs) or "待细化"
            link = "[" + escape(story["id"]) + "@r" + str(version["revision"]) + "](" + quote(card_path(story["id"]), safe="/.-") + ")"
            lines.append("| " + " | ".join((link, escape(version["content"]["title"]), STATES[decision(story)], ac_summary,
                                             "是" if readiness(data, story["id"])["ready"] else "否",
                                             "已退役" if version["content"].get("lifecycle") == "retired" else "有效")) + " |")
        if not group:
            lines.append("| — | 暂无故事 | — | — | — | — |")
        lines.append("")
    return "\n".join(lines)


def prose(value):
    """把补充约束转换为可读文字，不向卡片直接输出JSON。"""
    if isinstance(value, dict):
        return "；".join(str(k) + "：" + prose(v) for k, v in value.items())
    if isinstance(value, list):
        return "；".join(prose(v) for v in value)
    return str(value)


def render_card(data, story_id):
    """日常卡片只展示故事和编号验收；管理记录留在独立数据中。"""
    require_valid(data)
    story = next((o for o in data["objects"] if o["id"] == story_id and o["kind"] == "story"), None)
    if not story:
        raise ValueError("未知故事")
    content = current(story)["content"]
    story_sentence = content["statement"]
    lines = ["# " + escape(story_id) + "｜" + escape(content["title"]), "", story_sentence,
             "", "## 验收条件", ""]
    acs = sorted((o for o in data["objects"] if o["kind"] == "acceptance"
                  and current(o)["content"]["story_id"] == story_id
                  and current(o)["content"].get("lifecycle") != "retired"),
                 key=lambda o: ({"success": 0, "boundary": 1, "failure": 2}[current(o)["content"]["type"]], o["id"]))
    for number, ac in enumerate(acs, 1):
        item = current(ac)["content"]
        sentence = item["given"].rstrip("。；，") + "时，" + item["when"].rstrip("。；，") + "，" + item["then"].rstrip("。；，") + "。"
        lines.append(str(number) + ". " + sentence)
    if not acs:
        lines.append("暂未补充。")
    notes = []
    for obj in [story] + acs:
        detail = current(obj)["content"]
        for key, label in (("rules", "业务规则"), ("constraints", "约束"), ("risks", "风险与待决事项")):
            if detail.get(key):
                notes.append("- " + label + "：" + prose(detail[key]))
    if notes:
        lines += ["", "## 补充说明", "", *notes]
    if content.get("lifecycle") == "retired":
        lines += ["", "> 此故事已退役，保留供历史查询。"]
    lines += ["", "[返回故事索引](../index.md)"]
    return "\n".join(lines) + "\n"
