# Known Issues

每次使用 `game-ui-image-generator` 前先读本文件。遇到会导致返工、误解或后续拆解困难的问题，按模板追加。

## 新增记录模板

```markdown
### KI-YYYYMMDD-短名

- 状态：active / resolved / watch
- 触发条件：
- 问题表现：
- 根因：
- 预防规则：
- 修正动作：
- 验证方式：
- 来源：
```

## 记录区

### KI-20260707-too-pretty-not-splittable

- 状态：active
- 触发条件：只强调“好看”“高级”“氛围感”，没有要求元素可分离。
- 问题表现：图像视觉漂亮，但 UI 元素边界粘连、光效覆盖严重，后续无法稳定做 Sprite Plan。
- 根因：prompt 偏概念图，没有工程拆解约束。
- 预防规则：用于本项目时必须加入“UI elements should be visually separable for later standalone sprite generation”。
- 修正动作：重新生成时强调按钮、卡片、面板、icon、进度条、装饰件边界清楚。
- 验证方式：能否列出 8-20 个明确可拆 UI 元素。
- 来源：本项目目标定义。

### KI-20260707-garbled-text

- 状态：active
- 触发条件：prompt 中要求大量文字、小字、长句或多语言混排。
- 问题表现：AI 生成乱码、错字、伪文字，影响 UI 可信度。
- 根因：图像模型不适合大量精确文字排版。
- 预防规则：只保留少量关键短文本，并用 `Text (verbatim)` 明确列出；长文案留给后续 Text Node。
- 修正动作：减少文字数量，改成标题、按钮、数字、短 label。
- 验证方式：放大查看关键文字是否准确可读。
- 来源：游戏 UI 生图通用风险。

### KI-20260707-background-fights-ui

- 状态：active
- 触发条件：背景细节过多、对比过强或装饰穿过 UI 主体。
- 问题表现：主 UI 边缘不清楚，后续难以判断面板边界和元素归属。
- 根因：背景和 UI 主体竞争视觉焦点。
- 预防规则：背景应低对比、低复杂度，不能穿插核心 UI 边界。
- 修正动作：prompt 中加入“background supports the UI, lower contrast than foreground, no decorations crossing UI borders”。
- 验证方式：缩略图下仍能看清主面板和按钮边界。
- 来源：Mermaid Pass 类 UI 的后续拆分经验。

### KI-20260707-overcrowded-screen

- 状态：watch
- 触发条件：一个 UI 画面要求太多系统和状态。
- 问题表现：界面拥挤、元素变小、文字变多，难以拆解和复用。
- 根因：单张图承载过多功能。
- 预防规则：一张图聚焦一个核心界面或弹窗；复杂系统拆成多张图生成。
- 修正动作：减少组件数量，优先主面板、标题、核心奖励/商品、主按钮、货币/关闭按钮。
- 验证方式：主要元素能在 720x1280 下清晰辨认。
- 来源：游戏 UI 生图规划准则。

### KI-20260708-asset-sheet-index-labels

- 状态：active
- 触发条件：要求模型生成带有多格 asset sheet / sprite sheet / production board，并在 prompt 中写了 “cell list, in order”。
- 问题表现：模型会在每个 asset cell 左上角自动加绿色圆点、数字编号、标签或索引标记，即使 prompt 已要求 asset cells 不包含动态文字。
- 根因：模型把 “in order” 和列表编号理解成视觉标注，而不是纯排布顺序；production board 语境也会诱发设计稿式标注。
- 预防规则：asset sheet prompt 必须显式要求 “no visible cell labels, no numbers, no index markers, no captions, no badges, no annotation marks; order is implicit by grid position only”。
- 修正动作：重新生成时强化无标签约束；如果已经生成，后续切图/验证必须把编号标记当作污染物，不可进入 sprite。
- 验证方式：查看 asset sheet 原图和 `sprite_overview.png`，每个 cell 左上角不应有数字、圆点或文字标签。
- 来源：`spec_driven_panel_split_stability` run_03 中，asset sheet 自动生成了 `1` 到 `6` 的绿色编号圆点，污染多个 extracted sprite。

### KI-20260708-low-contrast-texture-cell-bbox

- 状态：active
- 触发条件：asset sheet 中包含浅色 parchment / cream / paper texture tile，并放在同样很浅的 neutral backing 上。
- 问题表现：生成图肉眼看 cell 是干净的，但后续复用旧粗 bbox 或 foreground-safe auto bbox 时，会把左侧背景、植物、分隔边界或 backing strip 裁进 texture sprite。
- 根因：低对比 texture 与浅色 backing 的色差太小，自动前景检测难以区分 cell backing、texture tile 和相邻背景；固定 bbox 跨 run 又会漂移。
- 预防规则：生成 production board 时，低对比 texture cell 要有更明确的 cell backing、足够 gutter、清晰内框或轻微可检测边界；不要让 texture cell 贴近 asset-sheet 左边界或 full-effect 区域。验证层优先使用 `asset_sheet_detection.mode: "grid_cell_foreground_safe_bbox"`，把跨 run 漂移当成 grid/cell 搜索框问题先处理。
- 修正动作：严格 prompt 不能单独解决；在 Layer Contract 中使用 `grid_cell_foreground_safe_bbox` 做板级检测，再保留 `bbox_detection_hint: "trim_saturated_left_edge_then_foreground"` 作为个别 cell 的回退路径。
- 验证方式：查看 `asset_sheet_detection.json` 和 `focused_split_comparison.png` 中的 `panel_inner_texture`，透明候选不应带入绿色/背景竖条，`green_ratio <= 0.02` 且 `corner_alpha_max == 0`。
- 来源：`spec_driven_panel_split_no_label_stability` run_01 和 run_03 中，no-label prompt 已去掉编号，但 `panel_inner_texture` 因 bbox/detection 漂移带入左侧植物/背景竖条；改用 `grid_cell_foreground_safe_bbox` 后 strict/no-label auto validation 达到 3/3。
