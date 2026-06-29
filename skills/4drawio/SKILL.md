---
name: 4drawio
description: "数学建模非数据型图示绘制阶段。根据 `reports/ANALYSIS_MODELING_REPORT.md`、`reports/RESULTS_REPORT.md` 和已有 `figures/figure_manifest.json` 生成技术路线图、子问题求解流程图、模型结构图、数据处理流程图等 DrawIO 图，并更新同一份 `figures/figure_manifest.json`。"
---

# DrawIO 非数据图示绘制

本 skill 承接 `3coding-visual`。它只负责论文中的非数据型图示，例如技术路线图、求解流程图、模型结构图、数据处理流程图、变量关系图、指标体系图等。

## 数学建模规范参考

如需领域判断，读取 `../_references/math_modeling_norms.md` 中的“图表与可视化”和“非数据图工具选择”小节。该文件只作为规范知识库，不要求为了凑数量生成额外图示。
如需确认图表 manifest 的共享约束、统一状态语义或回退规则，读取 `../_references/workflow_contract.md`。

## 阶段边界

- 本阶段负责：DrawIO 源文件、非数据图 PDF、图示生成记录、图示 manifest 更新。
- 本阶段不负责：折线图、柱状图、散点图、热力图、箱线图、雷达图等数据图。这些由 `3coding-visual` 生成。
- 本阶段不重跑模型、不修改 `code/`，不改写 `reports/RESULTS_REPORT.md` 的数值结论。

## 必须产出

- `figures/*.drawio`
- `figures/*.pdf`
- `reports/DRAWIO_REPORT.md`
- 更新 `figures/figure_manifest.json`

## 工作流程

### Step 1: 盘点已有图表和需求

优先读取：

- `reports/ANALYSIS_MODELING_REPORT.md`
- `reports/RESULTS_REPORT.md`
- `figures/figure_manifest.json`（若存在）
- `figures/` 目录列表

先列出需要的非数据图，例如：

```text
DRAWIO PLAN CHECKLIST:
[ ] fig_roadmap
[ ] fig_flow_q1
[ ] fig_flow_q2
[ ] fig_pipeline
[ ] fig_model
```

清单不是固定模板，要根据题目实际删减或增补。`fig_flow_q<id>` 按实际子问题数量扩展。

### Step 2: 判定图类型

常见图示选择：

| 图类型 | 文件名建议 | 适用场景 |
| --- | --- | --- |
| 技术路线图 | `fig_roadmap` | 展示整体解题路线、章节逻辑、方法串联 |
| 子问题求解流程图 | `fig_flow_q<id>` | 展示单个子问题的输入、判断、算法、输出 |
| 数据处理流程图 | `fig_pipeline` | 展示数据清洗、特征构造、建模输入 |
| 模型结构图 | `fig_model` | 展示模块关系、变量关系、模型层次 |
| 指标体系图 | `fig_index_system` | 展示目标层、准则层、指标层 |

不要用 DrawIO 重复绘制数据图。

### Step 3: 生成 DrawIO 源文件

每张图一个 `.drawio` 文件，放在 `figures/`。要求：

- 文字语言与论文语言一致。
- 节点文字短，必要时双行。
- 同类节点样式统一。
- 箭头方向清晰，避免交叉。
- 解释留给正文，不在图里塞大段说明。

### Step 4: 导出 PDF

优先用可用的 DrawIO 命令导出 PDF；若导出失败，保留 `.drawio` 并在 `reports/DRAWIO_REPORT.md` 记录原因和建议命令。

### Step 5: 自检

每张图至少检查：

- `.drawio` 文件非空。
- 若导出成功，`.pdf` 文件非空。
- 节点没有明显重叠。
- 文件名和图意一致。
- 没有与 `3coding-visual` 的数据图重复。

### Step 6: 写生成记录并更新 manifest

创建 `reports/DRAWIO_REPORT.md`，并把非数据图写入 `figures/figure_manifest.json`。每条记录至少包含：

```json
{
  "id": "fig_roadmap",
  "type": "drawio",
  "path": "figures/fig_roadmap.pdf",
  "recommended_section": "引言/总体思路",
  "source": "reports/ANALYSIS_MODELING_REPORT.md"
}
```

## 质量要求

- 图示服务论文论证，不为装饰而画。
- 每张图必须能对应到 `reports/ANALYSIS_MODELING_REPORT.md` 中的真实方法。
- 论文阶段引用的非数据图都应有 `.drawio` 源文件和 PDF，或者在 `reports/DRAWIO_REPORT.md` 中说明导出失败。
