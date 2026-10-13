"""将持续维护包渲染为供用户审阅的中文故事卡片。"""
import json
from story_workspace_validation import current, decision, readiness, require_valid

LABELS = {"actor": "用户", "scenario": "场景", "goal": "目标", "value": "价值",
          "statement": "用户故事", "epic_id": "所属 Epic", "outcome": "预期结果",
          "story_id": "所属故事", "story_revision": "绑定故事修订", "given": "假如",
          "when": "当", "then": "那么", "derived_from": "来源对象", "rules": "业务规则",
          "risks": "风险与待决事项", "source_refs": "证据", "selection": "导入时状态"}
STATES = {"draft": "待确认", "approved": "已确认", "rejected": "未通过"}


def display(value):
    """复杂附加信息保持可见，避免渲染时丢失原始约束。"""
    return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)


def render(data):
    """当前正文从 JSON 投影；历史快照仍可通过 show 读取。"""
    require_valid(data)
    lines = ["# 用户故事需求包 " + data["package_id"], "",
             "> 此正文由持续维护包生成；修改时更新源包后重新生成，避免两份正文不一致。", "",
             "## 背景与来源", ""]
    context_labels = {"source": "需求来源", "scope": "范围", "facts": "事实", "assumptions": "假设",
                      "unknowns": "未知", "constraints": "约束", "non_goals": "非目标"}
    for key, value in data["context"].items():
        lines.append("- " + context_labels.get(key, key) + "：" + display(value))
    for kind, heading in (("epic", "史诗故事"), ("story", "用户故事"), ("acceptance", "验收条件")):
        lines += ["", "## " + heading]
        for obj in data["objects"]:
            if obj["kind"] != kind:
                continue
            version, content = current(obj), current(obj)["content"]
            lines += ["", "### " + obj["id"] + "@r" + str(version["revision"]) + " " + content.get("title", ""),
                      "", "审阅：" + STATES[decision(obj)] + "；内容状态：" +
                      ("已退役" if content.get("lifecycle") == "retired" else "当前有效"), ""]
            for key, value in content.items():
                if key in ("title", "invest_review", "lifecycle"):
                    continue
                if key == "type":
                    value = {"success": "成功路径", "failure": "失败与恢复", "boundary": "边界条件"}[value]
                lines.append("- " + LABELS.get(key, "类型" if key == "type" else key) + "：" + display(value))
            if kind == "story":
                lines += ["", "INVEST 检查：", ""]
                for key, item in content.get("invest_review", {}).items():
                    lines.append("- " + key + "：" + item["status"] + "；" + item["reason"])
                result = readiness(data, obj["id"])
                lines += ["", "**结构就绪：" + ("是" if result["ready"] else "否") + "**"]
                for key, label in (("missing_types", "缺少已确认验收类型"), ("stale_acceptance", "需随故事重审"),
                                   ("pending_acceptance", "待确认验收")):
                    if result[key]:
                        lines.append("- " + label + "：" + "、".join(result[key]))
            lines += ["", "修订记录："]
            lines += ["- r" + str(v["revision"]) + "：" + v["reason"] for v in obj["versions"]]
            for review in obj["reviews"]:
                lines.append("- r" + str(review["revision"]) + " " + STATES[review["decision"]] +
                             "；确认人：" + review["actor"] + "；依据：" + review["ref"])
    return "\n".join(lines) + "\n"
