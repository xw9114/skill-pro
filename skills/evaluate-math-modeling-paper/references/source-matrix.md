# 来源矩阵

内置来源快照日期为 `2026-06-19`。本文件只保留来源摘要、用途和已知缺口，不长篇引用原文。

## 使用规则

- 需要引用官方要求、说明时效性或解释为什么这样判时读取本文件。
- 只把这里的来源当作公开权威来源摘要，不要把本文件本身当作新的官方规则来源。
- 报告和 JSON 中引用规则时，优先使用下面的 `source_id`。
- 区分 `document_version` 与 `applies_to_year`：前者是文档自身版本，后者是本次评审适用赛季。
- 用户提供的当前官方规则优先级最高，输出时使用 `source_mode = user_file` 或 `manual_note` 记录来源。

## 来源表

| source_id | 竞赛/机构 | 年份/版本 | 性质 | URL | 支持内容 | 备注 |
| --- | --- | --- | --- | --- | --- | --- |
| `CUMCM-CHARTER` | CUMCM | 长期公开 | official_guidance | https://www.mcm.edu.cn/html_cn/block/44e92058f537729c6b6a62a3662ee417.html | 官方公开核心评奖标准 | 已确认公开核心标准含假设合理性、建模创造性、结果正确性、文字表述清晰程度；未公开统一数值权重 |
| `CUMCM-2026-RULES` | CUMCM | 2026 | official_rule | https://www.mcm.edu.cn/html_cn/node/9d8e511fe7a1447b35f53a82c908e2e0.html | 2026 参赛规则、提交要求 | 当前年份官方规则，优先级高 |
| `CUMCM-2026-FORMAT` | CUMCM | 2026 | official_rule | https://www.mcm.edu.cn/html_cn/node/4cd596519c9eb9fbd866398f6df0caa3.html | 2026 论文格式要求 | 当前年份官方格式要求，优先级高 |
| `CUMCM-2023-REVIEW-NORM` | CUMCM | document_version=2023-revised; applies_to_year=2026 | official_guidance | https://www.mcm.edu.cn/html_cn/node/b1f48689659f0660e80a2d6279d7b37d.html | 全国奖项评阅规范 | 2023 年修订稿，适合支撑合规与评审流程说明；不要写成 2026 文档版本 |
| `CUMCM-2025-AI` | CUMCM | document_version=2025-trial; applies_to_year=2026 | official_rule | https://www.mcm.edu.cn/html_cn/node/eebcfb6dc37fd2de9603dc16026fdf01.html | AI 使用与披露要求 | 2025 年试行规定，适合判定 AI 披露合规；不要写成 2026 文档版本 |
| `COMAP-2026-INSTRUCTIONS` | COMAP MCM/ICM | 2026 | official_rule | https://www.contest.comap.com/undergraduate/contests/mcm/instructions.php | 官方 instructions、页数和提交规则 | 当前年份官方规则，优先级高 |
| `COMAP-FAQ` | COMAP MCM/ICM | 2026 公开 FAQ | official_guidance | https://www.contest.comap.com/undergraduate/contests/mcm/faq.php | 常见规则解释 | 适合补充说明边界和疑义 |
| `COMAP-TIPS` | COMAP MCM/ICM | document_version=V20240912; applies_to_year=2026 | official_guidance | https://www.contest.comap.com/undergraduate/contests/mcm/flyer/MCM-ICM_Tips.pdf | Summary Sheet、假设、验证、写作建议 | 支撑官方定性维度，不是数值评分表 |
| `COMAP-AI-POLICY` | COMAP MCM/ICM | document_version=v102025; applies_to_year=2026 | official_rule | https://www.contest.comap.com/undergraduate/contests/mcm/flyer/Contest_AI_Policy.pdf | AI 披露要求 | 适合 AI 合规判定 |
| `COMAP-SUBMISSION` | COMAP MCM/ICM | document_version=V20251232; applies_to_year=2026 | official_guidance | https://www.contest.comap.com/undergraduate/contests/mcm/flyer/MCM-ICM_SubProcess.pdf | 提交流程和文件要求 | 支撑提交格式与文件要求说明；版本号语义不等同日期 |
| `IMMC-RULES` | IMMC | 当前公开；cross-reference | official_rule | https://www.immchallenge.org/Pages/Rules.html | IMMC 官方规则 | 跨赛事、跨学段参考；面向中学生国际轮，不替代目标赛事规则 |
| `SIAM-M3-RULES` | SIAM M3 | 当前公开；cross-reference | official_rule | https://m3challenge.siam.org/the-challenge/rules-and-guidelines/ | M3 规则与指南 | 跨赛事、跨学段参考；高中赛制，不替代目标赛事规则 |
| `SIAM-M3-TIPS` | SIAM M3 | 当前公开；cross-reference | official_guidance | https://m3challenge.siam.org/resources/tips-guidance/ | 建模与写作建议 | 跨赛事、跨学段参考；高中赛制，不替代目标赛事规则 |
| `GAIMME-2E` | SIAM GAIMME | 第二版；cross-reference | educational_rubric | https://www.siam.org/media/wwjd5o2k/gaimme-2nd-ed-final-online-viewing-color.pdf | 教育性 rubric、建模写作规范 | 不是竞赛终审表，不可冒充官方评分表 |

## 已核验事实摘要

### CUMCM 2026

- 已确认的硬规则摘要：
  - 电子版第一页摘要
  - 摘要原则上不超过 1 页
  - 无需英文摘要
  - 正文不超过 30 页
  - 不要目录
  - 匿名
  - 必要代码完整可运行且与结果一致
  - 引用合规
  - AI 使用按规定披露
  - 论文与支撑材料各不超过 20MB
- 已确认的公开定性评审重点：
  - 假设合理性
  - 建模创造性
  - 结果正确性
  - 文字表述清晰程度
- 已知缺口：
  - 官方未公开统一数值权重

### COMAP MCM/ICM 2026

- 已确认的硬规则摘要：
  - 单一英文 PDF
  - 至少 12pt
  - 第一页 Summary Sheet
  - 控制号和页码
  - 匿名
  - AI 披露
  - 文件小于 25MB
  - 25 页上限，含摘要、正文、参考文献等；AI 报告例外按政策
- 已确认的公开定性评审重点：
  - Thought processes
  - Problem analysis
  - Modeling approaches
  - Mathematical methods
  - Summary Sheet 权重很高
  - 强调假设、模型动机、测试/误差/敏感性/稳定性、优缺点、结果解释、组织清晰与引用
- 已知缺口：
  - 官方未公开统一数值权重

### 其他权威交叉来源

- `IMMC-RULES`、`SIAM-M3-RULES`、`SIAM-M3-TIPS`、`GAIMME-2E` 仅用于跨赛事、跨学段的定性启发，共同支持以下长期稳定维度：
  - 问题定义
  - 假设/限制
  - 变量/参数/单位
  - 模型构建与方法选择
  - 数学正确性
  - 计算透明度和可复现性
  - 结果解释
  - 验证/敏感性/稳健性
  - 局限与适用边界
  - 组织表达
  - 引用诚信

## 已知缺口与使用限制

- CUMCM 和 COMAP 都没有公开统一的通用数值权重，不能伪装成官方评分表。
- `GAIMME-2E` 是教育 rubric，不是竞赛终审表。
- 交叉来源不得用于反推目标赛事硬规则，也不得提高目标赛事官方结论置信度。
- 如果用户要求对当前年份正式合规性做强结论，而当前年份可能已变化且无法联网核验，应明确标记时效风险。
