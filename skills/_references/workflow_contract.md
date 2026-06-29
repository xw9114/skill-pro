# 数学建模工作流共享契约

本文件是数学建模阶段型 skills 的跨阶段单一真源。它只定义共享语义，不替代各阶段自己的执行步骤。

## 何时读取

- `1start-mathmodel`：锁定项目根目录、交付模式、阶段顺序、回退规则和完成定义时读取。
- `2analysis-modeling`：建立 `requirements.json`、`model_tasks.json`，或判断分析改动会影响哪些下游阶段时读取。
- `3coding-visual`：回填 `all_results.json`、更新 `figure_manifest.json`、声明 `contract_closure` 时读取。
- `4drawio`：更新共享 manifest、决定 `skipped + SKIP` 是否成立时读取。
- `5writing`：创建 `paper/task_evidence_matrix.md`、判断是否允许正式写作、声明证据闭环时读取。
- `6verity`：给出 `PASS/WARN/FAIL`、判定阻塞字段和最终完成状态时读取。

## 共享范围

以下语义统一以本文件为准：

1. `task_coverage`、`quality_blocked`、`submission_blocked`、`validated`
2. 阶段状态与 Gate 取值
3. 上下游失效与重置规则
4. 论文证据链最小闭环
5. 最终“完成”的判定条件

阶段特有的工作流、模板、工具调用、产物细节，仍以各自 `SKILL.md` 为准。

## 跨阶段闭环链路

默认闭环链路如下：

```text
requirements.json
-> model_tasks.json
-> all_results.json
-> figure_manifest.json
-> task_evidence_matrix.md
-> paper body
-> VERIFY_REPORT.md
```

任何一环缺口都不能靠后文文字润色代替。

## 统一字段语义

### `task_coverage`

- `missing`：官方要求尚未进入契约。
- `partial`：要求已登记，但拆分、责任阶段、指标、验证方法或预期证据仍不完整。
- `complete`：全部官方要求均已独立登记，并映射到责任阶段、指标、验证方法和预期证据。

`task_coverage` 只表示需求范围是否完整，不表示实现已经完成。

### `quality_blocked`

存在会使结论不可信的硬问题时为 `true`，例如数据泄漏、模型与题意不符、关键指标缺失、结果不可复现、数值矛盾或重大因果越界。

### `submission_blocked`

存在阻止交付或投稿的硬问题时为 `true`，例如缺少必需章节或声明、编译失败、图表缺失、页数超限、格式不合规或缺少用户专属提交信息。

### `validated`

只有实际执行对应检查且证据仍与当前输入、契约和产物一致时才能为 `true`。文件存在、旧报告 PASS 或人工推测都不能代替验证。

## 阶段状态与 Gate

阶段状态：`pending / in_progress / passed / warned / failed / skipped`

Gate：`PENDING / PASS / WARN / FAIL / SKIP`

统一规则：

- `[x]` 只用于 `passed + PASS`，或不适用且理由充分的 `skipped + SKIP`。
- 只要当前阶段存在硬错误，或其关键共享字段为 `task_coverage=missing|partial`、`quality_blocked=true`，当前 Gate 就不能标为 `PASS`。
- `WARN` 只表示非阻断局限；不得用 `WARN` 掩盖契约缺口、数值冲突、编译失败或证据链断裂。
- 依赖阶段仍为 `PENDING/WARN/FAIL` 时，后续阶段不得宣称 `PASS`。
- 最终存在 `submission_blocked=true` 时，最终 Gate 必须是 `FAIL`。

## 失效与重置规则

- 官方题面、附件、赛事规则、交付模式变化后：`requirements.json` 及其下游阶段全部重新核对。
- `requirements.json` 或 `model_tasks.json` 变化后：`3coding-visual`、`5writing`、`6verity` 相关 `validated` 必须重置为 `false`。
- `all_results.json` 或 `figure_manifest.json` 变化后：`5writing`、`6verity` 相关 `validated` 必须重置为 `false`。
- 论文正文、章节结构、关键图表、模板入口变化后：`6verity` 的 `validated` 必须重置为 `false`。
- 旧 `VERIFY_REPORT.md`、旧 PDF、旧 JSON 不能直接作为当前 PASS 证据；只有先确认它们仍对应当前输入和产物，才能继续引用。

## 论文证据链最小标准

每个顶层任务至少形成以下闭环：

```text
任务定义
-> 建模理由
-> 求解方法
-> 结果载体
-> 验证或边界
-> 直接答案与落地解释
```

补充约束：

- 摘要、总述、Summary Sheet 只能汇总，不能替代正文闭环。
- 图表、表格、JSON、正文小节之间必须可追溯互引。
- 未证明全局最优时，只能表述为当前最优可行解、近似解或启发式解，并给出依据。
- 若合同要求图、表或验证证据，缺失时不得靠文字“描述已完成”代替。

## 最终完成定义

只有最终 Gate 为 `PASS`，且 `requirements.json` 同时满足以下条件，才能称为“完成”：

```text
task_coverage = complete
quality_blocked = false
submission_blocked = false
validated = true
```

对 `5writing` 和 `6verity` 的额外要求：

- `task_evidence_matrix.md` 已覆盖题面顶层任务，并能回链到正文和结果证据。
- `model_tasks.json -> all_results.json -> figure_manifest.json -> paper body` 闭环成立。
- 编译、验收和当前版本证据一致；若任何一项失败，只能报告 `WARN` 或 `FAIL`，不得宣称“可提交”。
