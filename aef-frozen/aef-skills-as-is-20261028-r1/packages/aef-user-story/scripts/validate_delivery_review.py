"""只读核对评审证据账本；不认证语义完整、独立性真实性或人工批准。"""

import argparse
import hashlib
import json
from pathlib import Path

from delivery_review_references import rendered_anchors, validate_owner


def input_fingerprint(refs):
    """按路径及实际内容指纹计算所有视角共同输入的身份。"""
    ordered = sorted(refs, key=lambda row: row["path"])
    return hashlib.sha256(json.dumps(ordered, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def validate(record, root):
    """发现记录缺口即报告；字段自述不能证明模型实际遵守隔离。"""
    errors = []
    root = root.resolve()

    def require(condition, message):
        """收集所有问题，便于一次修复。"""
        if not condition:
            errors.append(message)

    def exists(reference):
        """检查相对文件真实存在，拒绝根目录外引用及符号链接逃逸。"""
        if not isinstance(reference, str) or not reference:
            return False
        path = Path(reference)
        resolved = (root / path).resolve()
        return not path.is_absolute() and resolved.is_relative_to(root) and resolved.is_file()

    require(isinstance(record, dict), "记录必须是对象")
    if not isinstance(record, dict):
        return {"record_valid": False, "errors": errors, "semantic_quality": "not_assessed"}
    require(record.get("schema") == "aef-story-delivery-review/v1", "评审记录版本不支持")
    require(record.get("scope") in ("whole", "local", "format"), "缺交付范围")
    require(record.get("mode") in ("independent", "targeted", "self"), "缺复核方式")
    require(bool(record.get("selection_reason")), "缺方式与视角选择理由")
    refs = record.get("input_refs", [])
    require(isinstance(refs, list) and bool(refs), "缺固定输入")
    clean_refs = []
    for ref in refs if isinstance(refs, list) else []:
        if not isinstance(ref, dict) or not exists(ref.get("path")):
            errors.append("输入路径无效或越界")
            continue
        actual = hashlib.sha256((root / ref["path"]).read_bytes()).hexdigest()
        require(ref.get("sha256") == actual, "固定输入已漂移：" + ref["path"])
        clean_refs.append({"path": ref["path"], "sha256": ref.get("sha256")})
    require(len({ref["path"] for ref in clean_refs}) == len(clean_refs), "输入路径重复")
    fingerprint = input_fingerprint(clean_refs)
    frozen_paths = {str((root / ref["path"]).resolve()) for ref in clean_refs}
    reviewers = record.get("reviewers", [])
    require(isinstance(reviewers, list), "reviewers 必须为列表")
    reviewers = reviewers if isinstance(reviewers, list) else []
    if record.get("mode") == "independent":
        require(len(reviewers) >= 2, "独立多视角审查需要多个代理；数量由范围决定")
        require(len({str(r.get("agent_id")) for r in reviewers if isinstance(r, dict)}) == len(reviewers), "代理身份重复")
        outputs = [str((root / r["output_ref"]).resolve()) for r in reviewers
                   if isinstance(r, dict) and isinstance(r.get("output_ref"), str)]
        require(len(set(outputs)) == len(reviewers), "独立代理须有各自实际输出文件")
    reviewer_map = {}
    for reviewer in reviewers:
        if not isinstance(reviewer, dict):
            errors.append("评审者记录必须为对象")
            continue
        require(all(isinstance(reviewer.get(k), str) and bool(reviewer[k].strip())
                    and reviewer[k] == reviewer[k].strip() for k in ("perspective", "agent_id")), "视角/代理身份须为稳定非空字符串")
        identifier, duties = reviewer.get("id"), reviewer.get("duties")
        require(isinstance(identifier, str) and bool(identifier) and identifier not in reviewer_map, "缺稳定评审者ID或ID重复")
        require(isinstance(duties, list) and bool(duties) and all(isinstance(d, str) and d for d in duties), "缺实际承接职责")
        if isinstance(identifier, str):
            reviewer_map[identifier] = duties if isinstance(duties, list) else []
        require(reviewer.get("input_fingerprint") == fingerprint, "评审者输入版本不一致")
        require(exists(reviewer.get("output_ref")), "缺评审者实际输出")
        if record.get("mode") == "independent":
            require(reviewer.get("isolated") is True, "独立阶段不能交换其他代理意见")
    applicability = record.get("applicability", [])
    require(isinstance(applicability, list), "applicability 必须为列表")
    applicability = applicability if isinstance(applicability, list) else []
    if record.get("scope") == "whole":
        named = {r.get("perspective") for r in applicability if isinstance(r, dict)
                 and isinstance(r.get("perspective"), str)}
        require({"platform_architect", "business_ecosystem"}.issubset(named), "整体请求须核对平台架构师和商业生态是否适用")
    perspectives = set()
    for row in applicability:
        require(isinstance(row, dict) and row.get("decision") in ("selected", "covered", "not_applicable", "unknown")
                and bool(row.get("reason")), "视角适用性缺依据")
        perspective = row.get("perspective") if isinstance(row, dict) else None
        require(isinstance(perspective, str) and bool(perspective) and perspective not in perspectives, "同版视角适用性须唯一且有身份")
        if isinstance(perspective, str):
            perspectives.add(perspective)
        if isinstance(row, dict) and row.get("decision") in ("selected", "covered"):
            assigned = row.get("covered_by", [])
            require(isinstance(assigned, list) and bool(assigned), "选中视角缺实际承接者")
            for identifier in assigned if isinstance(assigned, list) else []:
                require(isinstance(identifier, str) and identifier in reviewer_map
                        and row.get("perspective") in reviewer_map[identifier], "视角没有被所指评审者实际承接")
    coverage = record.get("coverage", [])
    require(isinstance(coverage, list) and bool(coverage), "缺覆盖与归属记录")
    for row in coverage if isinstance(coverage, list) else []:
        if not isinstance(row, dict):
            errors.append("覆盖行必须为对象")
            continue
        treatment = row.get("treatment")
        require(bool(row.get("id")) and bool(row.get("dimension")), "覆盖项缺身份或业务维度")
        require(treatment in ("story", "rule", "future-ac", "task", "defer", "na", "gap"), "覆盖项层级无效")
        require(bool(row.get("reason")), "覆盖项缺层级或取舍理由")
        owners = row.get("owner_refs", [])
        require(isinstance(owners, list), "归属必须为引用列表")
        if treatment in ("story", "rule", "future-ac"):
            require(bool(owners), "Story/规则/后续AC缺所属故事或候选的明确落点")
        for owner in owners if isinstance(owners, list) else []:
            errors.extend(validate_owner(owner, root, frozen_paths))
    issues = record.get("issues", [])
    require(isinstance(issues, list), "issues 必须为列表")
    seen = set()
    for issue in issues if isinstance(issues, list) else []:
        if not isinstance(issue, dict):
            errors.append("问题必须为对象")
            continue
        identifier = issue.get("id")
        if not isinstance(identifier, str):
            errors.append("问题ID必须为字符串")
            continue
        require(bool(identifier) and identifier not in seen, "问题ID缺失或重复")
        seen.add(identifier)
        require(issue.get("severity") in ("minor", "major", "critical"), "问题缺影响判断")
        require(issue.get("status") in ("open", "resolved", "needs_decision", "retained"), "问题缺处置状态")
        evidence = issue.get("evidence_refs", [])
        require(isinstance(evidence, list) and bool(evidence), "问题缺发现证据")
        for item in evidence if isinstance(evidence, list) else []:
            require(exists(item), "问题证据不存在或越界")
        if issue.get("status") in ("resolved", "retained"):
            require(exists(issue.get("resolution_ref")), "问题缺修订或保留依据")
        if issue.get("severity") in ("major", "critical") and issue.get("status") != "resolved":
            require(record.get("conclusion") != "reviewable", "关键缺口未解决不能声称已收敛可审阅")
    issue_map = {row["id"]: row for row in issues if isinstance(row, dict) and isinstance(row.get("id"), str)} if isinstance(issues, list) else {}
    for row in coverage if isinstance(coverage, list) else []:
        if not isinstance(row, dict):
            continue
        if row.get("blocking") is True:
            require(record.get("conclusion") != "reviewable", "明确阻断项不能与已收敛结论并存")
        if row.get("treatment") == "gap" or (row.get("treatment") == "defer" and row.get("blocking") is True):
            related = row.get("issue_ids", [])
            valid = isinstance(related, list) and bool(related) and all(isinstance(i, str) and i in issue_map for i in related)
            require(valid, "缺口/阻断后移项须关联真实问题")
            if valid:
                require(any(issue_map[i].get("status") != "resolved" for i in related), "缺口仍存在却关联全已解决问题")
        if row.get("treatment") == "defer":
            require(type(row.get("blocking")) is bool, "后移项须声明是否阻断本轮")
    require(record.get("conclusion") in ("reviewable", "needs_decision", "incomplete"), "缺有限评审结论")
    require(record.get("approval_claim") is False and record.get("utility_claim") is False, "评审账本不得声明人工批准或实际效用")
    return {"record_valid": not errors, "errors": errors, "input_fingerprint": fingerprint,
            "semantic_quality": "not_assessed", "independence": "declared_not_authenticated",
            "approval": "not_verified"}


def main():
    """命令行只读校验，非法输入返回非零退出码。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", type=Path)
    parser.add_argument("--root", type=Path, required=True, help="允许引用的证据目录")
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.record.read_text(encoding="utf-8")), args.root)
    except (OSError, ValueError, TypeError) as error:
        result = {"record_valid": False, "errors": [str(error)], "semantic_quality": "not_assessed"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["record_valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
