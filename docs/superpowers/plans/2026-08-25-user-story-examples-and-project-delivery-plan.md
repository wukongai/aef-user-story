# User Story 完整案例与项目落盘 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 发布 `aef-user-story` 0.2.0，使 Agent 能通过可修改、可确认的对话把三类用户需求转成符合 INVEST、带三类验收条件、可安全写入项目并可追踪到下游 Spec/PRD 的双文件需求包。

**Architecture:** 根 `SKILL.md` 只承载强制互动状态机和停止点，三份直白 reference 分别负责写法、格式和项目落盘。`aef-story-card/v2` 用结构化 JSON 保存 INVEST、双确认、Acceptance 和多项下游路由；现有 Python 校验器继续支持 v1，并新增双文件一致性校验。三个案例同时提供完整对话和目标项目输出，作为行为说明与回归资产。

**Tech Stack:** 中文 Markdown、JSON、YAML、Python 3 标准库、`unittest`、Git、Skill Engineering Content Gate / Creation Review / Portable Self Test。

**执行状态（2026-08-25）：** Tasks 1–7 的本地实现与发布前验证均已完成；19 个 unittest 通过，Content Gate pass，Production Review 100/A，Portable Self Test pass 且 `target_unchanged: true`。验证证据见 `docs/superpowers/testing/2026-08-25-user-story-v0.2-test-report.md`。

## Global Constraints

- 目标版本固定为 `0.2.0`，公开仓库仍为 `wukongai/aef-user-story`，MIT License。
- User Story 使用 3C 和 INVEST；开发 Task 不在本 Skill 中生成。
- `E—Estimable` 只判断后续能否估算，不输出 Story Points。
- 每条准备下游交接的 Story 必须有 success、failure、boundary 三类 Acceptance。
- Story 和 Acceptance 分别确认；任一 Story 修改会使相关 Acceptance 失效。
- PRD 是可选路由，不是唯一出口；允许 `direct_spec / prd / backlog / specialist_review`。
- 默认项目目录为 `docs/requirements/<slug>/`，只生成 `user-story.md` 和 `story-card.json`。
- 写入项目前必须预览路径和内容并取得明确批准；已有文件禁止静默覆盖。
- v2 不输出 `vertical_slice_review`；旧 v1 校验兼容必须保留。
- 不生成正式 PRD、Spec、Plan、Task、测试代码或业务代码。
- 全部用户可见说明使用简体中文，标准术语、schema 字段和命令可以保留英文。
- 不伪造独立行为基线；没有新鲜独立上下文时保持 `utility_claim: false`。

---

## File Map

| 路径 | 职责 |
|---|---|
| `SKILL.md` | 强制对话、修改循环、两次确认、写入批准和下游钩子 |
| `references/how-to-write-user-story.md` | 3C、Epic/Story、标准句式、INVEST、Acceptance 方法 |
| `references/user-story-format.md` | `user-story.md` 与 `aef-story-card/v2` 字段、状态和引用合同 |
| `references/how-to-save-to-project.md` | 路径发现、双文件预览、非覆盖写入和下游路由 |
| `references/aef-integration.md` | AEF 未来消费 0.2.0 的边界 |
| `scripts/validate_story_card.py` | v1/v2 StoryCard 结构、状态、覆盖和引用校验 |
| `scripts/validate_story_package.py` | 双文件存在性、frontmatter 和 Story/Acceptance ID 一致性校验 |
| `examples/*/conversation.md` | 三个完整互动案例 |
| `examples/*/project-output/**` | 每个案例对应的双文件项目输出 |
| `tests/test_validate_story_card.py` | v1 兼容与 v2 数据合同回归 |
| `tests/test_validate_story_package.py` | 双文件一致性回归 |
| `tests/test_skill_contract.py` | 主 Skill 互动与 reference 路由回归 |
| `tests/test_examples.py` | 三个案例、两次确认、写入批准和输出校验 |

---

### Task 1: 用失败测试锁定 v2 StoryCard 合同

**Files:**

- Create: `tests/fixtures/valid-story-card-v2.json`
- Create: `tests/fixtures/invalid-story-card-v2.json`
- Modify: `tests/test_validate_story_card.py:1-34`
- Preserve: `tests/fixtures/valid-story-card.json`
- Preserve: `tests/fixtures/invalid-story-card.json`

**Interfaces:**

- Consumes: 当前 `validate_story_card(payload: dict) -> list[dict[str, str]]`。
- Produces: v2 fixture 字段合同，以及后续 `_validate_v2(payload)` 必须满足的断言。

- [ ] **Step 1: 写 v2 有效 fixture**

`valid-story-card-v2.json` 使用 `schema_version: aef-story-card/v2`，包含：

```json
{
  "schema_version": "aef-story-card/v2",
  "artifact_type": "aef-story-card",
  "package_id": "REQ-001",
  "status": "ready_for_spec",
  "source": {
    "summary": "用户希望点击逐字稿回到对应视频位置。",
    "facts": ["用户观看长视频"],
    "assumptions": ["第一版面向视频学习者"],
    "unknowns": ["首版视频来源范围"],
    "constraints": ["不锁定转写技术"]
  },
  "epic": {
    "epic_id": "EPIC-001",
    "title": "提升长视频学习效率",
    "status": "identified",
    "story_ids": ["US-001"]
  },
  "stories": [
    {
      "story_id": "US-001",
      "title": "点击逐字稿跳转视频",
      "actor": "视频学习者",
      "scenario": "阅读逐字稿时",
      "goal": "点击文字跳到对应视频位置",
      "value": "快速回看相关内容",
      "statement": "作为视频学习者，当我阅读逐字稿时，我希望点击文字跳到对应视频位置，从而快速回看相关内容。",
      "status": "approved",
      "invest_review": {
        "independent": {"status": "pass", "reason": "不依赖其他 Story"},
        "negotiable": {"status": "pass", "reason": "未锁定技术方案"},
        "valuable": {"status": "pass", "reason": "用户能快速回看内容"},
        "estimable": {"status": "pass", "reason": "范围和边界清楚"},
        "small": {"status": "pass", "reason": "只有一个用户结果"},
        "testable": {"status": "pass", "reason": "三类验收条件齐全"}
      },
      "acceptance_ids": ["AC-US-001-S", "AC-US-001-F", "AC-US-001-B"]
    }
  ],
  "acceptance": [
    {"acceptance_id": "AC-US-001-S", "story_id": "US-001", "type": "success", "given": "已有带时间戳逐字稿", "when": "点击文字", "then": "跳到对应时间"},
    {"acceptance_id": "AC-US-001-F", "story_id": "US-001", "type": "failure", "given": "解析失败", "when": "打开逐字稿", "then": "显示失败和重试入口"},
    {"acceptance_id": "AC-US-001-B", "story_id": "US-001", "type": "boundary", "given": "文字无时间戳", "when": "点击文字", "then": "不错误跳转并提示"}
  ],
  "scope": {"included": ["点击定位"], "excluded": ["全文搜索"]},
  "reviews": {
    "story": {"status": "approved", "confirmation": "explicit_user_confirmation", "change_summary": []},
    "acceptance": {"status": "approved", "confirmation": "explicit_user_confirmation", "change_summary": []}
  },
  "delivery": {"human_file": "./user-story.md", "machine_file": "./story-card.json"},
  "next_step": {
    "items": [
      {
        "route": "direct_spec",
        "reason": "需求和验收边界已经清楚",
        "capability": "spec-writing",
        "story_ids": ["US-001"],
        "target_id": "SPEC-US-001",
        "suggested_path": "docs/specs/SPEC-US-001.md",
        "required_acceptance_ids": ["AC-US-001-S", "AC-US-001-F", "AC-US-001-B"]
      }
    ]
  }
}
```

- [ ] **Step 2: 写 v2 无效 fixture**

从有效 fixture 派生并同时制造这些错误：缺 `valuable` INVEST 项、`testable.reason` 为空、Acceptance review 为 `draft`、缺 boundary Acceptance、Epic 引用 `US-404`、两个 next-step item 重复引用 `US-001`、next step 引用 `AC-MISSING`，同时顶层仍错误标记 `ready_for_spec`。

- [ ] **Step 3: 扩充单元测试**

在 `tests/test_validate_story_card.py` 增加：

```python
def load_fixture(name: str) -> dict:
    return json.loads((SKILL_ROOT / "tests" / "fixtures" / name).read_text(encoding="utf-8"))


class StoryCardV2Tests(unittest.TestCase):
    def test_v1_valid_fixture_remains_supported(self) -> None:
        self.assertEqual(MODULE.validate_story_card(load_fixture("valid-story-card.json")), [])

    def test_v2_valid_fixture_passes(self) -> None:
        self.assertEqual(MODULE.validate_story_card(load_fixture("valid-story-card-v2.json")), [])

    def test_v2_invalid_fixture_reports_all_new_contract_failures(self) -> None:
        errors = MODULE.validate_story_card(load_fixture("invalid-story-card-v2.json"))
        codes = {item["code"] for item in errors}
        self.assertTrue(
            {"missing_invest", "required_text", "illegal_transition", "missing_coverage", "dangling_reference", "duplicate_route"}.issubset(codes),
            errors,
        )

    def test_unknown_schema_is_rejected_without_falling_back_to_v1(self) -> None:
        payload = load_fixture("valid-story-card-v2.json")
        payload["schema_version"] = "aef-story-card/v999"
        errors = MODULE.validate_story_card(payload)
        self.assertEqual(errors[0]["code"], "unsupported_schema")
```

- [ ] **Step 4: 运行测试并确认 RED**

Run: `python3 tests/test_validate_story_card.py -v`

Expected: v1 测试继续 PASS；v2 有效 fixture FAIL，错误包含当前校验器只接受 `aef-story-card/v1`。

- [ ] **Step 5: 提交测试 RED**

```bash
git add tests/fixtures/valid-story-card-v2.json tests/fixtures/invalid-story-card-v2.json tests/test_validate_story_card.py
git commit -m "test: 锁定 StoryCard v2 合同"
```

---

### Task 2: 实现 v1/v2 StoryCard 校验

**Files:**

- Modify: `scripts/validate_story_card.py:12-252`
- Modify: `scripts/self_test.py:12-39`

**Interfaces:**

- Consumes: Task 1 的 v1/v2 fixtures。
- Produces: `validate_story_card(payload: object) -> list[dict[str, str]]`、`_validate_v1(payload: dict)`、`_validate_v2(payload: dict)`。

- [ ] **Step 1: 把当前 v1 实现原样移入 `_validate_v1`**

将当前 `validate_story_card` 的 v1 内容改名为：

```python
def _validate_v1(payload: dict[str, Any]) -> list[dict[str, str]]:
    """校验 aef-story-card/v1；保留 0.1.0 行为。"""
    # 当前第 56-252 行逻辑原样保留，schema_version 仍要求 v1。
```

不得删除 v1 的 `vertical_slice_review`、`selected_story_id` 或 `prd_handoff` 校验。

- [ ] **Step 2: 增加版本分发**

```python
def validate_story_card(payload: object) -> list[dict[str, str]]:
    if not isinstance(payload, dict):
        return [{"code": "invalid_type", "path": "$", "message": "顶层必须是对象"}]
    version = payload.get("schema_version")
    if version == "aef-story-card/v1":
        return _validate_v1(payload)
    if version == "aef-story-card/v2":
        return _validate_v2(payload)
    return [{
        "code": "unsupported_schema",
        "path": "schema_version",
        "message": "只支持 aef-story-card/v1 或 aef-story-card/v2",
    }]
```

- [ ] **Step 3: 实现 INVEST 校验 helper**

```python
INVEST_KEYS = {
    "independent", "negotiable", "valuable",
    "estimable", "small", "testable",
}
INVEST_STATUSES = {"pass", "risk", "fail"}


def _validate_invest(review: object, base: str, errors: list[dict[str, str]]) -> bool:
    if not isinstance(review, dict):
        _add(errors, "invalid_type", base, "必须是对象")
        return False
    all_pass = True
    for key in sorted(INVEST_KEYS):
        if key not in review:
            _add(errors, "missing_invest", f"{base}.{key}", "缺少 INVEST 项")
            all_pass = False
            continue
        item = review[key]
        if not isinstance(item, dict):
            _add(errors, "invalid_type", f"{base}.{key}", "必须是对象")
            all_pass = False
            continue
        status = item.get("status")
        if status not in INVEST_STATUSES:
            _add(errors, "invalid_enum", f"{base}.{key}.status", "INVEST 状态无效")
            all_pass = False
        if status != "pass":
            all_pass = False
        _require_text(item.get("reason"), f"{base}.{key}.reason", errors)
    return all_pass
```

- [ ] **Step 4: 实现 `_validate_v2`**

完整校验顺序固定为：顶层字段 → source 数组 → epic/story 引用 → Story 字段与 INVEST → Acceptance ID/类型/覆盖 → reviews 状态 → delivery → next-step items → `ready_for_spec` 门禁。

`next_step.items` 校验规则：

```python
ROUTES = {"direct_spec", "prd", "backlog", "specialist_review"}

# 每个 item 必填 route/reason/capability/story_ids/target_id/
# suggested_path/required_acceptance_ids。
# direct_spec 的 story_ids 长度必须等于 1。
# 当前范围 approved Story 必须且只能出现在一个 item 中。
# item 中 Story/Acceptance 必须存在，且 Acceptance 属于引用 Story。
```

`ready_for_spec` 时额外要求：所有当前路由为 `direct_spec`、Story/Acceptance reviews 均 approved、所有 approved Story 的 INVEST 全 pass、三类 Acceptance 齐全、Epic 本身没有作为 Story 出现在 route 中。

- [ ] **Step 5: 更新聚合自测**

`scripts/self_test.py` 同时加载 `valid-story-card.json`、`valid-story-card-v2.json` 和 `invalid-story-card-v2.json`，新增 keys：

```python
checks.update({
    "valid_v1_story_card_passes": not validate_story_card(valid_v1),
    "valid_v2_story_card_passes": not validate_story_card(valid_v2),
    "invalid_v2_story_card_fails": bool(invalid_v2_errors),
    "v2_invest_and_route_failures_reported": {
        "missing_invest", "duplicate_route", "illegal_transition"
    }.issubset({item["code"] for item in invalid_v2_errors}),
})
```

- [ ] **Step 6: 运行 GREEN 和回归**

Run: `python3 tests/test_validate_story_card.py -v`

Expected: 全部 PASS。

Run: `python3 scripts/self_test.py`

Expected: JSON 中 `"ok": true`，v1/v2 keys 均为 true。

- [ ] **Step 7: 提交校验器**

```bash
git add scripts/validate_story_card.py scripts/self_test.py
git commit -m "feat: 支持 StoryCard v2 与 INVEST 校验"
```

---

### Task 3: 实现双文件需求包一致性校验

**Files:**

- Create: `scripts/validate_story_package.py`
- Create: `tests/test_validate_story_package.py`
- Create: `tests/fixtures/packages/valid/user-story.md`
- Create: `tests/fixtures/packages/valid/story-card.json`
- Create: `tests/fixtures/packages/mismatched/user-story.md`
- Create: `tests/fixtures/packages/mismatched/story-card.json`

**Interfaces:**

- Consumes: `validate_story_card(payload)`。
- Produces: `validate_story_package(package_dir: Path) -> list[dict[str, str]]` 和 CLI `validate_story_package.py <directory> [--json]`。

- [ ] **Step 1: 先写失败测试**

```python
class StoryPackageValidatorTests(unittest.TestCase):
    def test_valid_package_passes(self) -> None:
        self.assertEqual(MODULE.validate_story_package(FIXTURES / "valid"), [])

    def test_mismatched_markdown_and_json_ids_fail(self) -> None:
        errors = MODULE.validate_story_package(FIXTURES / "mismatched")
        codes = {item["code"] for item in errors}
        self.assertIn("package_id_mismatch", codes)
        self.assertIn("story_id_mismatch", codes)
        self.assertIn("acceptance_id_mismatch", codes)

    def test_missing_human_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as name:
            errors = MODULE.validate_story_package(Path(name))
        self.assertTrue(any(item["path"] == "user-story.md" for item in errors))
```

- [ ] **Step 2: 运行测试确认 RED**

Run: `python3 tests/test_validate_story_package.py -v`

Expected: ERROR，因为 `scripts/validate_story_package.py` 不存在。

- [ ] **Step 3: 实现无第三方依赖校验器**

实现常量和接口：

```python
FRONTMATTER_PATTERN = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
STORY_PATTERN = re.compile(r"^###\s+(US-\d+)[:：]", re.MULTILINE)
ACCEPTANCE_PATTERN = re.compile(r"^###\s+(AC-US-\d+-(?:S|F|B)\d*)[:：]", re.MULTILINE)


def _parse_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_PATTERN.search(text)
    if not match:
        return {}
    result: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    return result


def validate_story_package(package_dir: Path) -> list[dict[str, str]]:
    # 1. 要求 user-story.md 和 story-card.json 都存在；
    # 2. 调用 validate_story_card；
    # 3. 比较 frontmatter package_id；
    # 4. 比较 Markdown 标题与 JSON 中 Story/Acceptance ID 集合；
    # 5. 检查 delivery.human_file/machine_file 使用相对文件名。
```

CLI 退出码与 StoryCard 校验器一致：0 有效、1 合同错误、2 用法/读取错误。

- [ ] **Step 4: 运行 GREEN**

Run: `python3 tests/test_validate_story_package.py -v`

Expected: 全部 PASS。

- [ ] **Step 5: 提交双文件校验器**

```bash
git add scripts/validate_story_package.py tests/test_validate_story_package.py tests/fixtures/packages
git commit -m "feat: 校验 User Story 双文件需求包"
```

---

### Task 4: 用失败测试锁定主 Skill 的互动行为

**Files:**

- Create: `tests/test_skill_contract.py`
- Modify: `SKILL.md:1-128`
- Create: `references/how-to-write-user-story.md`
- Create: `references/user-story-format.md`
- Create: `references/how-to-save-to-project.md`
- Modify: `references/aef-integration.md:1-42`
- Explicitly delete after replacement: `references/story-shaping-standard.md`
- Explicitly delete after replacement: `references/story-card-contract.md`
- Modify: `skill.contract.yaml:1-111`

**Interfaces:**

- Consumes: 设计文档和 Task 2/3 的 v2 接口。
- Produces: 可发现、可执行的互动状态机和三个职责单一的 reference。

- [ ] **Step 1: 写静态行为合同测试**

```python
class SkillContractTests(unittest.TestCase):
    def test_main_skill_contains_all_three_approval_gates(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("User Story 修改循环", "User Story 明确确认", "验收条件修改循环", "验收条件明确确认", "写入预览", "写入批准"):
            self.assertIn(phrase, text)

    def test_main_skill_tells_user_available_edits(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("修改某一条", "拆分某一条", "合并两条", "增加遗漏 Story", "暂缓某一条"):
            self.assertIn(phrase, text)

    def test_plain_language_references_exist_and_are_routed(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for name in ("how-to-write-user-story.md", "user-story-format.md", "how-to-save-to-project.md"):
            self.assertTrue((ROOT / "references" / name).is_file())
            self.assertIn(name, text)

    def test_v2_skill_does_not_make_prd_or_story_points_mandatory(self) -> None:
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("PRD 是可选路径", text)
        self.assertIn("不计算 Story Points", text)
        self.assertNotIn("### 3. 选择首个垂直切片", text)
```

- [ ] **Step 2: 运行测试确认 RED**

Run: `python3 tests/test_skill_contract.py -v`

Expected: FAIL，缺少三个新 reference、修改循环和写入批准措辞。

- [ ] **Step 3: 重写主 Skill 为薄入口**

`SKILL.md` 固定章节：适用/不适用 → 输入与安全 → 资源路由 → 需求复述 → Epic/Story 与 INVEST → User Story 修改循环 → Story Gate → Acceptance 修改循环 → Acceptance Gate → 写入预览与批准 → 下游路由 → 校验 → 完成条件。

Story Gate 必须原样包含用户可选动作：确认全部、修改某一条、拆分某一条、合并两条、增加遗漏 Story、暂缓某一条、调整范围或顺序。

Acceptance Gate 必须说明：修改 Story 会使关联 Acceptance 失效；只为 confirmed Story 生成 success/failure/boundary；技术任务不是 Acceptance。

- [ ] **Step 4: 写三份直白 reference**

`how-to-write-user-story.md` 必须包含：3C、输入分类、Epic/Story、标准句式、INVEST 六项定义与证据、Acceptance 方法、常见错误。垂直切片只在 `Valuable` 辅助说明中出现一次。

`user-story-format.md` 必须完整列出 `user-story.md` 九段结构、`aef-story-card/v2` 字段、reviews 状态、next-step items 和 v1/v2 迁移。

`how-to-save-to-project.md` 必须包含：现有规范发现顺序、默认路径、双文件预览、明确批准、冲突停止、写后校验、四种 route 和下游能力钩子。

- [ ] **Step 5: 更新合同并显式删除被替换 reference**

`skill.contract.yaml` 版本改为 `0.2.0`；输出改为 `story_package`、`story_card_v2`、`next_step`；delegate 改为 capability-based `downstream_requirement_skill`；增加 `project_write_preview` stop；测试命令列出四个 unittest 文件。

确认新 reference 已完成并通过静态测试后，显式执行：

```bash
git rm references/story-shaping-standard.md references/story-card-contract.md
```

- [ ] **Step 6: 运行 GREEN 与内容门禁**

Run: `python3 tests/test_skill_contract.py -v`

Expected: 全部 PASS。

Run: `python3 /Users/aim5/.codex/skills/skill-engineering/scripts/content_gate.py . --json`

Expected: `status: pass`，无断链 reference。

- [ ] **Step 7: 提交主 Skill 与 reference**

```bash
git add SKILL.md skill.contract.yaml references/how-to-write-user-story.md references/user-story-format.md references/how-to-save-to-project.md references/aef-integration.md tests/test_skill_contract.py
git add -u references/story-shaping-standard.md references/story-card-contract.md
git commit -m "feat: 增加 User Story 互动与项目落盘合同"
```

---

### Task 5: 用三个完整案例验证互动和双文件输出

**Files:**

- Create: `tests/test_examples.py`
- Create: `examples/01-video-transcript-jump/conversation.md`
- Create: `examples/01-video-transcript-jump/project-output/docs/requirements/video-transcript-jump/{user-story.md,story-card.json}`
- Create: `examples/02-ai-meeting-assistant/conversation.md`
- Create: `examples/02-ai-meeting-assistant/project-output/docs/requirements/ai-meeting-assistant/{user-story.md,story-card.json}`
- Create: `examples/03-ai-content-workflow/conversation.md`
- Create: `examples/03-ai-content-workflow/project-output/docs/requirements/ai-content-workflow/{user-story.md,story-card.json}`

**Interfaces:**

- Consumes: `validate_story_package(package_dir)` 和 Task 4 的对话合同。
- Produces: 三个可读案例和六个可复用输出文件。

- [ ] **Step 1: 先写案例合同测试**

```python
CASES = {
    "01-video-transcript-jump": "direct_spec",
    "02-ai-meeting-assistant": "prd",
    "03-ai-content-workflow": "direct_spec",
}


class ExampleTests(unittest.TestCase):
    def test_every_conversation_contains_interaction_and_write_approval(self) -> None:
        markers = (
            "## 用户原始需求", "## Agent 复述", "## 澄清问题",
            "## User Story 修改", "## User Story 确认",
            "## 验收条件修改", "## 验收条件确认",
            "## 写入预览", "## 用户批准写入", "## 下游钩子",
        )
        for case in CASES:
            text = (ROOT / "examples" / case / "conversation.md").read_text(encoding="utf-8")
            for marker in markers:
                self.assertIn(marker, text, (case, marker))

    def test_every_project_output_is_a_valid_package(self) -> None:
        for case in CASES:
            packages = list((ROOT / "examples" / case / "project-output" / "docs" / "requirements").iterdir())
            self.assertEqual(len(packages), 1)
            self.assertEqual(PACKAGE_MODULE.validate_story_package(packages[0]), [])

    def test_expected_route_is_present(self) -> None:
        for case, route in CASES.items():
            card = next((ROOT / "examples" / case / "project-output").rglob("story-card.json"))
            payload = json.loads(card.read_text(encoding="utf-8"))
            self.assertIn(route, {item["route"] for item in payload["next_step"]["items"]})
```

- [ ] **Step 2: 运行测试确认 RED**

Run: `python3 tests/test_examples.py -v`

Expected: ERROR/FAIL，因为 examples 尚不存在。

- [ ] **Step 3: 写案例一完整对话和输出**

对话必须真实展示 actor 从“视频用户”修改为“视频学习者”，boundary Acceptance 从“只提示”修改为“提示并提供重新解析入口”，然后两次确认和写入批准。输出一条 `US-001`，route 为 `direct_spec`，target 为 `SPEC-US-001`。

- [ ] **Step 4: 写案例二完整对话和输出**

对话从录音/转写/总结/任务/搜索/分享/权限混合输入开始，识别 Epic，形成至少六条候选 Story。用户把“自动分配任务”改为“组织者确认后发布”，当前范围选择 US-001/US-003/US-004，其余 deferred；每条当前 Story 都有三类 Acceptance，route 为单个 `prd` item 并引用三条 Story。

- [ ] **Step 5: 写案例三完整对话和输出**

对话展示原 Story 的 INVEST 初评：I/E/S/T 不通过、V 有风险；拆成选题、写作、配图、审核、发布；用户说明没有独立审核者，于是移除审核 Story，并把发布前本人确认写入 Acceptance。每条当前 approved Story 使用独立 `direct_spec` item 和不同 `SPEC-US-*`。

- [ ] **Step 6: 运行 GREEN**

Run: `python3 tests/test_examples.py -v`

Expected: 三项测试全部 PASS。

Run: `python3 scripts/validate_story_package.py examples/01-video-transcript-jump/project-output/docs/requirements/video-transcript-jump --json`

Expected: `valid: true`。

- [ ] **Step 7: 提交案例**

```bash
git add examples tests/test_examples.py
git commit -m "docs: 增加三个完整 User Story 对话案例"
```

---

### Task 6: 更新公开说明、自测清单和版本记录

**Files:**

- Modify: `README.md:1-51`
- Modify: `CHANGELOG.md:1-14`
- Modify: `tests/self-test.json:1-31`
- Modify: `tests/baseline.json`

**Interfaces:**

- Consumes: Tasks 1-5 的稳定入口与案例。
- Produces: 0.2.0 用户说明和 Portable Self Test 声明。

- [ ] **Step 1: 更新 README**

README 必须用中文解释：三个触发例、INVEST、两次修改确认、默认项目目录、双文件、PRD 可选、四种 next route、两个校验命令和 examples 索引。不写 Story Points。

- [ ] **Step 2: 更新 CHANGELOG**

新增 `## [0.2.0] - 2026-08-25`，按“新增/变更/兼容”记录互动循环、v2、双文件、三个案例和 v1 validator 兼容；把 0.1.0 现有英文条目翻译成中文，但不改历史含义。

- [ ] **Step 3: 更新自测清单**

`tests/self-test.json` 增加 `scripts/validate_story_package.py` 的无参数安全失败条目，并在 `scripts/self_test.py` 条目中加入 v2 checks keys。Portable runner 不支持参数，所以 package 脚本直接条目预期退出 2 且 stdout 包含 `[usage]`。

- [ ] **Step 4: 保持诚实基线**

`tests/baseline.json` 仍标记 `baseline_pending`，增加说明：0.2.0 三案例作者上下文测试不等于独立 baseline，不能把结构测试包装成效用证明。

- [ ] **Step 5: 运行全部确定性测试**

```bash
python3 tests/test_validate_story_card.py -v
python3 tests/test_validate_story_package.py -v
python3 tests/test_skill_contract.py -v
python3 tests/test_examples.py -v
python3 scripts/self_test.py
```

Expected: 全部 PASS，聚合自测 `"ok": true`。

- [ ] **Step 6: 提交发布文档**

```bash
git add README.md CHANGELOG.md tests/self-test.json tests/baseline.json
git commit -m "docs: 更新 aef-user-story 0.2.0 说明"
```

---

### Task 7: 生产门禁、真实检查和发布

**Files:**

- Create: `docs/superpowers/testing/2026-08-25-user-story-v0.2-test-report.md`
- Modify: `docs/superpowers/plans/2026-08-25-user-story-examples-and-project-delivery-plan.md`

**Interfaces:**

- Consumes: 0.2.0 完整候选。
- Produces: 可审计验证证据、干净本地提交和经批准的远程发布。

- [ ] **Step 1: 运行内容与创建门禁**

```bash
python3 /Users/aim5/.codex/skills/skill-engineering/scripts/content_gate.py . --json
python3 /Users/aim5/.codex/skills/skill-engineering/scripts/creation_review.py . --profile production --json
python3 /Users/aim5/.codex/skills/skill-engineering/scripts/skill_self_test.py . --json
```

Expected: Content Gate pass；Production Review 100/A 或无阻断 finding；Portable Self Test pass 且 `target_unchanged: true`。

- [ ] **Step 2: 运行公开内容扫描**

Run: `rg -n '<占位词>|T[B]D|待[补]|/Users/aim5|CodingProject|训练营第|课程第|story_points|suggested_points|points:' SKILL.md README.md references examples`

Expected: 零命中；设计/计划和命令示例不在公开 Skill 内容扫描范围。

- [ ] **Step 3: 写测试报告**

分别记录：v1 兼容、v2 结构、双文件一致性、三个对话案例、内容门禁、production review、portable self-test、未完成的独立效用基线。不得把三个作者编写案例标为独立 rollout。

- [ ] **Step 4: 显式提交验证文档**

```bash
git add docs/superpowers/testing/2026-08-25-user-story-v0.2-test-report.md docs/superpowers/plans/2026-08-25-user-story-examples-and-project-delivery-plan.md docs/superpowers/specs/2026-08-25-user-story-examples-and-project-delivery-design.md
git commit -m "test: 记录 aef-user-story 0.2.0 验证证据"
```

- [ ] **Step 5: 检查本地发布状态**

```bash
git status --short --branch
git log -7 --oneline
```

Expected: 工作区干净，`main` 领先 `origin/main`，提交按测试→实现→案例→文档→验证排列。

- [ ] **Step 6: 停止并让用户检查本地版本**

向用户提供本地 `SKILL.md`、三份 reference、三个 conversation 和三个项目输出的可点击路径。用户未明确确认前不 push。

- [ ] **Step 7: 经确认后 push 并核验**

```bash
git push origin main
git ls-remote origin refs/heads/main
gh api repos/wukongai/aef-user-story/contents/SKILL.md --jq '{html_url: .html_url, raw_url: .download_url, sha: .sha}'
```

Expected: 远程 main 与本地 HEAD 相同，线上 SKILL 和 Raw 地址可访问。

- [ ] **Step 8: 远程安装验证**

在 `mktemp -d` 创建的空目录运行：

```bash
npx skills add wukongai/aef-user-story
```

Expected: 只发现并可安装 `aef-user-story`；记录 CLI 版本、安装范围和结果，不把临时安装目录提交到仓库。
