---
name: 3coding-visual
description: "数学建模编程实现与数据图表生成阶段。根据 `reports/ANALYSIS_MODELING_REPORT.md` 和 `reports/contracts/model_tasks.json` 编写可复现代码、运行求解、验证约束，输出 `reports/RESULTS_REPORT.md`、`results/all_results.json`，并维护 `figures/figure_manifest.json`。"
---

# 编程实现与数据图表生成

本 skill 承接 `2analysis-modeling`。目标是把建模报告里的模型和算法落实为可复现程序，跑出可信结果，并生成论文所需的数据型图表。

## 数学建模规范参考

如需领域判断，读取 `../_references/math_modeling_norms.md` 中的“题型防错速查”“代码实现与结果”“编码阶段常见错误”和“图表与可视化”小节。该文件只作为规范知识库，不新增本阶段固定产物。
如需确认 `model_tasks.json -> all_results.json -> figure_manifest.json` 的闭环、统一状态语义或回退重置规则，读取 `../_references/workflow_contract.md`。

## 阶段边界

- 本阶段负责：代码、实验运行、结果记录、结果表、数据驱动图表。
- 本阶段不负责：技术路线图、算法流程图、系统架构图、概念示意图。这些交给 `4drawio`。
- 本阶段不写论文正文，只为 `5writing` 提供可信数值和图表资产。

## 必须产出

- `reports/RESULTS_REPORT.md`
- `results/all_results.json`
- `figures/figure_manifest.json`
- `code/` 下的可复现实现
- 逐子问题 `contract_closure`

## 工作流程

### Step 1: 搭建代码结构

按 `plan.md` 创建 `code/`、`results/`、`figures/` 骨架，再开始写代码。子问题文件可命名为：

- `code/q1.py`, `code/q2.py`, `...`
- 或 `code/problem_<id>.py`

不要默认写死 `problem1.py/problem2.py/problem3.py`。

### Step 2: 逐子问题实现

优先读取：

- `reports/ANALYSIS_MODELING_REPORT.md`
- `reports/contracts/model_tasks.json`

每个子问题至少完成：

1. 读取所需数据。
2. 实现模型或算法。
3. 验证约束。
4. 输出核心结果。
5. 绘制必要图表。
6. 在 `reports/RESULTS_REPORT.md` 中写清方法、关键数值和校验结果。

每完成一个子问题，立刻做一次 `contract_closure`，逐项核对：

1. `inputs`：合同输入依赖是否真实使用并登记。
2. `key_metrics`：合同关键指标是否在结果中出现；若命名不同，必须显式提供别名映射。
3. `outputs`：合同要求的图、表、JSON 引用、派生文件是否真实存在并登记。
4. `validation`：是否留下约束校验、误差评估、稳健性检查或其他验证证据。
5. `reproduce_command`：是否能从当前项目根目录直接复现。

任一子项不通过，该子问题的 `contract_closure.status` 就不能写成 `PASS`。

### Step 3: 记录结果契约

在 `results/all_results.json` 中记录关键数值、表格、图表、数据来源、验证证据和复现命令。保持最小可读结构，例如：

```json
{
  "subproblems": [
    {
      "id": "q1",
      "metrics": {"rmse": 0.0},
      "metric_aliases": {"contract_metric_name": "rmse"},
      "tables": ["results/q1_table.csv"],
      "figures": ["figures/fig_q1_fit.pdf"],
      "validation": {"rmse_check": "PASS"},
      "data_sources": ["data/attachment1.xlsx"],
      "reproduce_command": "python code/q1.py",
      "contract_closure": {
        "inputs": "PASS",
        "key_metrics": "PASS",
        "outputs": "PASS",
        "validation": "PASS",
        "reproduce_command": "PASS",
        "status": "PASS"
      }
    }
  ]
}
```

约定：

- `metric_aliases` 用于“合同指标名 -> 实际结果字段名”的显式映射。
- 若合同没有要求图，可以不产图；但必须提供其他证据载体，如 `tables`、`artifacts` 或结构化结果字段，并写明 `figure_absence_reason`。
- 若合同明确要求图或表，则缺失对应文件、缺少 `all_results.json` 登记，或缺少 `figure_manifest.json` 登记，均视为 `FAIL`。

### Step 4: 维护图表清单

在 `figures/figure_manifest.json` 中登记本阶段生成的数据图，至少包含：

```json
[
  {
    "id": "fig_q1_fit",
    "type": "data",
    "path": "figures/fig_q1_fit.pdf",
    "recommended_section": "问题一结果",
    "source": "results/all_results.json:q1"
  }
]
```

`4drawio` 会继续维护同一份 manifest；不要另起第二份图表清单。

仅把真实存在、且允许进入论文的图登记进 manifest。合同要求但尚未生成的图，不能用文字说明代替登记。

### Step 5: 写结果报告

`reports/RESULTS_REPORT.md` 推荐包含：

- 运行环境
- 数据读取与预处理
- 各子问题结果
- 约束与一致性校验
- 灵敏度分析
- 与建模报告的一致性说明
- 可复现运行方式
- 各子问题 `contract_closure` 摘要

所有进入论文的数值、表格、图表，都必须能回溯到 `RESULTS_REPORT.md` 或 `results/all_results.json`。

## 质量要求

- 优化类问题先保证可行解，再优化目标值。
- 预测类问题必须做训练/验证划分或合理误差评估。
- 评价类问题必须说明指标方向、归一化方法和权重来源。
- 图表输出为适合论文的 PDF；标题交给 Typst caption，不在图内写大标题。
