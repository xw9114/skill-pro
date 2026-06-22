---
name: 1start-mathmodel
description: "数学建模竞赛完整工作流入口。仅在用户明确要启动整套比赛流程时使用：收集偏好，生成 plan.md 与 todo.md，并串联 2analysis-modeling、3coding-visual、4drawio、5writing、6verity。不要用于单独的建模咨询、单次审稿或单阶段代码/论文任务。"
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, WebSearch, WebFetch
---

# 数学建模工作流

本 skill 是数学建模竞赛项目的总控入口。它负责启动流程、记录偏好、生成计划，并按顺序调用后续阶段 skill；它不替代任何下游阶段。

## 数学建模规范参考

如需领域判断，读取 `../_references/math_modeling_norms.md`。该文件只提供竞赛规范和防错知识，不改变本 skill 的阶段顺序和产出约定。

## 必须产出

在当前工作目录中创建或更新：

- `plan.md`：整体流程方案、阶段顺序、预期产物和风险控制。
- `todo.md`：阶段任务清单、阶段状态和 gate。

## 工作流

### 1. 询问用户偏好

只问会实质影响流程的问题，默认控制在 4-6 项：

1. 竞赛类型或目标赛制。
2. 语言与主要工具（Python / MATLAB / Typst 等）。
3. 时间预算。
4. 优先目标：可交稿 / 可复现 / 冲奖。
5. 是否允许使用外部文献。
6. Typst 模板或论文格式偏好。

### 2. 制定方案

按以下结构编写 `plan.md`：

```markdown
# 方案

workflow:
1. 赛题分析与建模设计 - `2analysis-modeling`
2. 编程实现和图表生成 - `3coding-visual`
3. 非数据图绘制 - `4drawio`
4. 竞赛论文撰写 - `5writing`
5. 验证和验收 - `6verity`
```

## 项目目录结构

各阶段按此骨架创建和填充文件：

```text
.
├── plan.md
├── todo.md
├── reports/
│   ├── ANALYSIS_MODELING_REPORT.md
│   ├── RESULTS_REPORT.md
│   ├── DRAWIO_REPORT.md
│   ├── VERIFY_REPORT.md
│   └── contracts/
│       └── model_tasks.json
├── code/
│   ├── q1.py
│   ├── q2.py
│   ├── ...
│   └── utils.py
├── results/
│   └── all_results.json
├── figures/
│   ├── *.pdf
│   ├── *.drawio
│   └── figure_manifest.json
└── paper/
    ├── main.typ
    └── sections/
```

若更适合按题号命名，也可使用 `problem_<id>.py`；不要默认写死 `problem1.py/problem2.py/problem3.py`。

### 3. 生成待办

将 `todo.md` 写成阶段性 checklist，并显式区分：

- `status`：`pending / in_progress / passed / warned / failed`
- `gate`：`PENDING / PASS / WARN / FAIL`

规则：

- 只有 `status=passed` 且 `gate=PASS` 时，条目才能写成 `[x]`。
- `gate=WARN` 或 `gate=FAIL` 时，条目必须保持 `[ ]`，分别对应 `status=warned` 或 `status=failed`。
- 阶段开始执行后先改为 `status=in_progress`，不要直接从 `pending` 跳到 `[x]`。

推荐格式：

```markdown
# 待办事项

- [ ] 1. 赛题分析与建模设计 - `2analysis-modeling` - status: pending - gate: PENDING
- [ ] 2. 编程实现和图表生成 - `3coding-visual` - status: pending - gate: PENDING
- [ ] 3. 非数据图绘制 - `4drawio` - status: pending - gate: PENDING
- [ ] 4. 竞赛论文撰写 - `5writing` - status: pending - gate: PENDING
- [ ] 5. 验证和验收 - `6verity` - status: pending - gate: PENDING
```

每进入或结束一个阶段，都要更新 `todo.md` 对应状态和 gate，并在必要时用一行备注写明未通过原因。

### 4. 依次执行阶段

| 阶段 | Skill | 作用 | 主要产物 |
| --- | --- | --- | --- |
| 赛题分析与建模设计 | `2analysis-modeling` | 解析题意、识别变量/约束/数据/评价指标，并建立数学模型与求解策略。 | `reports/ANALYSIS_MODELING_REPORT.md`, `reports/contracts/model_tasks.json` |
| 编程实现和图表生成 | `3coding-visual` | 实现可复现代码，运行实验，产出数值结果和数据图。 | `code/`, `reports/RESULTS_REPORT.md`, `results/all_results.json`, `figures/figure_manifest.json` |
| 非数据图绘制 | `4drawio` | 生成流程图、结构图、路线图等非数据图。 | `figures/*.drawio`, `figures/*.pdf`, `reports/DRAWIO_REPORT.md`, `figures/figure_manifest.json` |
| 竞赛论文撰写 | `5writing` | 基于前序报告和 manifest 组织论文并嵌入图表。 | `paper/` |
| 验证和验收 | `6verity` | 默认只做验收并输出 `PASS/WARN/FAIL`；只有用户明确要求修复时才进入修复模式。 | `reports/VERIFY_REPORT.md` |

## 阶段边界

- `3coding-visual` 负责所有依赖计算结果或实验输出的数据图表。
- `4drawio` 只负责概念图、算法流程图、架构图、路线图等非数据图示。
- `5writing` 优先读取 `model_tasks.json`、`all_results.json`、`figure_manifest.json`，再按需回看长报告。
- `6verity` 默认验收，不默认代替写作阶段直接改论文。
- 任何前序阶段只要 gate 不是 `PASS`，后续阶段都不得标记为 completed。
