"""故事库行为回归：独立卡片、局部变更、无损迁移和固定引用。"""
import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.find_spec("story_library")
if SPEC:
    import story_library as lib
import story_workspace as ws


class LibraryTests(unittest.TestCase):
    """以实际旧包构造多Epic故事库。"""

    def setUp(self):
        """先断言新功能存在，再建立每个测试独立输入。"""
        self.assertIsNotNone(SPEC, "故事库尚未实现")
        self.data = json.loads((ROOT / "examples/04-local-revision/story-workspace.json").read_text())
        self.data = ws.add_object(self.data, "epic", "EP-002",
                                  {"title": "管理学习资料", "outcome": "方便整理"}, "新增史诗")
        story = copy.deepcopy(next(o for o in self.data["objects"] if o["id"] == "US-002")["versions"][-1]["content"])
        story["epic_id"] = "EP-002"
        self.data = ws.revise_object(self.data, "US-002", 1, story, "调整归类")
        story = copy.deepcopy(story)
        story.pop("epic_id")
        story["title"] = "未归类故事"
        self.data = ws.add_object(self.data, "story", "US-003", story, "保留待归类故事")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "library"
        self.write(lib.export_library(self.data))

    def write(self, files):
        """仅测试夹具写入；正式CLI本身不写文件。"""
        for name, content in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    def object(self, ident):
        """获取指定对象，不依赖文件或对象顺序。"""
        return next(o for o in self.data["objects"] if o["id"] == ident)

    def test_index_groups_epics_and_unassigned_without_story_body(self):
        index = (self.root / "index.md").read_text()
        for phrase in ("EPIC-001", "EP-002", "未归类", "stories/US-001.md", "US-002@r2"):
            self.assertIn(phrase, index)
        self.assertNotIn(self.object("US-001")["versions"][-1]["content"]["statement"], index)

    def test_each_card_only_contains_own_story_and_acceptance(self):
        card = (self.root / "stories/US-001.md").read_text()
        self.assertIn("1. ", card)
        self.assertIn("2. ", card)
        self.assertIn("3. ", card)
        self.assertIn("明确说明失败原因并允许重新上传", card)
        for noise in ("审阅：", "修订记录", "invest_review", "绑定故事修订", "@r", "- 用户：", "- 场景：", "- 目标：", "- 价值："):
            self.assertNotIn(noise, card)
        self.assertNotIn("US-002", card)
        self.assertNotIn("US-003", card)
        self.assertNotIn("管理学习资料", card)

    def test_metadata_has_no_story_collection(self):
        metadata = json.loads((self.root / ".story-library.json").read_text())
        self.assertNotIn("stories", metadata)
        self.assertNotIn("objects", metadata)
        self.assertNotIn("US-003", json.dumps(metadata, ensure_ascii=False))
        self.assertTrue((self.root / ".story-data/US-001.json").is_file())

    def test_roundtrip_preserves_all_object_versions_and_reviews(self):
        actual = lib.read_library(self.root)
        self.assertEqual({o["id"]: o for o in actual["objects"]},
                         {o["id"]: o for o in self.data["objects"]})
        self.assertEqual(actual["context"], self.data["context"])
        self.assertEqual(actual.get("origin"), self.data.get("origin"))
        self.assertEqual(lib.validate_library(self.root), [])

    def test_edit_story_only_changes_own_files_and_index(self):
        content = copy.deepcopy(self.object("US-002")["versions"][-1]["content"])
        content["goal"] += "并分享"
        content["statement"] = content["statement"].rstrip("。") + "，并分享结果。"
        plan = lib.plan_change(self.root, "revise", "US-002", content=content, expected=2, reason="调整目标")
        paths = {item["path"] for item in plan["files"]}
        self.assertEqual(paths, {".story-data/US-002.json", "stories/US-002.md", "index.md"})
        before = (self.root / "stories/US-001.md").read_bytes()
        self.write({f["path"]: f["content"] for f in plan["files"]})
        self.assertEqual((self.root / "stories/US-001.md").read_bytes(), before)
        self.assertEqual(lib.validate_library(self.root), [])

    def test_edit_acceptance_does_not_touch_other_card_or_metadata(self):
        content = copy.deepcopy(self.object("AC-US-001-F")["versions"][-1]["content"])
        content["then"] += "，保留已输入内容"
        plan = lib.plan_change(self.root, "revise", "AC-US-001-F", content=content, expected=2, reason="补充恢复")
        paths = {f["path"] for f in plan["files"]}
        self.assertTrue({".story-data/US-001.json", "stories/US-001.md"} <= paths)
        self.assertTrue(paths <= {".story-data/US-001.json", "stories/US-001.md", "index.md"})

    def test_add_story_does_not_rewrite_existing_cards(self):
        content = copy.deepcopy(self.object("US-003")["versions"][-1]["content"])
        plan = lib.plan_change(self.root, "add", "US-004", kind="story", content=content, reason="新增")
        self.assertEqual({f["path"] for f in plan["files"]},
                         {".story-data/US-004.json", "stories/US-004.md", "index.md"})
        self.assertEqual(next(f for f in plan["files"] if f["path"].endswith("US-004.md"))["before_sha256"], None)

    def test_epic_edit_only_changes_index_and_metadata(self):
        content = copy.deepcopy(self.object("EP-002")["versions"][-1]["content"])
        content["title"] = "整理学习材料"
        plan = lib.plan_change(self.root, "revise", "EP-002", content=content, expected=1, reason="完善标题")
        self.assertEqual({f["path"] for f in plan["files"]}, {".story-library.json", "index.md"})

    def test_reclassification_preserves_card_path(self):
        content = copy.deepcopy(self.object("US-003")["versions"][-1]["content"])
        content["epic_id"] = "EP-002"
        plan = lib.plan_change(self.root, "revise", "US-003", content=content, expected=1, reason="归类")
        self.assertEqual({f["path"] for f in plan["files"]},
                         {".story-data/US-003.json", "index.md"})
        self.assertTrue((self.root / "stories/US-003.md").is_file())

    def test_reference_pins_story_and_acceptance_without_body(self):
        ref = lib.make_reference(self.data, "US-001")
        self.assertEqual(ref["story_revision"], 1)
        self.assertIn({"id": "AC-US-001-F", "revision": 2}, ref["acceptance_refs"])
        self.assertNotIn("goal", ref)
        changed = copy.deepcopy(self.object("AC-US-001-F")["versions"][-1]["content"])
        changed["then"] += "稍后重试"
        newer = ws.revise_object(self.data, "AC-US-001-F", 2, changed, "更新")
        resolved = lib.resolve_reference(newer, ref)
        self.assertEqual(resolved["acceptance"][1]["revision"], 2)
        self.assertTrue(resolved["outdated"])
        self.assertEqual(ref["acceptance_refs"][1]["revision"], 2)

    def test_dangling_reference_rejected(self):
        ref = lib.make_reference(self.data, "US-001")
        ref["story_revision"] = 99
        with self.assertRaises(ValueError):
            lib.resolve_reference(self.data, ref)

    def test_baseline_plan_detects_concurrent_change(self):
        content = copy.deepcopy(self.object("US-003")["versions"][-1]["content"])
        content["goal"] += "新目标"
        plan = lib.plan_change(self.root, "revise", "US-003", content=content, expected=1, reason="更新")
        self.assertEqual(lib.check_plan(self.root, plan), [])
        with (self.root / "stories/US-003.md").open("a") as f:
            f.write("人工补充")
        self.assertTrue(lib.check_plan(self.root, plan))

    def test_manual_projection_edit_is_not_overwritten(self):
        (self.root / "stories/US-001.md").write_text("人工保留内容")
        self.assertTrue(lib.validate_library(self.root))
        with self.assertRaises(ValueError):
            lib.plan_change(self.root, "review", "US-002", expected=2,
                            outcome="approved", actor="示例", ref="synthetic:approved")

    def test_missing_card_is_detected(self):
        (self.root / "stories/US-001.md").unlink()
        self.assertTrue(lib.validate_library(self.root))

    def test_history_rewrite_detected_against_previous_library(self):
        before = lib.read_library(self.root)
        altered = copy.deepcopy(before)
        next(o for o in altered["objects"] if o["id"] == "US-001")["versions"][0]["content"]["goal"] = "历史改写"
        self.write(lib.export_library(altered))
        self.assertTrue(lib.validate_library(self.root, previous=before))

    def test_untrusted_id_cannot_escape_library(self):
        content = copy.deepcopy(self.object("US-003")["versions"][-1]["content"])
        updated = ws.add_object(self.data, "story", "../../outside", content, "保留特殊旧ID")
        files = lib.export_library(updated)
        self.assertTrue(all(".." not in Path(path).parts and not Path(path).is_absolute() for path in files))
        self.assertTrue(any("story-" in path for path in files))

    def test_symlink_source_is_rejected(self):
        source = self.root / ".story-data/US-001.json"
        external = Path(self.temp.name) / "external.json"
        external.write_bytes(source.read_bytes())
        source.unlink()
        source.symlink_to(external)
        self.assertTrue(lib.validate_library(self.root))

    def test_acceptance_cannot_move_to_another_story(self):
        content = copy.deepcopy(self.object("AC-US-001-F")["versions"][-1]["content"])
        content["story_id"] = "US-002"
        content["story_revision"] = 2
        with self.assertRaises(ValueError):
            lib.plan_change(self.root, "revise", "AC-US-001-F", content=content, expected=2, reason="迁移归属")

    def test_bad_library_metadata_is_reported(self):
        (self.root / ".story-library.json").write_text("[]")
        self.assertTrue(lib.validate_library(self.root))


    def test_new_library_rejects_symlink_root(self):
        target = Path(self.temp.name) / "external"
        target.mkdir()
        link = Path(self.temp.name) / "linked"
        link.symlink_to(target, target_is_directory=True)
        self.assertTrue(lib.check_plan(link, lib.make_plan({}, lib.export_library(self.data))))

    def test_plan_rejects_path_aliases(self):
        plan = lib.make_plan({}, {"stories/US-001.md": "第一份", "stories//US-001.md": "第二份"})
        self.assertTrue(lib.check_plan(Path(self.temp.name) / "new", plan))

    def test_retired_acceptance_does_not_block_new_reference(self):
        old_ref = lib.make_reference(self.data, "US-001")
        newer = copy.deepcopy(self.data)
        for obj in self.data["objects"]:
            if obj["kind"] == "acceptance" and obj["versions"][-1]["content"]["story_id"] == "US-001":
                content = copy.deepcopy(obj["versions"][-1]["content"])
                content["lifecycle"] = "retired"
                newer = ws.revise_object(newer, obj["id"], obj["versions"][-1]["revision"], content, "退役旧验收")
        content = copy.deepcopy(self.object("US-001")["versions"][-1]["content"])
        content["goal"] += "新目标"
        newer = ws.revise_object(newer, "US-001", 1, content, "修改目标")
        ref = lib.make_reference(newer, "US-001")
        self.assertEqual(ref["acceptance_refs"], [])
        self.assertFalse(lib.resolve_reference(newer, ref)["outdated"])
        self.assertTrue(lib.resolve_reference(newer, old_ref)["outdated"])

    def test_active_stale_acceptance_cannot_generate_reference(self):
        content = copy.deepcopy(self.object("US-001")["versions"][-1]["content"])
        content["goal"] += "新目标"
        newer = ws.revise_object(self.data, "US-001", 1, content, "修改目标")
        with self.assertRaises(ValueError):
            lib.make_reference(newer, "US-001")


    def test_readable_card_preserves_full_statement_and_changes(self):
        content = copy.deepcopy(self.object("US-001")["versions"][-1]["content"])
        content["statement"] += "且只能查看本人上传的视频。"
        newer = ws.revise_object(self.data, "US-001", 1, content, "补充访问限制")
        exported = lib.export_library(newer)
        self.assertIn(content["statement"], exported["stories/US-001.md"])
        self.assertNotEqual(exported["stories/US-001.md"], (self.root / "stories/US-001.md").read_text())
        self.assertEqual(newer["objects"][0], self.data["objects"][0])


if __name__ == "__main__":
    unittest.main()
