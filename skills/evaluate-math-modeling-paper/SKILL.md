---
name: evaluate-math-modeling-paper
description: "依据权威公开规则和用户提供的当前赛事要求，对完整数学建模论文进行证据化内容质量评审、赛事合规检查、可重复综合评分和优先修改建议。用于已有完整论文初稿或定稿后的正式审稿场景；输入至少包括论文、题面/任务、竞赛名称与年份。不要用于读题拆解、建模路线建议、局部方案或未完成草稿的快速预检；这类任务改用 `math-modeling-contest`。不负责重写论文，不负责 Typst、PDF、路径、编译或空白页等工程验收。"
---

# 数学建模论文证据评审

本 skill 用于对已经写成的数学建模论文做证据化评审，重点处理“内容质量是否站得住”和“赛事规则是否踩线”。推荐流程：`5writing -> evaluate-math-modeling-paper -> 定向修订 -> 6verity`。

## 与竞赛顾问 skill 的分界

- 已有完整论文，并要求正式合规检查、证据化评分、优先修改项或阻断结论：使用本 skill。
- 只有题面、思路、局部方案、局部结果或未完成草稿，并需要拆题、路线比较或快速风险预检：改用 `math-modeling-contest`。
- 用户只说“帮我审论文”且材料状态不明确时，先确认论文是否完整以及是否需要正式评分，再选择一个 skill；不要重复评审。

## 读取顺序

1. 始终读取 `references/competition-profiles.md`，先确定竞赛画像和规则优先级。
2. 始终读取 `references/evaluation-rubric.md`，按其中的维度、档位和置信度规则评审。
3. 始终读取 `references/source-matrix.md`，使用稳定的来源 ID、版本和适用年份。
4. 产出报告和 JSON 前读取 `references/output-contract.md`。
5. 人工完成维度判断后，运行 `scripts/score_evaluation.py` 做确定性校验与计分。
6. 仅核对兼容副本的“已验证 / 兼容保留”边界是否漂移时，运行 `scripts/verify_contract_boundary.py`；它只复核 `_tmp_skill_verify` 已覆盖分支，不扩大已验证语义。

## 输入要求

- 必需：论文、题面/任务、竞赛名称、竞赛年份
- 强烈建议：结果文件、代码、附件、AI 使用说明
- 正式评审前先检查必需输入：
  - 缺少论文时停止，要求用户提供论文。
  - 缺少题面、竞赛名称或年份时先向用户补问。
  - 用户无法补充时只能设置 `review_mode = preliminary`；不得输出 `final_score`，赛事专属合规项优先判 `UNKNOWN`。
- 缺失代码、结果或附件时：
  - 降低 `confidence`
  - 允许相关维度写成 `NOT_ASSESSABLE`
  - 不要假装验证过可复现性、结果正确性或代码可运行性

## 工件接入

按以下顺序建立 `artifacts` 清单，再开始判断：

1. 论文 PDF/DOCX：读取正文、页码结构和可用元数据。
2. 官方题面与附件：建立子问题、目标、约束、数据字段和单位基线。
3. 结果文件：核对正文关键数值、表格和图表是否一致。
4. 代码目录：核对入口、依赖、参数、随机种子、数据路径和关键结果生成链。
5. AI 使用说明及赛事规则：核对披露、匿名、格式和提交限制。

只对实际读取的工件建立证据引用。工件缺失时使用 `<family>:missing`，不得伪造文件、页码、章节或代码位置。

## 评审边界

- 只做：
  - 官方硬门槛/规则核对
  - 官方定性评审维度评审
  - 本 skill 的综合量化评分
  - 优先修改建议
- 不做：
  - 读题拆解、建模路线设计或未成稿阶段的快速预检；改用 `math-modeling-contest`
  - 代写或重写论文
  - 补跑大规模实验
  - Typst、PDF、路径、编译、空白页等工程验收
  - 预测官方获奖等级
- 如果用户要求“正式判断当前规则”且赛事年份可能变化：
  - 优先核验最新官方来源
  - 无法核验时只输出 `UNKNOWN` 或时效风险，不要把旧规则当当前事实

## 证据规则

- 每个官方结论、分数、扣分、`BLOCKER` / `MAJOR` / `MINOR`、优先修改项都必须附证据。
- 证据优先写成可追溯引用，例如：
  - `paper:p1`
  - `paper:sec-4.2`
  - `problem:q2`
  - `attachments:a1`
  - `results:all_results.json#q1.best_value`
  - `rule:CUMCM-2026-FORMAT`
- `task_coverage` 必须按题面顶层任务逐项记录，状态只允许 `mentioned` / `answered` / `evidenced` / `validated`，且语义严格递进。
- 摘要、总述、`summary-sheet`、`executive-summary`、`abstract` 等定位单独提到某任务，只能支撑 `mentioned`；不能代替正文 `paper_refs`、`body_evidence_refs` 或 `validation_evidence_refs`。
- 无证据不得断言。
- 规则优先级固定为：
  - 用户提供的当前官方规则
  - 当前年份官方页面或 PDF
  - 较旧官方规则
  - 官方通用指南
  - 教育 rubric
  - 本 skill 综合建议

## 工作流

### 1. 建立竞赛画像
按 `references/competition-profiles.md` 选择 `competition_profile`。若赛事不在已知画像内，使用通用画像，并显式记录时效风险和适用边界。

同时设置：
- `review_mode = formal`：论文、题面、竞赛名称和年份均可确认。
- `review_mode = preliminary`：至少一项正式评审输入不完整，只能形成预审。

### 2. 划分三类标准
始终分开书写以下三类信息：
- 官方硬门槛/规则
- 官方定性评审维度
- 本 skill 综合量化权重

绝不要把本 skill 的综合权重写成赛事官方评分表。

### 3. 先做合规，再做质量
先列出 `official_compliance.checks`，每项只判 `PASS` / `FAIL` / `UNKNOWN`。再评内容问题，严重级别只用 `BLOCKER` / `MAJOR` / `MINOR`。

### 4. 先写 `task_coverage`
按题面顶层任务逐项填写 `task_coverage`，每项至少包含：
- `task_id`
- `task_label`
- `status`
- `problem_ref`
- `paper_refs`
- `body_evidence_refs`
- `validation_evidence_refs`
- `evidence_refs`
- `notes`

状态含义：
- `mentioned`：只在摘要、总述或轻量描述里提到任务，没有正文回答或可追溯证据
- `answered`：正文已经回答任务，但还没有可追溯证据
- `evidenced`：正文已回答，且有 `body_evidence_refs`
- `validated`：在 `evidenced` 基础上，还有 `validation_evidence_refs`，且这些定位必须显式体现验证、敏感性、稳健性、回测、误差或约束检查等验证语义

### 5. 做维度评分
按 `references/evaluation-rubric.md` 的 10 个维度打分：
- 评分档位：`0` 到 `5`
- 证据不足：`NOT_ASSESSABLE`
- 维度评分必须带 `evidence_refs`
- 需要引用规则时再带 `source_ids`

### 6. 计算总分
先人工写出 `reports/contracts/paper_evaluation.json`，再运行：

```bash
py -3 scripts/score_evaluation.py reports/contracts/paper_evaluation.json
```

脚本只做确定性校验和计分，不替代内容判断。
脚本不会原地改写输入 JSON，而是把补全/计分后的 JSON 输出到 stdout；如果要保存结果，调用方需要使用重定向，或先写入临时文件后再替换目标文件。

### 7. 输出结果
按 `references/output-contract.md` 产出：
- `reports/PAPER_EVALUATION_REPORT.md`
- `reports/contracts/paper_evaluation.json`

若用户明确只要当前对话中的评审，不要强制创建持久化报告；仍须遵守同一输出契约，并用临时输入运行计分脚本。

## 判定要求

- 官方规则：`PASS` / `FAIL` / `UNKNOWN`
- 内容问题：`BLOCKER` / `MAJOR` / `MINOR`
- 总分：
  - `score_coverage = assessed_weight / 100`
  - 仅当 `review_mode = formal` 且全部 10 个维度都已评估时，输出 `final_score`
  - 否则只输出 `provisional_score`
- 若任一 `task_coverage[*].status` 低于 `evidenced`：
  - 置 `quality_blocked = true`
  - 置 `submission_blocked = true`
  - 执行摘要不得把当前稿件解释为“可提交”
- 若 `review_mode = preliminary`：
  - 置 `submission_blocked = true`
  - 但不要把 `preliminary` 误写成官方 `FAIL` 或内容 `BLOCKER`
- 若存在官方 `FAIL`：
  - 保留内容分
  - 同时标记 `official_compliance.compliance_blocked = true`
- 若存在内容 `BLOCKER`：
  - 保留内容分
  - 同时标记 `quality_blocked = true`
- 任一阻断存在时：
  - 标记 `submission_blocked = true`
  - 执行摘要不得把内容分解释为“可提交”或“已通过”

## 交付检查

完成前确认：
- `competition_profile`、`retrieval_date`、`sources` 已填写
- `review_mode`、`rubric`、`artifacts` 已填写
- `task_coverage` 已覆盖题面顶层任务，且摘要单独提及没有被误记为正文证据
- `official_compliance.checks` 每条有规则来源和证据
- `quality_blockers`、`priority_fixes` 每条有证据
- `quality_blocked`、`submission_blocked`、`overall_verdict` 已由脚本计算
- `dimension_scores` 的 ID、权重、档位与 rubric 一致
- `confidence` 明确反映输入完整度
- 没有把推测写成事实
