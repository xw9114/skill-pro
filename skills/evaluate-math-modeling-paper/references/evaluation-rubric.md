# 综合评审 Rubric

本文件定义的是 **本 skill 的综合量化设计**，不是任何赛事官方评分表。

## 一、三类标准必须分开

- **官方硬门槛/规则**：只判 `PASS` / `FAIL` / `UNKNOWN`
- **官方定性评审维度**：用于说明为什么某维度重要
- **本 skill 综合量化权重**：仅用于复现性综合评分

## 二、证据规则

- 每个维度评分必须至少带一条 `evidence_refs`
- 需要引用规则时再带 `source_ids`
- `task_coverage` 必须按题面顶层任务逐项记录 `mentioned` / `answered` / `evidenced` / `validated`
- 摘要、总述、`summary-sheet`、`executive-summary`、`abstract` 等定位，不能替代正文 `paper_refs`、`body_evidence_refs` 或 `validation_evidence_refs`
- 没有证据时：
  - 不要硬打分
  - 用 `NOT_ASSESSABLE`
  - 同时降低 `confidence`

## 三、任务覆盖状态

| 状态 | 最低要求 |
| --- | --- |
| `mentioned` | 任务被提到，但没有正文回答，也没有可追溯证据 |
| `answered` | 正文已回答任务，但没有 `body_evidence_refs` |
| `evidenced` | 正文已回答任务，且有 `body_evidence_refs` |
| `validated` | 在 `evidenced` 基础上，还有 `validation_evidence_refs`，且定位显式体现验证语义 |

任一任务低于 `evidenced` 时，稿件不能解释为可提交。

## 四、档位定义

| 档位 | 含义 |
| --- | --- |
| `5` | 证据充分、结构完整、论证严密，达到该维度的强表现 |
| `4` | 总体很强，只有轻微缺口，不影响主结论可信度 |
| `3` | 基本达标，能支撑主要论点，但存在明显补强空间 |
| `2` | 不完整或偏弱，主张能看出方向，但支撑不足 |
| `1` | 严重不足，存在明显缺项、逻辑断裂或方法不当 |
| `0` | 缺失、明显错误、与题目要求冲突，或证据显示结论站不住 |
| `NOT_ASSESSABLE` | 输入不足，无法负责任地判断该维度 |

## 五、100 分综合权重

| dimension_id | 权重 |
| --- | --- |
| `summary_and_task_coverage` | 10 |
| `problem_understanding` | 10 |
| `assumptions_data_variables_units` | 10 |
| `model_and_mathematical_correctness` | 20 |
| `computation_and_reproducibility` | 10 |
| `results_and_interpretation` | 15 |
| `validation_sensitivity_robustness` | 10 |
| `limitations_applicability_improvement` | 5 |
| `writing_organization_figures_citations` | 5 |
| `innovation_and_insight` | 5 |

## 六、维度锚点

### 1. `summary_and_task_coverage` (10)

- `5`：摘要或 Summary Sheet 覆盖全部子任务、核心方法、关键数值结果和主要结论，且能回溯到正文
- `3`：覆盖主要任务，但至少缺少一个子任务、关键结果或方法亮点
- `1`：主要是题目复述，缺少关键结果或摘要不能独立传达方案
- `0`：缺失摘要页，或摘要与正文明显不一致

### 2. `problem_understanding` (10)

- `5`：准确重述任务、约束、目标和评价口径，能解释任务之间的关系
- `3`：基本理解题意，但约束或目标有遗漏，问题拆解不够清楚
- `1`：存在明显误读、错拆题或把背景描述当主要任务
- `0`：核心任务理解错误，导致后续建模方向失真

### 3. `assumptions_data_variables_units` (10)

- `5`：关键假设必要且可解释，数据来源清楚，变量/参数/单位完整一致
- `3`：有基本假设和符号说明，但单位、边界或数据处理说明不够完整
- `1`：假设堆砌、变量未定义、单位混乱或数据口径不清
- `0`：关键变量、单位或数据设定错误到足以破坏结果解释

### 4. `model_and_mathematical_correctness` (20)

- `5`：模型结构、数学表达、约束和求解逻辑一致，推导或方法选择站得住
- `3`：主模型可理解且大体合理，但存在未解释跳步、方法匹配度一般或局部公式不严密
- `1`：模型与问题不匹配，关键公式、约束或推理链薄弱
- `0`：核心数学结构明显错误，无法支撑主要结论

### 5. `computation_and_reproducibility` (10)

- `5`：计算流程清楚，可追溯到代码/结果文件，关键参数和运行口径透明
- `3`：能看出计算路径，但参数、数据处理或复现实操信息不完整
- `1`：只给结果，不交代算法细节、参数或代码证据
- `0`：已有证据表明结果与支撑材料不一致，或必要代码明显缺失

### 6. `results_and_interpretation` (15)

- `5`：结果完整、数值可追溯，解释到业务/场景含义，能回答题目要求
- `3`：给出了主要结果，但解释偏薄或只停留在数值层
- `1`：结果片段化、缺少对任务的闭环回答
- `0`：结果与问题无关、明显冲突或无法回溯
- 若任一任务仅为 `mentioned`，该维度脚本封顶 `1`
- 若不存在 `mentioned` 但任一任务仅为 `answered`，该维度脚本封顶 `2`

### 7. `validation_sensitivity_robustness` (10)

- `5`：有有效的验证、误差分析、敏感性或稳健性检验，并讨论影响
- `3`：有基础验证，但不系统，或只有单一检验
- `1`：仅口头声称模型有效，没有实证支撑
- `0`：缺失验证，且已有证据表明结论对关键假设高度脆弱
- 若任一任务未到 `validated`，该维度脚本封顶 `3`

### 8. `limitations_applicability_improvement` (5)

- `5`：明确交代局限、适用边界和有针对性的改进方向
- `3`：提到局限或改进，但比较泛
- `1`：只写套话，没有对应模型实际弱点
- `0`：完全缺失，或声称模型普适或完美而无保留

### 9. `writing_organization_figures_citations` (5)

- `5`：结构清楚、图表服务论证、引用规范且无明显信息泄露
- `3`：整体可读，但局部组织松散、图表解释不足或引用偏弱
- `1`：堆图堆表、叙述跳跃、图表和文字脱节或引用混乱
- `0`：匿名性、引用诚信或基本写作规范存在严重问题

### 10. `innovation_and_insight` (5)

- `5`：方法组合、洞察或推广性有明显增量，不只是教材式套模
- `3`：有一定选择与整合，但创新度一般
- `1`：几乎纯模板化套用，缺少思考痕迹
- `0`：所谓创新与题目无关，或建立在错误前提上

## 七、合规与内容问题分层

### 官方规则状态

- `PASS`：有证据支持满足当前适用规则
- `FAIL`：有证据支持违反当前适用规则
- `UNKNOWN`：规则、材料或证据不足，不能强判

### 内容问题严重级别

- `BLOCKER`：足以阻断提交或使主结论不可信
- `MAJOR`：显著影响质量，但仍可通过定向修订修复
- `MINOR`：局部改进项，不改也未必阻断整体判断

## 八、置信度规则

| level | 适用情形 |
| --- | --- |
| `high` | 论文、题面、结果、代码、必要附件基本齐全，主要结论有交叉证据 |
| `medium` | 论文和题面齐全，但代码、结果或附件缺失一部分 |
| `low` | 只有论文或论文加题面，无法验证多项关键主张 |

## 九、计分规则

- `points_awarded = weight * rating / 5`
- `assessed_weight = 所有非 NOT_ASSESSABLE 维度权重之和`
- `score_coverage = assessed_weight / 100`
- 仅当 `review_mode = formal` 且 `score_coverage = 1.0` 时输出 `final_score`
- 否则只输出 `provisional_score`
- 若任一任务仅为 `mentioned`：
  - `results_and_interpretation <= 1`
- 若不存在 `mentioned` 但任一任务仅为 `answered`：
  - `results_and_interpretation <= 2`
- 若任一任务未到 `validated`：
  - `validation_sensitivity_robustness <= 3`
- 若任一任务低于 `evidenced`：
  - 置 `quality_blocked = true`
  - 置 `submission_blocked = true`
- 若 `review_mode = preliminary`：
  - 置 `submission_blocked = true`
  - 但不要把预审状态写成官方违规或内容 `BLOCKER`
- 若任一官方规则检查为 `FAIL`：
  - 保留内容分
  - 置 `official_compliance.compliance_blocked = true`
  - 不把内容分解释为可提交
- 若任一内容问题为 `BLOCKER`：
  - 保留内容分
  - 置 `quality_blocked = true`
  - 不把内容分解释为主结论可信或可提交
- `submission_blocked = official_compliance.compliance_blocked or quality_blocked`
- `overall_verdict` 只允许：
  - `BLOCKED_COMPLIANCE_AND_QUALITY`
  - `BLOCKED_COMPLIANCE`
  - `BLOCKED_QUALITY`
  - `PRELIMINARY`
  - `REVIEWED`
