"""维护问题的结构回归，不冒充实际Agent对话。"""
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class HealthRevisionTests(unittest.TestCase):
    """检查合同一致性及条件资源的组织。"""
    def test_exploration_contract(self):
        text=(ROOT/"skill.contract.yaml").read_text()
        self.assertIn("探索交接允许候选Story和缺失AC",text)
        self.assertIn("不得标为开发就绪",text)
        self.assertNotIn("condition: 双文件路径",text)
    def test_owner_boundaries(self):
        text=(ROOT/"tests/core-unit-mvp-cases.md").read_text()
        self.assertIn("不在User Story重建画布",text)
        self.assertNotIn("保留八章",text)
    def test_trigger_pair(self):
        self.assertIn("我要做一个",(ROOT/"tests/cases/success.yaml").read_text())
        self.assertIn("trigger: false",(ROOT/"tests/cases/tool-recommendation.yaml").read_text())
    def test_conditional_loading(self):
        text=(ROOT/"references/product-system.md").read_text()
        for heading in ("## 保存、版本与四类决定","## 恢复与变更","## 连续进入迭代的交接"):
            self.assertNotIn(heading,text)
        text=(ROOT/"references/story-library.md").read_text()
        self.assertIn("(revision-core.md)",text)
        self.assertNotIn("(continuous-maintenance.md)",text)
    def test_scope_revision_routes_to_business_only(self):
        text=(ROOT/"SKILL.md").read_text()
        self.assertIn("仅调整对话中的粗故事集合或MVP",text)
        self.assertIn("仅在操作具体Story/AC对象",text)
        text=(ROOT/"references/product-system.md").read_text()
        self.assertIn("这不属于故事库修订",text)
    def test_local_loading_checks_semantics(self):
        data=json.loads((ROOT/"tests/scenario-index.json").read_text())
        local=next(r for r in data["runs"] if r["id"]=="local-ac")
        self.assertNotIn("references/revision-core.md",local["required"])
        self.assertEqual(len(local["semantic_requirements"]),4)
        self.assertIn("references/revision-core.md",local["conditional_reads"])
    def test_evidence_index_is_honest(self):
        data=json.loads((ROOT/"tests/scenario-index.json").read_text())
        self.assertEqual(data["utility_claim"],"not-evaluated")
        for case in data["suites"]:
            self.assertTrue((ROOT/"tests"/case["path"]).is_file())
        for run in data["runs"]:
            self.assertEqual(run["status"],"not-evaluated")
            for path in run["required"]+run["avoid"]:
                self.assertTrue((ROOT/path).is_file())
    def test_local_edit_does_not_follow_core_link_unconditionally(self):
        text=(ROOT/"references/story-library.md").read_text()
        self.assertIn("不因出现核心链接而补读",text)
        self.assertIn("没有对应动作或缺口时，到此停止规则加载",text)
        self.assertIn("新增编号、跨包引用、拆分合并、退役",text)

if __name__=="__main__":
    unittest.main()
