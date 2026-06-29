---
name: 5writing
description: "数学建模竞赛论文 Typst 撰写阶段。优先读取 `reports/contracts/model_tasks.json`、`results/all_results.json`、`figures/figure_manifest.json`，再结合分析报告、结果报告和图表 PDF 选择比赛模板、组织章节，并在论文正文中按章节直接插入图表。"
---

# 竞赛论文 Typst 撰写

本 skill 承接 `3coding-visual` 和 `4drawio`。前序阶段提供真实数据、图表 PDF 和记录文件；本阶段负责选择比赛模板、组织论文结构，并决定每张图表放入哪个章节。

优先调用 `typst-author` 学习或校正 Typst 写法；若该 skill 不可用，则直接按模板结构和基础 Typst 语法继续，不阻塞主流程。

## 数学建模规范参考

如需领域判断，读取 `../_references/math_modeling_norms.md` 中的“论文写作”“图表与可视化”和“非数据图工具选择”小节。该文件只作为规范知识库，论文结构仍按比赛模板和当前赛题内容决定。

## 跨阶段契约导航

涉及任务证据链、`task_evidence_matrix.md`、阻塞判定和最终可交付条件时，读取 `../_references/workflow_contract.md`，并以其为准；本文件只保留写作阶段的具体执行动作。

## 模板族

本技能内捆绑的 Typst 模板位于：

```text
templates/zh/<竞赛>/main.typ
templates/en/<竞赛>/main.typ
```

论文中的所有数值和图表结论必须来自 `reports/RESULTS_REPORT.md`、`results/all_results.json` 或 `figures/figure_manifest.json`。不得编造、估算或使用不同的四舍五入方式。

## 工作流

### 步骤 0：选择语言和模板

除非用户明确要求中文，否则 MCM/ICM/COMAP 一律使用英文；中文竞赛名称使用中文模板。

### 步骤 1：准备模板

优先复制匹配模板到 `paper/`。若模板缺失，再从最小可编译 Typst 结构重建。

存在匹配模板时，绝不从零开始写整篇论文。

### 步骤 2：先读契约，再构建图表规划

优先读取：

- `reports/contracts/model_tasks.json`
- `results/all_results.json`
- `figures/figure_manifest.json`

然后再按需回看：

- `reports/ANALYSIS_MODELING_REPORT.md`
- `reports/RESULTS_REPORT.md`
- `reports/DRAWIO_REPORT.md`

正式写正文之前，先创建 `paper/task_evidence_matrix.md`，逐子问题列出：

- `task_id`
- `closure_status`
- `method_evidence`
- `direct_answer_evidence`
- `validation_or_boundary_evidence`
- `planned_section`
- `gaps`

矩阵字段、闭环语义和阻塞含义遵循 `../_references/workflow_contract.md`，不在本文件重复定义。

如果任一前序子问题的 `contract_closure` 不是 `PASS`，或从现有结果中无法判定为 `PASS`，就停止正式写作，先输出缺口清单；不得用行文润色去掩盖证据缺失。

先做一份图表规划，例如：

```text
fig_roadmap.pdf -> 引言/总体思路
fig_flow_q1.pdf -> 问题一方法
fig_pipeline.pdf -> 数据预处理
fig_q1_fit.pdf -> 问题一结果
```

再将 PDF 图表直接嵌入对应章节。Typst 图片路径必须相对于写入该 `image(...)` 的 `.typ` 文件。

### 步骤 3：撰写各节

按模板结构写正文，但对子问题章节不要固定暗示“三问”。若模板需要分问题文件，使用：

- `q1.typ`、`q2.typ`、`q3.typ`、...
- 或 `problem_<id>.typ`

若模板自带 `problem1/problem2/problem3` 命名，按实际题目数量扩展或重命名到等价结构，不要因为示例命名限制题目数量。

正文写作要求：

- 用连贯的学术段落，不堆砌列表。
- 图后有解释，公式后有变量说明。
- 不在最终论文中出现内部工作流名称，如 `reports/`、`results/`、`figures/`、`model_tasks.json`。
- 每个子问题对应的正文都至少覆盖四件事：`方法`、`证据载体`、`直接回答`、`验证或边界`。
- 摘要、Summary Sheet、引言中的综述句，不计入“每问正文闭环”。
- 如果某问没有图，也必须在正文中落到可追溯的表、数值、结构化结果或其他证据载体，且与 `task_evidence_matrix.md` 保持一致。

### 步骤 4：参考文献

创建 `paper/references.typ`，只使用真实存在的参考文献。

### 步骤 5：最后写摘要或总结

在所有章节完成后撰写摘要或 Summary Sheet。必须覆盖每个子问题的方法和关键数值结果。

摘要只能汇总已经在正文闭环的内容，不能替代某一问缺失的方法、证据、直接回答或验证边界。
