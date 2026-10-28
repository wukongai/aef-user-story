"""评审归属与原生引用适配；故事修订和验收绑定仍由原库负责。"""

import html
import json
import re
from pathlib import Path

from story_library_references import resolve_reference
from story_library_store import META, read_library, safe_file


def rendered_anchors(text):
    """解析常用ATX/Setext标题及a锚点，排除注释、代码和HTML块。"""
    visible, fence, html_block, hidden_end = [], None, False, None
    code_span = re.compile(r"(?<!`)(`+)(?!`)(.*?)\1(?!`)")
    for line in text.splitlines():
        # 已进入真实HTML块时，内部的围栏或反引号只是不透明正文。
        if hidden_end:
            if re.search(hidden_end, line, flags=re.IGNORECASE):
                hidden_end = None
            visible.append("")
            continue
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
            visible.append("")
            continue
        if marker and not (marker[1][0] == "`" and "`" in marker[2]):
            fence = marker[1]
            visible.append("")
            continue
        if html_block:
            html_block = bool(line.strip())
            visible.append("")
            continue
        if line.startswith(("    ", "\t")):
            visible.append("")
            continue
        # 先保护代码字面量，避免把其中未闭合的HTML标记解释成正文起点。
        line = code_span.sub(lambda match: match[0].replace("<", "\ue000").replace(">", "\ue001"), line)
        opaque = re.match(r"^ {0,3}<(pre|script|style|textarea)(?:\s|>|$)", line, flags=re.IGNORECASE)
        if re.match(r"^ {0,3}<!--", line) or opaque:
            ending = r"</" + opaque[1] + r"\s*>" if opaque else r"-->"
            if not re.search(ending, line, flags=re.IGNORECASE):
                hidden_end = ending
            visible.append("")
            continue
        if re.match(r"^ {0,3}</?(?!a(?:\s|>))[A-Za-z][^>]*>", line):
            html_block = True
            visible.append("")
            continue
        line = re.sub(r"<!--.*?-->", "", line)
        if "<!--" in line:
            line = line.split("<!--", 1)[0]
            hidden_end = r"-->"
        visible.append(line)
    plain = "\n".join(visible)
    inline_free = code_span.sub("", plain)
    anchors = re.findall(r'<a\s+id="([^"]+)"', inline_free)
    headings, counts = [], {}
    for index, line in enumerate(visible):
        atx = re.match(r"^ {0,3}#{1,6}[ \t]+(.+)$", line)
        if atx:
            headings.append(re.sub(r"[ \t]+#+[ \t]*$", "", atx[1]).strip())
        elif index and re.fullmatch(r" {0,3}(?:=+|-+)[ \t]*", line) and visible[index-1].strip() and not re.match(r"^ {0,3}#", visible[index-1]):
            headings.append(visible[index-1].strip())
    for heading in headings:
        heading = re.sub(r"!?\[([^]]*)\]\([^)]*\)", r"\1", heading)
        heading = html.unescape(re.sub(r"<[^>]+>", "", heading)).replace("\ue000", "<").replace("\ue001", ">")
        key = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = counts.get(key, 0)
        counts[key] = count + 1
        anchors.append(key if count == 0 else f"{key}-{count}")
    return anchors


def native_card(data, reference, relative, root, frozen_paths):
    """显式定位冻结原库，复用原解析器验证历史和AC，不创建新业务状态。"""
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError("原生引用缺有效的相对library_root")
    library = root / relative
    if not library.resolve().is_relative_to(root) or any(
            part.is_symlink() for part in (library, *library.parents) if part.is_relative_to(root)):
        raise ValueError("原生故事库路径越界或含符号链接")
    directory = library / ".story-data"
    if directory.is_symlink():
        raise ValueError("原生数据目录不能是符号链接")
    sources = [safe_file(library, META)]
    sources += [safe_file(library, ".story-data/" + path.name)
                for path in sorted(directory.iterdir())] if directory.exists() else []
    if any(str(path.resolve()) not in frozen_paths for path in sources):
        raise ValueError("原生故事库元数据或独立对象数据未冻结")
    resolved = resolve_reference(read_library(library), reference)
    if "reference" in data and any(data.get(key) != resolved[key] for key in ("story", "acceptance")):
        raise ValueError("resolve历史正文与原库解析结果不一致")
    return safe_file(library, reference["card_path"])


def validate_owner(owner, root, frozen_paths):
    """沿固定引用索引解析对象身份、修订与真实卡片章节，不复制业务正文。"""
    if not isinstance(owner, dict):
        return ["归属须为固定对象引用，不能仅指泛文件"]
    package, story, revision = (owner.get(key) for key in ("package_id", "story_id", "story_revision"))
    if not isinstance(package, str) or not package or not isinstance(story, str) or not story:
        return ["归属缺包身份或Story ID"]
    if type(revision) is not int or revision < 1:
        return ["归属缺有效Story修订"]
    reference, anchor = owner.get("index_ref"), owner.get("anchor")
    if not isinstance(reference, str) or not reference or not isinstance(anchor, str) or not anchor:
        return ["归属缺固定引用索引或真实章节"]
    index = (root / reference).resolve()
    if Path(reference).is_absolute() or not index.is_relative_to(root) or str(index) not in frozen_paths:
        return ["归属索引未冻结或越界"]
    try:
        data = json.loads(index.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return ["固定引用索引必须为对象"]
        if "reference" in data and "references" in data:
            return ["固定引用形态有歧义"]
        payload = data.get("reference", data)
        rows = data.get("references", [payload])
        if not isinstance(rows, list):
            return ["固定引用集合无效"]
        matches = [row for row in rows if isinstance(row, dict) and type(row.get("story_revision")) is int and
                   (row.get("package_id"), row.get("story_id"), row.get("story_revision")) == (package, story, revision)]
        namespace = payload.get("package_id") if isinstance(payload, dict) else None
        if len(matches) != 1 or namespace != package:
            return ["归属包/Story/修订不匹配或有歧义"]
        if "library_root" in owner:
            card = native_card(data, matches[0], owner["library_root"], root, frozen_paths).resolve()
        else:
            if "reference" in data:
                return ["原resolve输出需显式提供library_root"]
            card_path, base = matches[0].get("card_path"), data.get("card_path_base", ".")
            if not isinstance(card_path, str) or not isinstance(base, str):
                return ["固定引用缺卡片路径"]
            if Path(card_path).is_absolute() or Path(base).is_absolute():
                return ["固定引用卡片路径须为相对路径"]
            card = (index.parent / base / card_path).resolve()
        if not card.is_relative_to(root) or str(card) not in frozen_paths or not card.is_file():
            return ["归属卡片未冻结、不存在或越界"]
        text = card.read_text(encoding="utf-8")
        anchors = rendered_anchors(text)
        if anchors.count(anchor) != 1:
            return ["归属章节不存在或有歧义"]
    except (OSError, ValueError, TypeError, KeyError) as error:
        return ["固定归属引用无法解析：" + str(error)]
    return []
