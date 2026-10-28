"""复制真实故事库，验证评审账本与原生固定引用的接入合同。"""

import copy
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_delivery_review as review
from story_library_references import make_reference, resolve_reference
from story_library_store import export_library, read_library
from story_workspace_model import add_object, revise_object


class NativeDeliveryReviewTests(unittest.TestCase):
    """用原库作为修订与 AC 绑定的事实源，不更改原始夹具。"""

    def setUp(self):
        """复制完整库，并构造含真实输入和独立输出的评审记录。"""
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.library = self.root / "library"
        shutil.copytree(ROOT / "examples/05-story-library/library", self.library)
        for name in ("source.md", "user.md", "architect.md", "resolution.md"):
            (self.root / name).write_text("# 合成评审证据\n", encoding="utf-8")
        self.reference = make_reference(read_library(self.library), "US-001")
        self.anchor = "us-001点击逐字稿跳转视频"
        self.record = {
            "schema": "aef-story-delivery-review/v1", "scope": "whole", "mode": "independent",
            "selection_reason": "检查用户结果及固定对象归属", "input_refs": [],
            "applicability": [
                {"perspective": "platform_architect", "decision": "selected", "reason": "跨故事归属", "covered_by": ["architect"]},
                {"perspective": "business_ecosystem", "decision": "not_applicable", "reason": "合成库无供给交易关系"}],
            "reviewers": [
                {"id": "user", "perspective": "user", "duties": ["user"], "agent_id": "agent-user", "isolated": True, "output_ref": "user.md"},
                {"id": "architect", "perspective": "architect", "duties": ["platform_architect"], "agent_id": "agent-architect", "isolated": True, "output_ref": "architect.md"}],
            "coverage": [{"id": "CV-1", "dimension": "固定对象归属", "treatment": "rule", "reason": "交由所属故事验收", "owner_refs": []}],
            "issues": [{"id": "ISS-1", "severity": "major", "status": "resolved", "evidence_refs": ["user.md"], "resolution_ref": "resolution.md"}],
            "conclusion": "reviewable", "approval_claim": False, "utility_claim": False}
        self.use_reference(self.reference)

    def freeze(self, exclude=()):
        """重算真实输入及评审者指纹，避免负例只触发内容漂移。"""
        self.record["input_refs"] = [
            {"path": path.relative_to(self.root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(self.root.rglob("*"))
            if path.is_file() and path.relative_to(self.root).as_posix() not in exclude]
        fingerprint = review.input_fingerprint(self.record["input_refs"])
        for reviewer in self.record["reviewers"]:
            reviewer["input_fingerprint"] = fingerprint

    def use_reference(self, payload, index="library/pinned.json", native=True):
        """保存引用或原 resolve 输出；library_root 明确相对证据根。"""
        path = self.root / index
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        reference = payload.get("reference", payload)
        owner = {key: reference[key] for key in ("package_id", "story_id", "story_revision")}
        owner.update(index_ref=index, anchor=self.anchor)
        if native:
            owner["library_root"] = "library"
        self.record["coverage"][0]["owner_refs"] = [owner]
        self.freeze()

    def assert_valid(self, expected):
        """通过公开入口检查完整评审记录，并在失败时显示实际错误。"""
        result = review.validate(self.record, self.root)
        self.assertEqual(result["record_valid"], expected, result["errors"])

    def test_cli_reference_and_resolve_outside_library(self):
        """真实 CLI 的原引用和解析输出都可放在库外证据目录。"""
        command = [sys.executable, "-B", str(ROOT / "scripts/story_library.py")]
        made = subprocess.run(command + ["reference", str(self.library), "--id", "US-001"],
                              check=True, capture_output=True, text=True)
        reference = json.loads(made.stdout)
        self.use_reference(reference, "evidence/reference.json")
        resolved = subprocess.run(command + ["resolve", str(self.library), "--reference",
                                            str(self.root / "evidence/reference.json")],
                                  check=True, capture_output=True, text=True)
        for payload in (reference, json.loads(resolved.stdout)):
            with self.subTest(wrapped="reference" in payload):
                self.use_reference(payload, "evidence/reference.json")
                self.assert_valid(True)

    def test_historical_story_and_acceptance_use_original_resolution(self):
        """旧修订由原解析器回读，当前 Markdown 仍用于导航。"""
        data = read_library(self.library)
        story = next(obj for obj in data["objects"] if obj["id"] == "US-001")
        content = copy.deepcopy(story["versions"][-1]["content"])
        content["title"] = "新版逐字稿定位"
        newer = revise_object(data, "US-001", 1, content, "测试追加修订，保留历史")
        for relative, text in export_library(newer).items():
            (self.library / relative).write_text(text, encoding="utf-8")
        historical = copy.deepcopy(self.reference)
        next(row for row in historical["acceptance_refs"] if row["id"] == "AC-US-001-F")["revision"] = 1
        resolved = resolve_reference(read_library(self.library), historical)
        self.assertTrue(resolved["outdated"])
        self.assertEqual(resolved["story"]["content"]["title"], "点击逐字稿跳转视频")
        self.anchor = "us-001新版逐字稿定位"
        for payload in (historical, resolved):
            with self.subTest(wrapped="reference" in payload):
                self.use_reference(payload)
                self.assert_valid(True)

    def test_native_dependencies_must_all_be_frozen(self):
        """未引用故事的数据也参与原库有效性，不能遗漏其冻结证据。"""
        required = ["library/.story-library.json", "library/pinned.json", "library/stories/US-001.md"]
        required += [path.relative_to(self.root).as_posix() for path in self.library.glob(".story-data/*.json")]
        for relative in required:
            with self.subTest(missing=relative):
                self.freeze(exclude=(relative,))
                self.assert_valid(False)

    def test_invalid_library_root_never_falls_back_to_custom_index(self):
        """显式原生模式遇到越界、缺失或非库路径时必须拒绝。"""
        owner = self.record["coverage"][0]["owner_refs"][0]
        for root in ("../outside", str(self.library), "missing", "source.md", "library/stories", "", None):
            with self.subTest(library_root=root):
                owner["library_root"] = root
                self.assert_valid(False)

    def test_unreadable_or_invalid_native_data_cannot_downgrade(self):
        """即使自定义索引足以定位卡片，损坏的原生数据仍须阻断。"""
        for relative in (".story-library.json", ".story-data/US-003.json"):
            path = self.library / relative
            original = path.read_bytes()
            for content in (b"\xff", b"{}"):
                with self.subTest(file=relative, content=content):
                    path.write_bytes(content)
                    self.freeze()
                    self.assert_valid(False)
            path.write_bytes(original)

    def test_original_revision_and_acceptance_binding_are_enforced(self):
        """索引身份相符仍不能放行不存在的修订、AC 或错误故事绑定。"""
        data = read_library(self.library)
        content = copy.deepcopy(next(obj for obj in data["objects"] if obj["kind"] == "acceptance")["versions"][-1]["content"])
        content.update(story_id="US-002", story_revision=1)
        foreign = "AC-US-002-S"
        data = add_object(data, "acceptance", foreign, content, "合成跨故事绑定反例")
        for relative, text in export_library(data).items():
            (self.library / relative).write_text(text, encoding="utf-8")
        cases = []
        for field, value in (("story_revision", 99), ("acceptance_refs", None),
                             ("acceptance_refs", [{"id": foreign, "revision": 1}]),
                             ("acceptance_refs", [{"id": "AC-US-001-F", "revision": 99}])):
            reference = copy.deepcopy(self.reference)
            reference[field] = value
            cases.append(reference)
        for reference in cases:
            with self.subTest(reference=reference):
                self.use_reference(reference)
                self.assert_valid(False)

    def test_native_card_path_must_match_stable_story(self):
        """复制同一正文到另一文件不能替代原生固定卡片路径。"""
        shutil.copyfile(self.library / "stories/US-001.md", self.library / "stories/copied.md")
        reference = dict(self.reference, card_path="stories/copied.md")
        self.use_reference(reference)
        self.assert_valid(False)

    def test_resolve_wrapper_cannot_forge_original_body(self):
        """wrapper 的历史 Story 与 AC 正文必须等于原解析结果。"""
        resolved = resolve_reference(read_library(self.library), self.reference)
        for field in ("story", "acceptance"):
            with self.subTest(field=field):
                forged = copy.deepcopy(resolved)
                if field == "story":
                    forged["story"]["content"]["goal"] = "伪造另一项需求"
                else:
                    forged["acceptance"][0]["content"]["then"] = "伪造验收结果"
                self.use_reference(forged)
                self.assert_valid(False)

    def test_legacy_single_collection_and_card_path_base_remain_supported(self):
        """未声明 library_root 的自定义单引用、集合及路径基准保持兼容。"""
        reference = dict(self.reference, card_path="US-001.md")
        for payload in (dict(reference, card_path_base="../library/stories"),
                        {"package_id": reference["package_id"], "references": [reference],
                         "card_path_base": "../library/stories"}):
            with self.subTest(collection="references" in payload):
                self.use_reference(self.reference, "legacy/pinned.json", native=False)
                (self.root / "legacy/pinned.json").write_text(json.dumps(payload), encoding="utf-8")
                self.freeze()
                self.assert_valid(True)


if __name__ == "__main__":
    unittest.main()
