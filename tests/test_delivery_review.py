"""评审记录的反例测试，只验证证据账本，不验证产品价值。"""

import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


class DeliveryReviewTests(unittest.TestCase):
    """检查缺证据、漂移、漏归属和虚假收敛被明确报告。"""

    def setUp(self):
        """构造两个独立视角及固定来源的最小真实文件集合。"""
        spec = importlib.util.spec_from_file_location("delivery_review", ROOT / "scripts/validate_delivery_review.py")
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("source.md", "user.md", "architect.md", "story.md", "resolution.md"):
            (self.root / name).write_text("# 固定输入与证据\n", encoding="utf-8")
        (self.root / "story.md").write_text("# US-001 取得可用结果\n")
        (self.root / "pinned.json").write_text(json.dumps({"package_id":"DEMO", "story_id":"US-001", "story_revision":1, "card_path":"story.md"}))
        inputs = [{"path": name, "sha256": hashlib.sha256((self.root / name).read_bytes()).hexdigest()}
                  for name in ("source.md", "story.md", "pinned.json")]
        fingerprint = self.module.input_fingerprint(inputs)
        self.record = {"schema": "aef-story-delivery-review/v1", "scope": "whole", "mode": "independent",
            "selection_reason": "多个个人状态和共享能力，需要不同职责检查", "input_refs": inputs,
            "applicability": [{"perspective": "platform_architect", "decision": "selected", "reason": "共享与个人实例", "covered_by":["architect"]},
                              {"perspective": "business_ecosystem", "decision": "not_applicable", "reason": "无供给交易关系，已核对内容责任"}],
            "reviewers": [{"id":"user", "perspective": "user", "duties":["user"], "agent_id": "agent-user", "input_fingerprint": fingerprint, "isolated": True, "output_ref": "user.md"},
                          {"id":"architect", "perspective": "architect", "duties":["platform_architect"], "agent_id": "agent-architect", "input_fingerprint": fingerprint, "isolated": True, "output_ref": "architect.md"}],
            "coverage": [{"id": "CV-1", "dimension": "结果与隔离", "treatment": "rule", "reason": "逐故事后续验收覆盖",
                          "owner_refs": [{"package_id":"DEMO", "story_id":"US-001", "story_revision":1, "index_ref":"pinned.json", "anchor":"us-001-取得可用结果"}]}],
            "issues": [{"id": "ISS-1", "severity": "major", "status": "resolved", "evidence_refs": ["user.md"], "resolution_ref": "resolution.md"}],
            "conclusion": "reviewable", "approval_claim": False, "utility_claim": False}

    def validate(self):
        """调用只读验证接口。"""
        return self.module.validate(self.record, self.root)

    def refresh_inputs(self):
        """探针改正文后重算固定输入，避免只测到哈希漂移。"""
        for row in self.record["input_refs"]:
            row["sha256"] = hashlib.sha256((self.root / row["path"]).read_bytes()).hexdigest()
        fingerprint = self.module.input_fingerprint(self.record["input_refs"])
        for reviewer in self.record["reviewers"]:
            reviewer["input_fingerprint"] = fingerprint

    def test_valid_record_and_no_quality_claim(self):
        result = self.validate()
        self.assertTrue(result["record_valid"])
        self.assertEqual(result["semantic_quality"], "not_assessed")

    def test_source_drift_is_rejected(self):
        (self.root / "source.md").write_text("改变输入")
        self.assertFalse(self.validate()["record_valid"])

    def test_different_reviewer_input_is_rejected(self):
        self.record["reviewers"][1]["input_fingerprint"] = "0" * 64
        self.assertFalse(self.validate()["record_valid"])

    def test_cross_rule_cannot_lose_story_owner(self):
        self.record["coverage"][0]["owner_refs"] = []
        self.assertFalse(self.validate()["record_valid"])

    def test_independence_and_distinct_agents_are_required(self):
        self.record["reviewers"][1]["agent_id"] = "agent-user"
        self.assertFalse(self.validate()["record_valid"])
        self.record["reviewers"][1]["agent_id"] = "agent-architect"
        self.record["reviewers"][1]["isolated"] = False
        self.assertFalse(self.validate()["record_valid"])

    def test_open_major_cannot_be_closed_by_round_count(self):
        self.record["issues"][0]["status"] = "open"
        self.assertFalse(self.validate()["record_valid"])
        self.record["conclusion"] = "needs_decision"
        self.assertTrue(self.validate()["record_valid"])

    def test_missing_architect_and_ecosystem_applicability_is_rejected(self):
        self.record["applicability"] = []
        self.assertFalse(self.validate()["record_valid"])

    def test_local_self_review_does_not_need_platform_matrix(self):
        self.record.update(scope="local", mode="self", applicability=[], reviewers=[], selection_reason="仅改错别字")
        self.assertTrue(self.validate()["record_valid"])

    def test_extra_role_is_allowed_and_count_not_fixed(self):
        third = copy.deepcopy(self.record["reviewers"][0])
        (self.root / "third.md").write_text("# 独立交付意见\n")
        third.update(id="third", perspective="delivery", agent_id="third", output_ref="third.md")
        self.record["reviewers"].append(third)
        self.assertTrue(self.validate()["record_valid"])

    def test_path_escape_and_missing_evidence_are_rejected(self):
        self.record["issues"][0]["evidence_refs"] = ["../escape.md"]
        self.assertFalse(self.validate()["record_valid"])
        self.record["issues"][0]["evidence_refs"] = ["absent.md"]
        self.assertFalse(self.validate()["record_valid"])

    def test_no_approval_or_effectiveness_can_be_asserted(self):
        self.record["approval_claim"] = True
        self.assertFalse(self.validate()["record_valid"])

    def test_incomplete_input_does_not_crash(self):
        self.record = {"schema": "aef-story-delivery-review/v1"}
        self.assertFalse(self.validate()["record_valid"])

    def test_malformed_nested_fields_are_rejected(self):
        self.record["issues"][0]["id"] = []
        self.record["applicability"][0]["perspective"] = {"invalid": True}
        self.assertFalse(self.validate()["record_valid"])

    def test_retained_major_is_still_unresolved(self):
        self.record["issues"][0]["status"] = "retained"
        self.assertFalse(self.validate()["record_valid"])
        self.record["conclusion"] = "needs_decision"
        self.assertTrue(self.validate()["record_valid"])

    def test_gap_must_link_an_unresolved_issue(self):
        self.record["coverage"][0].update(treatment="gap", owner_refs=[])
        self.assertFalse(self.validate()["record_valid"])
        self.record["coverage"][0]["issue_ids"] = ["ISS-1"]
        self.record["issues"][0]["status"] = "open"
        self.record["conclusion"] = "incomplete"
        self.assertTrue(self.validate()["record_valid"])

    def test_generic_file_is_not_a_pinned_owner(self):
        self.record["coverage"][0]["owner_refs"] = ["story.md"]
        self.assertFalse(self.validate()["record_valid"])

    def test_wrong_package_revision_or_heading_are_rejected(self):
        original = copy.deepcopy(self.record["coverage"][0]["owner_refs"][0])
        for field, wrong in (("package_id", "OTHER"), ("story_revision", 99), ("anchor", "absent")):
            with self.subTest(field=field):
                self.record["coverage"][0]["owner_refs"][0] = dict(original, **{field:wrong})
                self.assertFalse(self.validate()["record_valid"])

    def test_owner_card_and_index_must_be_frozen_inputs(self):
        self.record["input_refs"] = self.record["input_refs"][:1]
        fingerprint = self.module.input_fingerprint(self.record["input_refs"])
        for reviewer in self.record["reviewers"]:
            reviewer["input_fingerprint"] = fingerprint
        self.assertFalse(self.validate()["record_valid"])

    def test_selected_role_must_have_assigned_actual_duty(self):
        self.record["reviewers"][1]["duties"] = ["user"]
        self.assertFalse(self.validate()["record_valid"])
        self.record["reviewers"][1]["duties"] = ["platform_architect"]
        self.record["applicability"][0]["covered_by"] = ["absent"]
        self.assertFalse(self.validate()["record_valid"])

    def test_independent_reports_must_have_distinct_targets(self):
        self.record["reviewers"][1]["output_ref"] = "user.md"
        self.assertFalse(self.validate()["record_valid"])

    def test_blocking_defer_blocks_even_minor_issue(self):
        self.record["coverage"][0].update(treatment="defer", blocking=True, issue_ids=["ISS-1"])
        self.record["issues"][0].update(severity="minor", status="open")
        self.assertFalse(self.validate()["record_valid"])
        self.record["conclusion"] = "needs_decision"
        self.assertTrue(self.validate()["record_valid"])

    def test_hidden_or_code_headings_are_not_targets(self):
        heading = "# US-001 取得可用结果"
        for text in (f"```markdown\n{heading}\n```\n", f"<!--\n{heading}\n-->\n", f"<pre>\n{heading}\n</pre>\n",
                     f"<!--\n{heading}\n", f"<div>同行正文\n{heading}\n</div>\n", f"<pre>\n\n{heading}\n"):
            with self.subTest(text=text):
                (self.root / "story.md").write_text(text)
                self.refresh_inputs()
                self.assertFalse(self.validate()["record_valid"])

    def test_closing_atx_and_setext_are_real_targets(self):
        for text in ("# US-001 取得可用结果 ###\n", "US-001 取得可用结果\n===================\n"):
            with self.subTest(text=text):
                (self.root / "story.md").write_text(text)
                self.refresh_inputs()
                self.assertTrue(self.validate()["record_valid"])

    def test_html_literals_in_code_do_not_hide_later_real_heading(self):
        """代码示例不能截断后续真实用户故事章节。"""
        for token in ("<!--", "<pre>", "<script>", "<style>", "<textarea>"):
            for prefix in (f"```html\n{token}\n```\n", f"`{token}`\n\n", f"    {token}\n\n"):
                with self.subTest(prefix=prefix):
                    (self.root / "story.md").write_text(prefix + "# US-001 取得可用结果\n")
                    self.refresh_inputs()
                    self.assertTrue(self.validate()["record_valid"])

    def test_real_html_blocks_remain_opaque_across_blank_lines_and_fences(self):
        """反引号或空行不能把真实HTML块中的伪标题变成归属。"""
        for opening in ("<!--", "<pre>", "<script>", "<style>", "<textarea>"):
            with self.subTest(opening=opening):
                (self.root / "story.md").write_text(opening + "\n```\n\n# US-001 取得可用结果\n")
                self.refresh_inputs()
                self.assertFalse(self.validate()["record_valid"])

    def test_closed_html_comment_allows_subsequent_real_heading(self):
        """真实注释中的围栏不能吞掉注释结束后的标题。"""
        (self.root / "story.md").write_text("<!--\n```\n-->\n# US-001 取得可用结果\n")
        self.refresh_inputs()
        self.assertTrue(self.validate()["record_valid"])

    def test_inline_code_anchor_is_not_real(self):
        (self.root / "story.md").write_text('# US-001 取得可用结果\n\n`<a id="fake"></a>`\n')
        self.record["coverage"][0]["owner_refs"][0]["anchor"] = "fake"
        self.refresh_inputs()
        self.assertFalse(self.validate()["record_valid"])

    def test_boolean_index_revision_is_not_numeric_revision(self):
        path = self.root / "pinned.json"
        data = json.loads(path.read_text())
        data["story_revision"] = True
        path.write_text(json.dumps(data))
        self.refresh_inputs()
        self.assertFalse(self.validate()["record_valid"])

    def test_same_perspective_cannot_have_opposite_decisions(self):
        self.record["applicability"].append({"perspective":"platform_architect", "decision":"not_applicable", "reason":"相反结论"})
        self.assertFalse(self.validate()["record_valid"])

    def test_agent_identity_is_stable_nonblank_text(self):
        for value in ({"id":"agent"}, "  "):
            with self.subTest(value=value):
                self.record["reviewers"][0]["agent_id"] = value
                self.assertFalse(self.validate()["record_valid"])


if __name__ == "__main__":
    unittest.main()
