"""持续维护模式：局部修改、修订历史和独立审批回归。"""
import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.find_spec("story_workspace")
if SPEC:
    import story_workspace as api


class WorkspaceTests(unittest.TestCase):
    """用户故事持续维护的行为测试。"""

    def setUp(self):
        """缺失实现时给出明确失败，建立包含两条故事的基线。"""
        self.assertIsNotNone(SPEC, "持续维护工具尚未实现")
        self.card = json.loads((ROOT / "tests/fixtures/valid-story-card-v2.json").read_text())
        self.w = api.import_v2(self.card)
        story = copy.deepcopy(self.w["objects"][1]["versions"][0]["content"])
        story["title"] = "独立的另一条故事"
        self.w = api.add_object(self.w, "story", "US-002", story, "新增另一条故事")

    def current(self, ident, workspace=None):
        """读取指定对象当前快照。"""
        return next(o for o in (workspace or self.w)["objects"] if o["id"] == ident)

    def approve_story(self, ident="US-001"):
        """模拟已有用户明确确认记录，不代表真实产品批准。"""
        self.w = api.review_object(self.w, ident, 1, "approved", "示例用户", "synthetic:story-confirmed")

    def test_import_keeps_card_and_starts_unapproved(self):
        self.assertEqual(self.w["origin"]["card"], self.card)
        self.assertFalse(api.readiness(self.w, "US-001")["ready"])
        self.assertEqual(self.current("US-001")["reviews"], [])

    def test_import_rejects_invalid_card(self):
        self.card["stories"][0]["actor"] = ""
        with self.assertRaises(ValueError):
            api.import_v2(self.card)

    def test_local_change_preserves_other_objects_and_old_snapshot(self):
        old = copy.deepcopy(self.w)
        content = copy.deepcopy(self.current("US-001")["versions"][-1]["content"])
        content["goal"] = "定位之后暂停视频"
        revised = api.revise_object(self.w, "US-001", 1, content, "用户调整目标")
        self.assertEqual(self.w, old)
        self.assertEqual(self.current("US-002", revised), self.current("US-002"))
        self.assertEqual(self.current("US-001", revised)["versions"][0], self.current("US-001")["versions"][0])
        self.assertEqual(self.current("US-001", revised)["versions"][-1]["revision"], 2)
        self.assertEqual(api.validate_workspace(revised, self.w), [])

    def test_story_change_makes_bound_acceptance_stale(self):
        self.approve_story()
        self.w = api.review_object(self.w, "AC-US-001-S", 1, "approved", "示例用户", "synthetic:ac")
        content = copy.deepcopy(self.current("US-001")["versions"][-1]["content"])
        content["goal"] += "并暂停"
        newer = api.revise_object(self.w, "US-001", 1, content, "改变目标")
        self.assertIn("AC-US-001-S", api.readiness(newer, "US-001")["stale_acceptance"])
        self.assertEqual(self.current("AC-US-001-S", newer), self.current("AC-US-001-S"))
        self.assertFalse(api.readiness(newer, "US-001")["ready"])

    def test_acceptance_change_preserves_story_review(self):
        self.approve_story()
        content = copy.deepcopy(self.current("AC-US-001-F")["versions"][-1]["content"])
        content["then"] = "明确提示并允许重新上传"
        newer = api.revise_object(self.w, "AC-US-001-F", 1, content, "完善失败恢复")
        self.assertEqual(self.current("US-001", newer), self.current("US-001"))
        self.assertEqual(self.current("AC-US-001-F", newer)["versions"][-1]["revision"], 2)

    def test_acceptance_cannot_be_approved_before_story(self):
        with self.assertRaises(ValueError):
            api.review_object(self.w, "AC-US-001-S", 1, "approved", "用户", "synthetic:ac")

    def test_ready_requires_three_approved_types(self):
        self.approve_story()
        for ident in ("AC-US-001-S", "AC-US-001-F"):
            self.w = api.review_object(self.w, ident, 1, "approved", "用户", "synthetic:ac")
        self.assertFalse(api.readiness(self.w, "US-001")["ready"])
        self.w = api.review_object(self.w, "AC-US-001-B", 1, "approved", "用户", "synthetic:ac")
        self.assertTrue(api.readiness(self.w, "US-001")["ready"])

    def test_ready_requires_invest_evidence(self):
        self.approve_story()
        content = copy.deepcopy(self.current("US-001")["versions"][-1]["content"])
        content["invest_review"]["small"]["status"] = "risk"
        newer = api.revise_object(self.w, "US-001", 1, content, "发现故事过大")
        self.assertFalse(api.readiness(newer, "US-001")["ready"])

    def test_duplicate_and_retired_ids_cannot_be_reused(self):
        content = copy.deepcopy(self.current("US-002")["versions"][-1]["content"])
        content["lifecycle"] = "retired"
        self.w = api.revise_object(self.w, "US-002", 1, content, "用户明确暂退")
        with self.assertRaises(ValueError):
            api.add_object(self.w, "story", "US-002", content, "不能复用")
        self.assertEqual(api.next_id(self.w, "story"), "US-003")

    def test_stale_write_and_noop_rejected(self):
        content = self.current("US-001")["versions"][-1]["content"]
        with self.assertRaises(ValueError):
            api.revise_object(self.w, "US-001", 99, content, "过期更新")
        with self.assertRaises(ValueError):
            api.revise_object(self.w, "US-001", 1, content, "没有变化")

    def test_previous_detects_history_rewrite_and_deletion(self):
        damaged = copy.deepcopy(self.w)
        damaged["objects"][1]["versions"][0]["content"]["goal"] = "被改写"
        self.assertTrue(api.validate_workspace(damaged, self.w))
        damaged = copy.deepcopy(self.w)
        damaged["objects"].pop()
        self.assertTrue(api.validate_workspace(damaged, self.w))

    def test_reordered_objects_keep_identity(self):
        reordered = copy.deepcopy(self.w)
        reordered["objects"].reverse()
        self.assertEqual(api.validate_workspace(reordered, self.w), [])
        self.assertEqual(api.next_id(reordered, "story"), "US-003")

    def test_broken_references_and_revision_rejected(self):
        damaged = copy.deepcopy(self.w)
        damaged["objects"][2]["versions"][0]["content"]["story_revision"] = 99
        self.assertTrue(api.validate_workspace(damaged))
        damaged = copy.deepcopy(self.w)
        damaged["objects"][0]["versions"][0]["revision"] = True
        self.assertTrue(api.validate_workspace(damaged))

    def test_malformed_inputs_fail_closed(self):
        for bad in (None, [], {}, {"schema_version": "aef-story-workspace/v1", "objects": [None]}):
            with self.subTest(bad=bad):
                self.assertTrue(api.validate_workspace(bad))

    def test_render_includes_ids_revisions_and_no_maps(self):
        text = api.render(self.w)
        for expected in ("US-001@r1", "US-002@r1", "AC-US-001-S@r1", "提升长视频学习效率"):
            self.assertIn(expected, text)
        self.assertNotIn("ITER-", text)

    def test_unicode_legacy_ids_are_preserved(self):
        self.card["epic"]["epic_id"] = "史诗-001"
        imported = api.import_v2(self.card)
        self.assertEqual(imported["objects"][0]["id"], "史诗-001")

    def test_new_stale_approval_rejected_against_previous(self):
        self.approve_story()
        content = copy.deepcopy(self.current("US-001")["versions"][-1]["content"])
        content["goal"] += "并暂停"
        previous = api.revise_object(self.w, "US-001", 1, content, "用户改目标")
        damaged = copy.deepcopy(previous)
        self.current("AC-US-001-S", damaged)["reviews"].append(
            {"revision": 1, "decision": "approved", "actor": "用户", "ref": "synthetic:stale"})
        self.assertTrue(api.validate_workspace(damaged, previous))

    def test_null_optional_title_is_rejected(self):
        damaged = copy.deepcopy(self.w)
        self.current("AC-US-001-S", damaged)["versions"][0]["content"]["title"] = None
        self.assertTrue(api.validate_workspace(damaged))

    def test_malformed_legacy_import_reports_value_error(self):
        self.card["status"] = []
        with self.assertRaises(ValueError):
            api.import_v2(self.card)

    def test_malformed_new_approval_fails_closed(self):
        damaged = copy.deepcopy(self.w)
        obj = self.current("AC-US-001-S", damaged)
        obj["versions"][0]["content"]["story_id"] = []
        obj["reviews"].append({"revision": 1, "decision": "approved", "actor": "用户", "ref": "synthetic:bad"})
        self.assertTrue(api.validate_workspace(damaged, self.w))

    def test_aggregated_approval_and_revision_requires_adjacent_baselines(self):
        original = copy.deepcopy(self.w)
        self.approve_story()
        approved = copy.deepcopy(self.w)
        content = copy.deepcopy(self.current("US-001")["versions"][-1]["content"])
        content["goal"] += "并暂停"
        revised = api.revise_object(approved, "US-001", 1, content, "变更")
        self.assertEqual(api.validate_workspace(approved, original), [])
        self.assertEqual(api.validate_workspace(revised, approved), [])
        self.assertTrue(api.validate_workspace(revised, original))

    def test_cli_error_is_json_and_read_only(self):
        import subprocess
        result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/story_workspace.py"), "validate",
                                 str(ROOT / "tests/fixtures/invalid-story-card.json")],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
