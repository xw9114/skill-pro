---
name: 6verity
description: "数学建模竞赛最终验收阶段。默认只做结构、图表引用、数值一致性、Typst 编译和 PDF 基础检查，并在 `reports/VERIFY_REPORT.md` 中输出 `PASS/WARN/FAIL`；只有用户明确要求修复时才进入修复模式。"
---

# 验证和验收

本 skill 是完整工作流的最后一关。默认模式只负责发现问题、归类风险、给出 `PASS/WARN/FAIL` 结论；不默认重写论文、不默认改代码、不默认回填前序阶段。只有用户明确要求修复时，才进入修复模式。

## 数学建模规范参考

如需领域判断，读取 `../_references/math_modeling_norms.md` 中的“论文验收与一致性”小节。该文件只是规范知识库，不是固定执行流程。
涉及契约闭环、阻塞字段、Gate 判定和最终 PASS 条件时，读取 `../_references/workflow_contract.md`，并以其为准；本文件只保留验收动作与检查项。

## 阶段边界

- 本阶段负责：结构验收、文本质量门禁、图表引用检查、结果一致性检查、Typst 编译检查、PDF 基础视觉检查、提交清单。
- 本阶段不负责：重新设计模型、重新跑大规模实验、默认重写整篇论文。
- 默认模式下只记录问题；修复模式下只做小范围、可回溯修复。

## 输入

优先把以下文件作为验收输入：

1. `reports/ANALYSIS_MODELING_REPORT.md`
2. `reports/contracts/model_tasks.json`
3. `reports/RESULTS_REPORT.md`
4. `results/all_results.json`
5. `figures/figure_manifest.json`
6. `reports/DRAWIO_REPORT.md`（若存在）
7. Typst 入口文件、章节文件、参考文献文件、图表目录、代码目录

旧项目若仍存在 `PROBLEM_ANALYSIS.md`，只作为兼容输入，不再作为默认命名。

## 工作流程

### Step 0: 先判定模式

- 默认：验收模式，只输出报告和结论。
- 仅当用户明确说“修复”“直接改”“帮我修到能过”为止时：进入修复模式。

### Step 1: 先跑契约闭环门禁

先按顺序检查 `model_tasks.json -> all_results.json -> figure_manifest.json -> paper body`，优先运行本 skill 的确定性脚本：

PowerShell / Python 原生调用示例：

```powershell
python "<按当前 skill 实际位置确定>/scripts/contract_closure_check.py" `
  --root-dir "$ROOT_DIR" `
  --model-tasks "$MODEL_TASKS_FILE" `
  --all-results "$ALL_RESULTS_FILE" `
  --figure-manifest "$FIGURE_MANIFEST_FILE" `
  --paper-dir "$PAPER_DIR" `
  --main "$MAIN_FILE" `
  --sections-dir "$SECTIONS_DIR"
```

如需落日志，由 PowerShell 自己做重定向，不要求 Bash 管道。

判定规则：

- 只要闭环未通过，结论就必须是 `FAIL`。
- `WARN` 只允许出现在闭环已经 `PASS` 之后的非阻断缺口。
- 若闭环失败，默认模式下停止正式验收结论；可以继续收集补充诊断，但不得把阶段标成通过。

### Step 2: 运行正文文本门禁

`writing_check.sh` 是 Bash 脚本，只能从 WSL / Git Bash / 其他 Bash 环境调用；不要声称 Windows CMD 或原生 PowerShell 直接可跑。优先显式传入实际路径：

```bash
set -o pipefail
SCRIPT_PATH="<按当前 skill 实际位置确定>/scripts/writing_check.sh"
mkdir -p _tmp
bash "$SCRIPT_PATH" \
  --paper-dir "$PAPER_DIR" \
  --main "$MAIN_FILE" \
  --sections-dir "$SECTIONS_DIR" \
  --references "$REFERENCES_FILE" \
  --figures-dir "$FIGURES_DIR" \
  --results-file "$RESULTS_FILE" \
  --analysis-report "$ANALYSIS_REPORT_FILE" \
  --model-tasks "$MODEL_TASKS_FILE" \
  --all-results "$ALL_RESULTS_FILE" \
  --figure-manifest "$FIGURE_MANIFEST_FILE" \
  | tee _tmp/writing_check.log
```

`writing_check.sh` 只扫描正文文本，不替代前一层契约闭环，也不生成论文、不编译 PDF。脚本输出的 `FAIL` 属于硬错误；默认模式下记录为未通过，修复模式下才进入修复。

### Step 3: 检查章节数量和标题顺序

重点检查：

- `main.typ` 中 `#include("...")` 的数量与正文结构是否匹配。
- 同时识别 `#include("x.typ")`、`#include ("x.typ")` 和 `#include "x.typ"`。
- include 顺序是否符合文件名前缀顺序。
- 章节文件是否缺失、重复引用、未被引用。
- 每个 section 是否有明确一级标题。
- 如果题目不是三问，不强行要求三段问题章节；按 `reports/ANALYSIS_MODELING_REPORT.md` 或 `model_tasks.json` 的子问题数量核对。

### Step 4: 检查图表和 manifest

检查：

- `#figure(image(...), caption: [...])` 的图片是否真实存在。
- `figures/figure_manifest.json` 中登记的论文用 PDF 是否存在、是否在正文中出现。
- 正文引用的图是否都已登记在 manifest；未登记则直接 `FAIL`。
- 数据图是否放在结果/分析章节，非数据图是否放在方法/总体思路章节。
- caption 是否过长、过泛或与图意不一致。

### Step 5: 检查写作质量和信息泄露

检查：

- `TODO`、`PLACEHOLDER`、`待补充`、`待续写` 等占位符。
- 正文是否泄露内部工作流文件名或 JSON 路径。
- 正文是否过度列表化。
- 图后是否缺解释、公式后是否缺变量说明、结论是否只报数不解释。

默认模式下只记录问题，不自动改文。

### Step 6: 检查数值一致性

检查：

- 论文中的关键数值是否来自 `reports/RESULTS_REPORT.md` 或 `results/all_results.json`。
- 目标函数值、误差指标、排名、权重、阈值、灵敏度结果是否冲突。
- `model_tasks.json` 中要求展示的核心结果，正文是否至少覆盖到了对应结论。
- 不强制要求“每问必须有图”；但若合同要求图或表，缺失对应载体时必须 `FAIL`。

### Step 7: 检查引用和模板规范

检查：

- 参考文献文件是否存在，或模板是否采用了其他真实引用机制。
- 正文引用标记是否能对应到真实参考文献。
- 选定的 Typst 入口是否保留比赛模板必要结构。

### Step 8: Typst 编译

如果 Typst 可用，编译论文并确认输出 PDF 非空。

- 默认模式：编译失败则直接记 `FAIL`。
- 修复模式：可以修语法、路径、图片引用或模板问题后重跑。

### Step 9: PDF 基础视觉检查

若有可用工具，导出页面 PNG 逐页检查空白页、缺页、明显裁切、重叠、乱码和越界；若没有工具，至少记录“未执行视觉检查”的原因，并完成 PDF 非空、页数、页面尺寸等基础检查。

### Step 10: 写验收报告

创建 `reports/VERIFY_REPORT.md`：

```markdown
# 验证和验收报告

## 结论
PASS / WARN / FAIL

## 检查项
| 检查项 | 结果 | 说明 |
| --- | --- | --- |

## 章节结构
## 图表引用
## 数值一致性
## 文本质量门禁
## Typst 编译
## PDF 视觉检查
## 仍需处理的问题
```

## 结论规则

- `FAIL`：存在硬错误，不能交稿。
- `WARN`：契约闭环和正文硬门禁均已通过，但仍有明显风险或缺口。
- `PASS`：契约闭环通过，硬错误清零，核心结果一致，图表引用正常，编译通过或已说明限制，视觉检查通过或已说明无法执行原因。

## 硬错误标准

以下问题必须判定 `FAIL`：

- `model_tasks.json -> all_results.json -> figure_manifest.json -> paper body` 任一环未闭合。
- 缺少选定的 Typst 入口或核心正文。
- Typst 入口 include 的章节文件不存在。
- 正文章节缺少一级 Typst 标题，或标题等号后缺少空格。
- 正文仍有占位符。
- 正文泄露内部工作流文件名。
- 引用的图片不存在。
- 正文引用的图未在 `figure_manifest.json` 登记。
- 合同要求的图、表、JSON 引用或上游输入依赖缺失。
- 关键数值与结果记录冲突。
- Typst 可用但论文编译失败。
- 编译后的 PDF 为空、缺页、页数异常或页面尺寸异常且无法解释。

## 警告标准

以下问题可判定为 `WARN`：

- 未引用的备用图片。
- 某章节过短或明显不均衡。
- caption 偏长。
- 参考文献偏少。
- 图表后解释文字不足。
- 视觉检查工具不可用，但已记录原因并完成基础 PDF 检查。
