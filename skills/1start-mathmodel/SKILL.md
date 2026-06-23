---
name: 1start-mathmodel
description: "启动并持续推进数学建模竞赛完整工作流。用于用户明确要求完成整道赛题、完整论文或端到端建模项目时：锁定官方题面和附件，建立逐条需求覆盖契约，生成 plan.md 与 todo.md，依次协调 2analysis-modeling、3coding-visual、可选的 4drawio、5writing 和 6verity，并在缺项或验收失败时回退修复直至达到明确终态。不要用于单独咨询、单阶段实现、局部论文修改或单次审稿。"
---

# 数学建模完整工作流

作为总控入口管理项目状态、阶段依赖和验收闭环；不要替代下游阶段 Skill 的专业工作。

## 核心原则

1. 先读完整题面和附件，再拆题或写代码。
2. 以官方要求逐条闭环，不以“文件已经存在”作为完成证据。
3. 先锁定权威输入、项目根目录和交付模式，禁止默认为训练样稿。
4. 前序契约变化时，立即使依赖它的后续阶段失效并重新验证。
5. 不用文字篇幅代替模型、结果、验证或题面覆盖。
6. 只在全部终态条件满足后宣告完成。
7. 论文必须形成“问题是什么 -> 为什么这样建模 -> 模型怎么求解 -> 结果是否可信 -> 结论如何落地”的证据链；缺少任一核心环节时，不得把论文阶段判定为完成。

需要领域规则时读取 `../_references/math_modeling_norms.md`。下游阶段必须按需完整读取各自的 `SKILL.md`。

## 论文证据链标准

在 `complete_solution` 或 `submission` 模式下，写作与验收阶段必须检查论文是否形成可追溯证据链，而不是只有公式、图表或结果摘要。正文至少覆盖：

- 问题拆分：准确重述题意，说明各子问题的递进关系和对应章节。
- 建模依据：核心模型、假设、变量、约束和目标函数要有现实或理论来源，并解释适用边界。
- 数据处理依据：说明原始数据问题、处理方法、选择原因和对有效信息的影响。
- 求解匹配：算法选择、初值或参数范围、约束处理和停止条件要与模型特点匹配。
- 结果可信性：不只给数值，还要提供误差、残差、稳定性、敏感性、对比、回代或不确定性证据中的必要项。
- 结论落地：每个子问题给出直接答案、实际含义、适用范围和局限；未证明全局最优的结果必须表述为当前最优可行解、近似解或启发式解，并给出界、差距或验证依据，禁止过度宣称。

若模型和结果已经存在但论文只停留在摘要式结果汇报，写作阶段至少应判定为 `WARN` 并回退补写；若缺少直接答案、可信性验证或关键任务覆盖，应判定为 `FAIL`。

## 阶段 0：锁定项目与输入

在执行前完成以下检查：

- 确定唯一项目根目录。优先使用同时包含题面、附件或既有 `plan.md` 的目录；候选目录不唯一时询问用户。不要把项目产物误写到通用工作区根目录。
- 找到并完整读取官方题面、数据说明和全部附件。PDF 等格式应使用适合的读取或渲染工具，不得只依赖文件名、摘要或旧报告。
- 记录赛事、年份、题号、语言、工具链、时间预算、外部资料政策和交付模式。
- 交付模式只能是 `submission`、`complete_solution` 或 `exploration`。用户说“完成整题”时默认 `complete_solution`；不得擅自降级为 `exploration` 或“训练样稿”。
- 仅询问会实质改变结果且无法从现有文件判断的问题。无法获得非阻塞偏好时采用保守默认值，并在 `plan.md` 明示。
- 若正式提交缺少队号、模板或声明等用户专属信息，继续完成可完成部分，同时设置 `submission_blocked=true`，不得伪造信息。

## 必须产出

在项目根目录创建或更新：

- `plan.md`：权威输入、交付模式、偏好、阶段顺序、验收条件和风险。
- `todo.md`：阶段状态、gate、阻塞项和最后验证时间。
- `reports/contracts/requirements.json`：官方题面与提交要求的逐条覆盖契约。
- `reports/contracts/model_tasks.json`：建模任务、输入、模型、指标和输出契约。
- `paper/task_evidence_matrix.md`：每项题面要求在模型、结果和论文中的证据位置。

项目骨架：

```text
.
├── plan.md
├── todo.md
├── problem/                       # 题面、来源记录；已有等价目录可复用
├── reports/
│   ├── ANALYSIS_MODELING_REPORT.md
│   ├── RESULTS_REPORT.md
│   ├── DRAWIO_REPORT.md           # 仅在 DrawIO 阶段适用时要求
│   ├── VERIFY_REPORT.md
│   └── contracts/
│       ├── requirements.json
│       └── model_tasks.json
├── code/
├── results/
│   └── all_results.json
├── figures/
│   └── figure_manifest.json
└── paper/
    ├── main.typ
    ├── task_evidence_matrix.md
    └── sections/
```

复用合理的既有结构，不为匹配示例而做无关重构。

## 需求覆盖契约

`requirements.json` 至少包含：

```json
{
  "competition": "",
  "year": "",
  "problem_id": "",
  "delivery_mode": "complete_solution",
  "authoritative_inputs": [],
  "requirements": [
    {
      "id": "R1",
      "type": "task",
      "requirement": "",
      "owner_stage": "2analysis-modeling",
      "planned_evidence": [],
      "evidence": [],
      "task_coverage": "missing",
      "validated": false
    }
  ],
  "task_coverage": "missing",
  "quality_blocked": true,
  "submission_blocked": false,
  "validated": false
}
```

逐条录入：

- 题面中的每个问题、子问题、指定方法、比较、预测、解释和建议。
- 数据与附件要求。
- 赛事特定的摘要页、目录、页数、匿名性、引用、AI 使用说明和文件格式要求。

不得把多个独立要求合并成无法单独验收的一条。`planned_evidence` 在分析阶段声明预期证据，`evidence` 在执行后指向实际可检查的文件、JSON 字段、表格、图或论文小节。

## 统一状态语义

### `task_coverage`

- `missing`：官方要求尚未进入契约。
- `partial`：要求已登记，但拆分、责任阶段、指标、验证方法或预期证据仍不完整。
- `complete`：全部官方要求均已独立登记，并映射到责任阶段、指标、验证方法和预期证据。

`task_coverage` 只表示需求范围是否完整，不表示实现已经完成。项目级 `task_coverage=complete` 仅当所有必需要求均为 `complete`；实际实现与验收状态由 `validated` 表示。

### `quality_blocked`

存在会使结论不可信的硬问题时为 `true`，例如数据泄漏、模型与题意不符、关键指标缺失、结果不可复现、数值矛盾或重大因果越界。非阻塞局限应记录为 WARN，但不得滥用阻塞字段。

### `submission_blocked`

存在阻止交付或投稿的硬问题时为 `true`，例如缺少必需章节或声明、编译失败、图表缺失、页数超限、格式不合规或缺少用户专属提交信息。

### `validated`

只有实际执行对应检查且证据仍与当前输入和契约一致时才能为 `true`。文件存在、旧报告 PASS 或人工推测都不能代替验证。任何权威输入、需求契约、模型结果、图表或论文正文变化后，受影响项必须重置为 `false`。

## Gate 规则

阶段状态：`pending / in_progress / passed / warned / failed / skipped`。

Gate：`PENDING / PASS / WARN / FAIL / SKIP`。

- `[x]` 仅用于 `passed + PASS` 或不适用且有理由的 `skipped + SKIP`。
- `task_coverage=missing|partial`、`quality_blocked=true` 或当前阶段存在硬错误时，gate 必须为 `FAIL`。
- `submission_blocked=true` 时，最终 gate 必须为 `FAIL`；阶段性 gate 可按责任归属标记。
- `WARN` 仅表示不阻塞直接答案、可信度与交付的局限。
- 后续阶段不得在任何依赖阶段为 `PENDING/WARN/FAIL` 时标记 `PASS`。

推荐的 `todo.md` 条目：

```markdown
- [ ] 1. 赛题分析与建模设计 — `2analysis-modeling` — status: pending — gate: PENDING — validated: false
```

每次进入、完成、回退阶段或发现新阻塞时立即更新状态，不要在流程末尾一次性补写。

## 阶段执行与验收

### 1. 赛题分析与建模设计 — `2analysis-modeling`

产物：`ANALYSIS_MODELING_REPORT.md`、`requirements.json`、`model_tasks.json`。

PASS 条件：

- 官方题面和附件已完整读取并登记。
- 每条任务要求均映射到模型任务、指标、预期输出和验证方法。
- 无未经说明的数据缺口、未来信息泄漏或关键定义歧义。
- 项目级 `task_coverage=complete`；此处表示设计覆盖完整，不表示结果已完成。

### 2. 编程实现和图表生成 — `3coding-visual`

产物：`code/`、`RESULTS_REPORT.md`、`all_results.json`、数据图和 manifest。

PASS 条件：

- `model_tasks.json` 中每项输入、指标、输出和验证均有机器可检查的结果。
- 复现命令成功；结果无 NaN、约束违例或未解释矛盾。
- 所有依赖计算的数据图已生成并登记。
- 需求证据已回填，受影响要求重新验证。

### 3. 非数据图绘制 — `4drawio`

仅当路线图、流程图或结构图能显著改善论文表达，或用户/赛制明确要求时执行。否则标记 `skipped + SKIP` 并记录理由。不得用概念图替代数据结果。

### 4. 竞赛论文撰写 — `5writing`

产物：`paper/`、`task_evidence_matrix.md` 和可编译论文。

PASS 条件：

- 每条任务要求都有明确的小节、直接答案和结果证据。
- 每个子问题形成“任务 -> 建模理由 -> 求解方法 -> 结果 -> 可信性证据 -> 实际解释”的最小论证链。
- 假设、变量、数据处理、算法选择、参数边界和局限不是孤立罗列，而能支撑后文结果。
- 关键图表在正文中说明用途、现象和结论，不以图表数量替代验证。
- 数值只引用当前权威结果，图表均来自当前 manifest。
- 论文结构满足赛事规则；必要的摘要、目录、参考文献和 AI 声明已处理。
- 不含内部路径、占位符、虚构引用、未验证结论，或把启发式/近似结果表述为已证明全局最优。

### 5. 验证和验收 — `6verity`

必须检查：任务覆盖、论文证据链、数值一致性、图表引用、引用真实性、编译、页数、提交结构和 PDF 全页视觉质量。

只有以下条件同时满足才能最终 PASS：

- 项目级 `task_coverage=complete`。
- 论文证据链覆盖完整；若存在未证明最优性、未闭合验证或结论过度宣称，不得标记为完成。
- `quality_blocked=false`。
- `submission_blocked=false`。
- 所有必需要求 `validated=true`。
- 当前版本的复现、编译和验收命令成功。

## 回退、修复与续跑

- 发现缺项时回退到最早责任阶段，不要只在论文中补一句话。
- 前序阶段被重新打开后，将所有依赖阶段重置为 `pending/PENDING` 和 `validated=false`；`SKIP` 阶段除外。
- 旧 `VERIFY_REPORT.md`、旧 PDF 或旧 JSON 不得作为当前 PASS 证据。先核对它们是否对应当前输入、契约和论文。
- 不删除用户文件；只覆盖明确属于本工作流且可再生的产物，并保留无关改动。
- 用户明确要求“完成整题”“完整工作流”或“修复到可交付”时，视为授权在项目范围内迭代修复。若用户只要求验收，则遵守 `6verity` 的只读边界。
- 遇到需要用户专属信息、外部授权或会改变目标的选择时停止推断，设置相应阻塞并询问用户。

## 完成定义

只有最终 gate 为 `PASS` 且 `requirements.json` 同时满足以下条件，才能称为“完成”：

```text
task_coverage = complete
quality_blocked = false
submission_blocked = false
validated = true
```

否则必须明确报告当前为 `WARN` 或 `FAIL`、阻塞项、已完成部分和最小下一步，不得用“论文已生成”代替完成声明。
