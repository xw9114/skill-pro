# 输出契约

本文件定义 `reports/PAPER_EVALUATION_REPORT.md` 和 `reports/contracts/paper_evaluation.json` 的最小结构。

## 一、Markdown 报告结构

```markdown
# PAPER_EVALUATION_REPORT

## 1. Executive Summary
- competition_profile
- review_mode
- retrieval_date
- task_coverage 概览
- official_compliance.overall
- official_compliance.compliance_blocked
- quality_blocked
- submission_blocked
- overall_verdict
- provisional_score 或 final_score
- score_coverage
- confidence.level

## 2. Task Coverage
| task_id | task_label | status | problem_ref | paper_refs | evidence_refs | notes |
| --- | --- | --- | --- | --- | --- | --- |

## 3. Official Compliance Checks
| check_id | result | rule_source_ids | evidence_refs | notes |
| --- | --- | --- | --- | --- |

## 4. Quality Blockers
| issue_id | severity | related_dimensions | evidence_refs | notes |
| --- | --- | --- | --- | --- |

## 5. Dimension Scores
| dimension_id | weight | rating | points_awarded | evidence_refs | summary |
| --- | --- | --- | --- | --- | --- |

## 6. Priority Fixes
| priority | title | severity | expected_gain | evidence_refs |
| --- | --- | --- | --- | --- |

## 7. Evidence Gaps and Timing Risks
- 缺失的题面、代码、结果、附件
- 不能强判的规则项
- 来源版本与时效风险
```

## 二、JSON 顶层字段

以下字段最少都要出现：

- `review_mode`
- `competition_profile`
- `retrieval_date`
- `rubric`
- `sources`
- `artifacts`
- `evidence_completeness`
- `task_coverage`
- `official_compliance`
- `quality_blockers`
- `dimension_scores`
- `score_coverage`
- `provisional_score` 或 `final_score`
- `quality_blocked`
- `submission_blocked`
- `overall_verdict`
- `confidence`
- `priority_fixes`

## 三、JSON 结构约定

### 1. `review_mode`

- `formal`：论文、题面/任务、竞赛名称和年份均可确认。
- `preliminary`：至少一项正式评审输入不完整，只能做预审。

`preliminary` 模式下不得输出 `final_score`；脚本会保留或生成 `provisional_score`。

`formal` 模式下，`evidence_completeness.paper` 和 `evidence_completeness.problem` 不能是 `missing` 或 `unknown`。

### 2. `competition_profile`

```json
{
  "profile_id": "cumcm-2026",
  "competition": "CUMCM",
  "year": 2026,
  "rule_mode": "current_official"
}
```

### 3. `rubric`

```json
{
  "id": "evaluate-math-modeling-paper-v1",
  "origin": "skill_composite",
  "official_weight_available": false
}
```

说明：
- 本 skill 的 100 分权重不是赛事官方评分表。
- 当官方未公开统一数值权重时，必须保持 `official_weight_available = false`。

### 4. `sources`

列表项最少包含：

- `id`
- `title`
- `authority`
- `source_mode`: `url` / `user_file` / `manual_note`
- `url`: `source_mode = url` 时必填；其他模式可为空或省略
- `local_path`: `source_mode = user_file` 时必填
- `sha256`: 用户本地文件建议填写
- `category`: `official_rule` / `official_guidance` / `educational_rubric` / `user_provided_current_rule`
- `document_version`
- `applies_to_year`
- `retrieved_at`

`id` 必须可被其他字段引用。用户提供的本地规则应使用 `source_mode = user_file`，并尽量记录 `local_path` 与 `sha256`。

### 5. `artifacts`

```json
[
  {
    "id": "paper-main",
    "kind": "paper",
    "status": "complete",
    "path": "D:/paper.pdf",
    "sha256": "optional",
    "notes": "已提取正文和页码。"
  }
]
```

说明：
- `kind` 只允许 `paper` / `problem` / `results` / `code` / `attachments`。
- `status` 使用 `complete` / `partial` / `minimal` / `missing` / `unknown`。
- 工件缺失时也要登记一条 `status = missing` 的记录，便于解释证据边界。
- 五类 `kind` 都必须至少出现一次，缺失工件用 `status = missing` 登记。

### 6. `evidence_completeness`

```json
{
  "paper": "complete",
  "problem": "complete",
  "results": "partial",
  "code": "missing",
  "attachments": "missing",
  "notes": "只收到论文和题面，结果记录不完整。"
}
```

状态值：`complete` / `partial` / `minimal` / `missing` / `unknown`。

若某类证据为 `missing`，该类证据引用只能写成 `<family>:missing`，例如 `code:missing`；不得伪造具体路径或页码。

### 7. `task_coverage`

```json
[
  {
    "task_id": "q1",
    "task_label": "任务一",
    "status": "evidenced",
    "problem_ref": "problem:q1",
    "paper_refs": ["paper:summary", "paper:sec-4.1"],
    "body_evidence_refs": ["paper:sec-4.1", "results:table-q1"],
    "validation_evidence_refs": [],
    "evidence_refs": ["paper:sec-4.1", "results:table-q1"],
    "notes": "摘要提到任务，正文给出方法和结果表。"
  }
]
```

说明：
- 必须按题面顶层任务逐项填写，不能合并成一条笼统结论。
- `status` 只允许 `mentioned` / `answered` / `evidenced` / `validated`，并且语义严格递进。
- `problem_ref` 必须引用单个题面顶层任务，例如 `problem:q1`。
- `paper_refs` 只允许引用论文位置，且 `status >= answered` 时必须包含正文位置。
- `body_evidence_refs`：
  - `mentioned` / `answered` 时必须为空列表
  - `evidenced` / `validated` 时必须非空
  - 若引用 `paper:*`，不能只落在摘要、总述、`summary-sheet`、`executive-summary`、`abstract` 等非正文定位
- `validation_evidence_refs`：
  - 仅 `validated` 时允许非空
  - `validated` 时必须非空
  - 每条 locator 都必须显式体现 `validation` / `robustness` / `sensitivity` / `backtest` / `error` / `constraint-check` 等验证语义
- `evidence_refs` 必须是列表：
  - 必须按顺序等于 `body_evidence_refs + validation_evidence_refs`
  - `mentioned` / `answered` 时因此也必须为空列表
- 摘要、总述、`summary-sheet`、`executive-summary`、`abstract` 等定位，不能代替正文 `paper_refs`、`body_evidence_refs` 或 `validation_evidence_refs`。

### 8. `official_compliance`

```json
{
  "checks": [
    {
      "id": "anonymous",
      "label": "匿名性",
      "status": "PASS",
      "rule_source_ids": ["CUMCM-2026-FORMAT"],
      "evidence_refs": ["paper:p1"],
      "notes": "首页未出现队伍身份。"
    }
  ]
}
```

说明：
- `overall` 和 `compliance_blocked` 由 `scripts/score_evaluation.py` 计算后输出到 stdout 中的 JSON。
- `status` 只允许 `PASS` / `FAIL` / `UNKNOWN`。

### 9. `quality_blockers`

```json
[
  {
    "id": "missing-validation",
    "severity": "MAJOR",
    "summary": "缺少有效验证。",
    "dimension_ids": ["validation_sensitivity_robustness"],
    "evidence_refs": ["paper:sec-5"],
    "source_ids": ["COMAP-TIPS"]
  }
]
```

任一 `severity = BLOCKER` 会使脚本输出 `quality_blocked = true`。

### 10. `dimension_scores`

`dimension_scores` 必须是对象，且 key 必须严格等于这 10 个维度 ID：

- `summary_and_task_coverage`
- `problem_understanding`
- `assumptions_data_variables_units`
- `model_and_mathematical_correctness`
- `computation_and_reproducibility`
- `results_and_interpretation`
- `validation_sensitivity_robustness`
- `limitations_applicability_improvement`
- `writing_organization_figures_citations`
- `innovation_and_insight`

每个维度最少结构：

```json
{
  "weight": 10,
  "rating": 4,
  "rationale": "摘要覆盖主要任务和关键结果，但还可以更凝练。",
  "evidence_refs": ["paper:p1", "paper:sec-6"],
  "source_ids": ["COMAP-TIPS"]
}
```

说明：
- `rating` 只允许整数 `0` 到 `5`，或字符串 `NOT_ASSESSABLE`。
- `weight` 必须与 rubric 固定权重一致。
- `points_awarded` 由脚本计算后输出到 stdout 中的 JSON。
- 脚本会按 `task_coverage` 做确定性封顶：
  - 任一任务仅为 `mentioned` 时，`results_and_interpretation <= 1`
  - 不存在 `mentioned` 但任一任务仅为 `answered` 时，`results_and_interpretation <= 2`
  - 任一任务未到 `validated` 时，`validation_sensitivity_robustness <= 3`

### 11. `confidence`

```json
{
  "level": "medium",
  "notes": "缺少代码和完整结果文件，因此无法对可复现性做强判断。",
  "evidence_refs": ["results:missing", "code:missing"]
}
```

### 12. `priority_fixes`

```json
[
  {
    "id": "fix-summary-coverage",
    "priority": 1,
    "title": "补强摘要对全部子任务的覆盖",
    "severity": "MAJOR",
    "expected_gain": "提高摘要完成度并减少审稿人误判。",
    "evidence_refs": ["paper:p1", "problem:q3"],
    "source_ids": ["COMAP-TIPS"],
    "related_dimensions": ["summary_and_task_coverage"]
  }
]
```

说明：
- `priority` 只允许 `1` 到 `3`，分别表示最高、中等、较低优先级。

## 四、脚本计算字段

运行 `scripts/score_evaluation.py` 后，stdout 输出的 JSON 会补充或覆盖以下字段：

- `official_compliance.overall`
- `official_compliance.compliance_blocked`
- `dimension_scores.*.points_awarded`
- `assessed_weight`
- `score_coverage`
- `provisional_score` 或 `final_score`
- `quality_blocked`
- `submission_blocked`
- `overall_verdict`

阻断规则：
- 任一任务低于 `evidenced` 时，脚本会置 `quality_blocked = true`。
- `review_mode = preliminary` 时，脚本会置 `submission_blocked = true`，但不会把预审状态改写成官方 `FAIL` 或内容 `BLOCKER`。

`overall_verdict` 只允许：

- `BLOCKED_COMPLIANCE_AND_QUALITY`
- `BLOCKED_COMPLIANCE`
- `BLOCKED_QUALITY`
- `PRELIMINARY`
- `REVIEWED`

脚本不会原地改写输入文件；若需要落盘，调用方应使用重定向，或先写入临时文件后再替换目标 JSON。

## 五、建议的证据引用格式

- 论文：`paper:p12`、`paper:sec-4.2`
- 题面：`problem:q1`
- 附件：`attachments:a2`
- 结果：`results:all_results.json#q1.metric`
- 代码：`code:src/main.py#L10`
- 规则：`rule:CUMCM-2026-FORMAT`
- 缺失：`code:missing`、`results:missing`
