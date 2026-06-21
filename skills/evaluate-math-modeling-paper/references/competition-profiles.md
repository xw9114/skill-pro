# 竞赛画像与规则优先级

本文件用于选择 `competition_profile`，并确保先判规则来源优先级，再判内容质量。

## 一、规则优先级

按以下顺序取用规则：

1. 用户提供的当前官方规则
2. 当前年份官方页面或 PDF
3. 较旧官方规则
4. 官方通用指南
5. 教育 rubric
6. 本 skill 综合建议

若用户要求对当前年份正式规则做强结论，而当前年份规则可能变化且无法联网核验，必须写出时效风险；不要把旧规则当当前事实。

## 二、已知画像

### `cumcm-2026`

- `competition`: `CUMCM`
- `year`: `2026`
- 优先来源：
  - `CUMCM-2026-RULES`
  - `CUMCM-2026-FORMAT`
  - `CUMCM-2025-AI`
  - `CUMCM-2023-REVIEW-NORM`
  - `CUMCM-CHARTER`

#### 官方硬门槛摘要

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

#### 官方定性评审维度摘要

- 假设合理性
- 建模创造性
- 结果正确性
- 文字表述清晰程度

#### 画像提醒

- 官方没有公开统一数值权重
- `CUMCM-2025-AI` 是 2025 年试行规定，`CUMCM-2023-REVIEW-NORM` 是 2023 年修订稿；二者可适用于 2026 评审语境，但不要写成 2026 文档版本
- 需要正式年份判断时，优先使用 2026 官方页面；无法核验更新时写时效风险

### `comap-2026`

- `competition`: `COMAP MCM/ICM`
- `year`: `2026`
- 优先来源：
  - `COMAP-2026-INSTRUCTIONS`
  - `COMAP-AI-POLICY`
  - `COMAP-SUBMISSION`
  - `COMAP-FAQ`
  - `COMAP-TIPS`

#### 官方硬门槛摘要

- 单一英文 PDF
- 至少 12pt
- 第一页 Summary Sheet
- 控制号和页码
- 匿名
- AI 披露
- 文件小于 25MB
- 25 页上限，含摘要、正文、参考文献等；AI 报告例外按政策

#### 官方定性评审维度摘要

- Thought processes
- Problem analysis
- Modeling approaches
- Mathematical methods
- Summary Sheet 权重很高
- 假设、模型动机、测试/误差/敏感性/稳定性、优缺点、结果解释、组织清晰与引用

#### 画像提醒

- 官方没有公开统一数值权重
- 如果缺少英文 PDF、Summary Sheet、控制号/页码或 AI 披露证据，很多正式判断都只能降级为 `UNKNOWN`

### `generic-modeling-competition`

- `competition`: `Generic Modeling Competition`
- `year`: 由用户输入决定
- 适用场景：
  - 赛事不在本文件已知列表
  - 规则年份无法确认
  - 只做通用内容评审，不做强合规结论

#### 默认来源优先顺序

- 目标赛事的当前官方规则
- 目标赛事的官方说明
- `IMMC-RULES`
- `SIAM-M3-RULES`
- `SIAM-M3-TIPS`
- `GAIMME-2E`

这些来源只提供跨赛事、跨学段的定性启发；不得替代目标赛事官方规则，也不得提高官方合规结论置信度。

#### 通用硬门槛策略

- 未经当前赛事规则确认的提交格式、页数、语言、匿名、文件大小、AI 披露都优先判 `UNKNOWN`
- 只有证据直接支持时才判 `PASS` 或 `FAIL`

#### 通用定性评审维度

- 问题定义
- 假设/限制
- 变量/参数/单位
- 模型构建与方法选择
- 数学正确性
- 计算透明度和可复现性
- 结果解释
- 验证/敏感性/稳健性
- 局限与适用边界
- 组织表达与引用诚信

## 三、输出时的最小要求

- `competition_profile.profile_id` 选用本文件 ID
- `competition_profile.competition` 写竞赛名称
- `competition_profile.year` 写目标年份
- `competition_profile.rule_mode` 建议取值：
  - `user_current_official`
  - `current_official`
  - `older_official`
  - `official_guidance`
  - `educational_rubric`
  - `mixed`
