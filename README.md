# TestImageUI

这是一个用于验证 **AI 生成 UI 效果图如何工程化拆解为可复用游戏 UI 资产** 的实验项目。

项目关注的不是“把图片切成很多矩形块”，而是验证一条更接近真实游戏 UI 生产的流程：

```text
AI UI 效果图
  -> 语义分析 / Sprite Plan / Layer IR
  -> 生成或提取独立 UI sprite
  -> 保留动态文字为 Text Node
  -> 根据 layout 信息重建 UI
  -> 对比原图、直接裁图重建、干净资产重建
```

## 项目目的

AI 生成的 UI 效果图通常只有一张扁平图片。它不是 PSD、Figma、Spine 或游戏引擎 Prefab，因此天然缺少：

- 图层结构
- 父子节点关系
- 透明通道
- 组件语义
- 可复用资产
- 动态文字
- 九宫格 / 拉伸信息

如果只是把原图按 bbox 裁成一堆矩形 PNG，虽然可以像素级贴回原图，但这些资源通常包含背景、遮挡、文字和其它 UI 元素，无法直接作为工程资产复用。

本项目要验证的是：

- 哪些元素可以直接使用或透传
- 哪些元素需要重新生成干净 sprite
- 哪些内容必须保留为 Text Node
- 如何用结构化 IR 描述拆解和布局
- 如何用生成出的素材重建 UI 并做质量对比

## 核心原则

### 1. 不把矩形 crop 当成最终 sprite

矩形 crop 只能作为：

- 参考图
- bbox 调试图
- 重建校验素材
- Codex 生图任务的 reference crop

最终可用的 sprite 应该是独立、干净、可复用、通常带透明背景的 PNG，例如：

- 无子元素的面板底图
- 无文字的按钮底图
- 无文字的进度条底图
- 独立 icon
- 独立装饰件
- 固定艺术字标题

### 2. 先做 Sprite Plan，再生成素材

处理一张新的 UI 图前，应该先分析哪些元素需要拆成什么样的 sprite，并输出 `sprite_plan.md` 或等价清单。

计划中应区分：

- **自动确认**：工程规则非常明确，例如按钮底图去文字、动态数字保留 Text。
- **需要人工确认**：例如艺术字是否图片化、主面板是否拆成多个装饰件、复杂 icon 是否包含底座。

这样可以避免一上来就生成错误资产。

### 3. 动态文字不默认生成 PNG

以下内容默认保留为 Text Node：

- 数字
- 价格
- 进度值
- 倒计时
- 按钮文案
- 普通 label

只有固定艺术字、强视觉标题或用户明确要求图片化时，才生成文字 sprite。

## 当前项目结构

```text
.
├── ai_ui_split_pipeline_engineering_plan.md
├── codex_regenerate_workflow.md
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── core/
│   ├── ir/
│   ├── assets/
│   ├── reconstruction/
│   ├── exporters/
│   └── report/
├── examples/
│   ├── input/
│   └── output/
├── ui_split_demo/
└── .codex/
    └── skills/
        ├── game-ui-image-generator/
        └── ui-sprite-regenerator/
```

重点文件：

- `ai_ui_split_pipeline_engineering_plan.md`：完整工程实验方案。
- `codex_regenerate_workflow.md`：Codex 作为 regenerate provider 时的任务流。
- `src/main.py`：Python CLI 入口。
- `.codex/skills/game-ui-image-generator/SKILL.md`：项目内 Codex skill，定义“如何生成适合后续拆解的游戏 UI 效果图”。
- `.codex/skills/ui-sprite-regenerator/SKILL.md`：项目内 Codex skill，定义“生成独立 sprite 而不是矩形裁图”的规则。
- `.codex/skills/ui-sprite-regenerator/references/known_issues.md`：Known Issues 机制，记录已踩过的坑和防错规则。

## Python Pipeline

当前 Python CLI 支持：

```bash
python3 -m src.main --help
```

常用模式：

### 校验 Layer IR

```bash
python3 -m src.main \
  --input examples/input/shop_popup.png \
  --layer-ir examples/input/shop_popup.layer_ir.json \
  --output examples/output/shop_popup \
  --mode validate
```

### 生成 Codex 生图任务包

```bash
python3 -m src.main \
  --input examples/input/shop_popup.png \
  --layer-ir examples/input/shop_popup.layer_ir.json \
  --output examples/output/shop_popup_codex \
  --mode prepare-regenerate
```

输出包括：

- `assets_direct/`：直接裁图，用于像素重建校验。
- `assets_regenerated/`：无需生图的透传资产。
- `regen_tasks/`：每个待生成 sprite 的任务目录。
- `regen_tasks_manifest.md`：任务清单。
- `layout_ir.pending.json`：引用待生成资产的预览 Layout IR。
- `report.md`

每个 `regen_tasks/<id>/` 包含：

- `reference_crop.png`
- `prompt.txt`
- `task.json`

### 使用已有素材重建 UI

当 Codex 或人工把目标素材放入 `assets_regenerated/` 后：

```bash
python3 -m src.main \
  --input examples/input/shop_popup.png \
  --layer-ir examples/input/shop_popup.layer_ir.json \
  --output examples/output/shop_popup_codex \
  --mode rebuild
```

会生成：

- `reconstruction_direct.png`
- `reconstruction_regenerated.png`
- `comparison.png`
- `layout_ir.json`
- `report.md`

`rebuild` 会严格校验所需 PNG：缺失、无法读取或尺寸不匹配都会返回失败，并打印具体 layer。

注意：同一个 output 目录不要并发执行 `prepare-regenerate` 和 `rebuild`，避免读到未写完的 PNG。

### 验证 Spec-driven Layer Contract

当已经有一张 `full_effect + asset_sheet` production board，并希望验证 asset sheet 是否遵守工程层归属时，可以使用：

```bash
python3 -m src.main \
  --mode validate-contract \
  --contract examples/input/spec_driven_product_card_contract.json \
  --output examples/output/spec_driven_product_card_contract_validation
```

`layer_contract.json` 使用 `schemas/layer_contract.schema.json` 描述，核心字段包括：

- `board_image`：production board 路径。
- `asset_cells`：每个 asset sheet cell 的 `id`、`role`、`bbox`、`children_excluded`、`forbid_text`、`scale_mode`。
- `asset_sheet_detection`：可选，用粗 bbox 生成验证用的有效 bbox。`mode: "foreground_safe_bbox"` 会在每个粗 bbox 内自动寻找主体安全框，过滤贴边竖条、分隔线或背景残片；`mode: "grid_cell_foreground_safe_bbox"` 会先按 asset sheet 的行/列聚合检测饱和边缘 strip，得到每个 cell 的搜索框，再在搜索框内做 foreground-safe bbox，适合低对比 texture cell 的跨 run 漂移验证。
- `bbox_detection_hint`：可选的单个 `asset_cells[*]` 兜底提示；当前支持 `trim_saturated_left_edge_then_foreground`。优先使用 `grid_cell_foreground_safe_bbox` 做板级规则，只有个别 cell 无法从 grid/cell 规律恢复时再使用 hint。
- `text_nodes`：动态文字，例如价格、数量、折扣，不生成 PNG。
- `validation_checks`：机器检查项，例如 `red_ratio_hsv <= 0.01`、`corner_alpha_max == 0`、`label_artifact_score == 0`。
- `manual_checks`：人工已确认的视觉归属检查。
- `rough_reconstruction`：可选，用候选素材和 Text Node 组装一个粗重建。

输出包括：

- `asset_cells/`：asset sheet cell 审计 crop。
- `assets_png/`：从 cell 提取的透明候选 sprite。
- `assets_fit_raw/`：粗重建使用的 layout instance。
- `bbox_overlay.png`、`sprite_overview.png`、`focused_split_comparison.png`。
- 启用 `asset_sheet_detection` 时，额外输出 `layer_contract_input.json`、`asset_sheet_detection.json`、`bbox_detection_overlay.png`。
- `sprite_manifest.json`、`layer_ir.json`、`layout_ir.json`、`probe_metrics.json`、`probe_report.md`。

这个模式验证的是 **layer ownership contract 和证据链路**，不是最终生产资产质量。通过后仍需要进一步确认精确 bbox、九宫格参数、字体/描边参数、软边 alpha，以及是否要改用 per-asset 透明生成或人工修图。

`label_artifact_score` 是一个针对 production board asset sheet 的启发式污染检查：如果透明候选 PNG 左上角出现小型高饱和圆形/徽章状前景组件，通常代表模型把 cell 编号、索引标记或设计稿注释画进了素材。它不能替代 OCR 或人工审图，但可以把 `asset_sheet_index_label_artifacts` 这类已知失败从“漏检”变成合同失败。

当前有一个 grid-cell bbox 回归测试，使用 `tests/fixtures/panel_split_no_label/` 与 `tests/fixtures/product_card_grid_detection/` 下的最小 fixture，用于防止 `grid_cell_foreground_safe_bbox` 退化回 asset-specific hint、固定 bbox 漂移，或把 `price_tag_bg` 这类紧凑横向控件扩成整格背景：

```bash
python3 -m unittest tests.test_panel_split_grid_detection_regression
```

## Codex Skills

### Game UI Image Generator

项目新增了一个用于前置生图的 skill：

```text
.codex/skills/game-ui-image-generator/
```

它解决的问题是：生成一张游戏 UI 效果图时，不只追求“好看”，还要让它适合后续 `Sprite Plan`、`Layer IR`、独立 sprite 生成和 UI 重建。

核心约束：

- UI 元素语义清楚、边界清楚、层级清楚。
- 元素之间留出拆分空间，不要全部粘在一起。
- 背景服务 UI，不要干扰面板、按钮、卡片、icon 的边界。
- 文字少而准，动态文字保持短、清晰、可替换。
- 一张图聚焦一个屏幕或一个弹窗，不要塞太多系统。
- 生成前整理 `generation_brief`，明确 UI 类型、画布、组件清单、精确文字和后续拆解约束。

配套参考文件：

```text
.codex/skills/game-ui-image-generator/references/best_practices.md
.codex/skills/game-ui-image-generator/references/prompt_templates.md
.codex/skills/game-ui-image-generator/references/known_issues.md
```

### UI Sprite Regenerator

项目内置了一个 skill：

```text
.codex/skills/ui-sprite-regenerator/
```

它的核心约束：

```text
不要把原图矩形 crop 当成最终 sprite。
先输出 Sprite Plan，人工确认后先补 sprite manifest 与 Layout/Layer IR。
独立 sprite 的自然尺寸不等于工程尺寸，尺寸和位置必须由 IR 锁定。
运行前读取 known_issues.md，遇到新坑要记录。
```

典型输出结构：

```text
output/<screen>_single_sprites/
  sprite_plan.md
  sprite_manifest.json
  layer_ir.json
  layout_ir.json
  generated_src/
    <id>_chroma.png
  assets_png/
    <id>.png
  assets_fit_raw/
    <id>.png
  bbox_overlay.png
  sprite_overview.png
  reconstruction.png
  comparison.png
```

其中：

- `sprite_manifest.json` 保存人工确认后的可执行生成清单。
- `layer_ir.json` / `layout_ir.json` 保存 bbox、层级、锚点、Text Node 和资源引用。
- `generated_src/` 保存原始生成图，通常是 chroma-key 背景。
- `assets_png/` 保存最终独立透明源 sprite，按语义素材命名，允许复用。
- `assets_fit_raw/` 保存按 IR bbox 装进透明画布后的布局实例，方便回贴。
- `bbox_overlay.png` 把 bbox 画在源图上，用于人工检查大小、位置和层级。
- `sprite_overview.png` 用棋盘格背景展示每个独立 sprite。
- `reconstruction.png` / `comparison.png` 用于验证大小、位置、层级和视觉一致性。

## 示例数据

### Shop Popup

早期 controlled demo，用于对比：

- 原图
- 直接裁图 asset sheet
- 重生成 asset sheet
- direct reconstruction
- clean asset reconstruction
- 三栏 comparison

位置：

```text
ui_split_demo/
examples/input/shop_popup.png
examples/output/shop_popup/
examples/output/shop_popup_codex/
```

### Mermaid Pass

用于验证更复杂的 AI UI 图：

```text
examples/input/mermaid_pass_raw.png
examples/input/mermaid_pass.png
examples/input/mermaid_pass_raw.layer_ir.json
examples/output/mermaid_pass_single_sprites/
```

其中 `mermaid_pass_single_sprites/assets_png/` 是一次真正的独立 sprite 生成实验，不是矩形裁图。

### Casual Home

用于验证主界面 UI 的 Sprite Plan、人工确认、manifest、Layout/Layer IR 与 bbox overlay：

```text
examples/input/casual_home.png
examples/input/casual_home_raw.png
examples/output/casual_home_single_sprites/
```

这一组样例特别用于验证两件事：

- AI 生成的独立 sprite 自然尺寸不等于工程尺寸。
- 可复用源素材和布局实例要分开，例如 `assets_png/star_slot.png` 可以生成多个 `assets_fit_raw/star_slot_*.png`。

### SLG Main

用于验证横屏 SLG 主界面的完整链路：

```text
examples/input/slg_main_raw.png
examples/input/slg_main.png
examples/output/slg_main_single_sprites/
```

当前已完成：

- `sprite_plan.md`：Sprite Plan。
- `sprite_manifest.json`：40 个源 sprite 的生成清单。
- `layer_ir.json` / `layout_ir.json`：105 个布局节点，其中 40 个 Text Node、4 个 ignore hit area。
- `assets_png/`：40 个独立源素材，不是源图矩形切块。
- `assets_fit_raw/`：61 个按 Layer IR bbox 回贴的布局实例。
- `sprite_overview.png`、`reconstruction.png`、`comparison.png`：资产总览和回贴对比。

这组样例暴露了一个关键边界：当前方案可以把一张扁平 AI UI 图工程化拆成独立 sprite，但无法保证重新生成的独立素材在视觉上等同于原图那次全局生成结果。差距通常体现在整体材质、描边厚度、字体、阴影、icon 占比、色彩饱和度和细节密度，而不是某几个红框局部。

### SLG Fidelity Experiment

为避免过度设计，先做了一个低成本上限实验：

```text
examples/output/slg_main_fidelity_experiment/
```

实验只选两个组件：

- `top_resource_strip`：顶部四个资源条作为一个组合控件候选。
- `build_nav_button`：底部 BUILD 按钮作为一个组合控件候选。

输出：

- `focused_component_comparison.png`：source / current / crop proxy 三栏局部对比。
- `full_hybrid_proxy_comparison.png`：source、当前独立 sprite 重建、只替换两个 proxy 区域后的整图对比。
- `experiment_manifest.json`：组件 bbox、输入、输出和简单 RGB delta。

重要说明：`proxy_crops_not_final_sprites/` 中的文件是源图 crop proxy，只用于判断组合控件路线的上限收益，不能作为最终可复用 sprite。它们的价值是回答一个窄问题：如果组合控件替换能明显减少漂移，再继续做真实的组合控件重生成；如果不能，就不要继续增加复杂度。

当前实验观察：

- `top_resource_strip` 当前重建与源图差距明显，平均 RGB delta 约 57.61；proxy 贴回后局部接近源图。
- `build_nav_button` 当前重建与源图差距明显，平均 RGB delta 约 45.20；proxy 贴回后按钮字重、icon 占比和底板关系都回到源图状态。
- 这说明“组合控件优先”对高保真视觉有收益，但 crop proxy 只能作为上限参照，下一步若继续，应生成真正的组合控件 sprite，而不是直接使用 crop。

### Build Nav Button Realgen Experiment

在 crop proxy 上限实验之后，针对 `build_nav_button` 做了一次真实组合 sprite 生成实验：

```text
examples/output/slg_main_build_nav_button_realgen/
```

输出：

- `assets_png/build_nav_button_composite.png`：真实生成并去底后的组合 sprite，不是源图 crop。
- `assets_fit_raw/build_nav_button_composite.png`：fit 到 `[320, 560, 130, 152]` bbox 的布局实例。
- `focused_realgen_comparison.png`：source / current / crop proxy / real generated composite 四栏局部对比。
- `full_realgen_comparison.png`：整屏对比。
- `experiment_manifest.json`：生成源、bbox、输出和指标。

指标，均为与 source crop 的平均 RGB delta：

- 当前独立 sprite 重建：45.20
- crop proxy 上限：0.00
- 真实生成组合 sprite：53.61

这次结果很有价值：真实生成组合 sprite 的结构是完整的，也确实避免了多 layer 组装错位，但它没有接近 crop proxy 上限。主要问题是生成结果比源图更高清、更厚重、更接近大号方形按钮，`BUILD` 字体和 hammer 占比也发生了漂移。

因此目前只能得出一个谨慎结论：组合控件路线可以减少“拆太细导致的组装漂移”，但单次泛化 AI 生成并不能保证源图级高保真。后续若继续，应优先尝试更窄的策略，例如“按钮底与 icon 组合生成、文字仍用 Text Node”或“使用更强 reference/edit/inpaint 路径”，而不是直接全屏推广组合 sprite。

### Build Nav Button Decomposed Realgen Experiment

随后按更工程化的边界测试了：

```text
button_bg + hammer_icon + badge_dot + Text Node
```

位置：

```text
examples/output/slg_main_build_nav_button_decomposed/
```

输出：

- `assets_png/build_button_bg.png`：无 icon、无红点、无文字的按钮底板。
- `assets_png/build_hammer_icon.png`：独立 hammer icon。
- `assets_png/build_badge_dot.png`：独立红点 badge。
- `assets_fit_raw/`：按实验 bbox fit 后的布局实例。
- `focused_decomposed_comparison.png`：source / current / crop proxy / whole realgen / decomposed realgen 五栏局部对比。
- `full_decomposed_comparison.png`：整屏对比。

指标，均为与 source crop 的平均 RGB delta：

- 当前独立 sprite 重建：45.20
- crop proxy 上限：0.00
- 整按钮真实生成：53.61
- 拆分真实生成 + Text Node：45.64

这次实验说明：拆成 `button_bg + hammer_icon + badge_dot + Text Node` 的边界更符合工程目标，也避免了整按钮烘焙文字的问题，但它并没有明显优于当前独立 sprite 重建。主要原因仍是生成出来的底板、锤子和红点比源图更厚重、更高清、更干净，素材本身的风格漂移没有消失。

因此当前更准确的判断是：拆分边界可以解决可编辑性和组装结构问题，但不能单独解决源图级视觉还原问题。若继续追求高保真，下一步应比较“参考引导/编辑式生成”或“从源图局部 clean-up / inpaint 提取”是否比重新生成更接近源图，而不是继续调整拆分粒度。

### Build Button BG Cleanup Experiment

为了验证“参考引导/编辑式生成”是否能改善漂移，又做了一次更窄的小实验：

```text
examples/output/slg_main_build_button_bg_cleanup/
```

实验只替换 `build_button_bg`：

- 输入参考：`build_nav_button_source_reference_crop.png`。
- 目标：删除锤子、红点、`BUILD` 文案和地图背景，只保留干净按钮底板。
- 最终资产：`assets_png/build_button_bg_cleanup.png`，透明 PNG，不是源图 crop。
- 回贴方式：复用上一轮的 hammer icon、badge dot，并继续用 Text Node 绘制 `BUILD`。

指标，均为与 source crop 的平均 RGB delta：

- 当前独立 sprite 重建：45.20
- crop proxy 上限：0.00
- 整按钮真实生成：53.61
- 拆分真实生成 + Text Node：45.64
- cleanup/inpaint 按钮底板 + 复用 icon/Text：47.56

这次结果没有改善视觉相似度。它成功生成了工程上干净的按钮底板，但模型把源图中的小按钮“修正”为更规整、更厚、更高清的标准按钮底板，导致回贴后仍然不像原图。这个结果说明：只把局部 crop 作为参考，再让模型清理/补全，并不能稳定达到 crop proxy 的上限；被遮挡区域仍然会被模型按自己的 UI 先验重画。

### Top Resource Strip Realgen Experiment

为了换一个不同类型组件，又测试了顶部资源条：

```text
examples/output/slg_main_top_resource_strip_realgen/
```

这次没有生成带数字的整条 crop，而是做了一个更接近工程可用的组合 sprite：

- `assets_png/top_resource_strip_frame.png`：透明组合 sprite，包含四个资源 icon、四个资源条底板、四个绿色加号。
- 不包含 `WOOD` / `FOOD` / `GOLD` / `GEMS` 标签。
- 不包含 `2.5M` / `3.2M` / `4.7M` / `1,250` 数值。
- 标签和数值仍然通过 Text Node 回贴。
- 背景天空不进入 sprite；对比时使用源图可见天空估算了一个 clean background。

指标：

- 当前独立 sprite 重建，全 crop delta：57.61
- crop proxy 上限，全 crop delta：0.00
- realgen frame + Text Nodes，全 crop delta：53.92
- 当前独立 sprite 重建，UI mask delta：60.78
- realgen frame + Text Nodes，UI mask delta：58.34

这次结果比当前独立 sprite 略好，但提升很小，仍远没有接近 crop proxy 上限。主要偏差不是透明处理，而是模型重新排版了多槽位控件：资源条变得更长、更均匀，icon 风格和颜色发生漂移，例如宝石从紫色偏成了银蓝色，gold icon 也变成了更标准的圆章。

因此对 `top_resource_strip` 的判断是：组合控件 sprite 对宽 HUD 区域可能有一点收益，但不能稳定锁住源图中的 spacing、icon identity、条宽和材质细节。它适合做“更像游戏 UI 的 mock 资产”，不适合直接承诺源图级高保真还原。

### Build Nav Button Visual Extract Experiment

在 `codex/source-preserving-sprite-extract` 分支上又测试了一个不同路线：

```text
examples/output/slg_main_build_nav_button_visual_extract/
```

这次不再让 AI 重新生成按钮，而是做 `source_preserving_mask_extract`：

- 从 source crop 保留 BUILD 按钮的原图像素。
- 用非矩形 alpha mask 去掉按钮外部地图背景。
- 输出 `assets_png/build_nav_button_visual_state.png`，透明 PNG，不是矩形 crop。
- 保留锤子、红点和 `BUILD` 文案，属于 `visual_state_sprite`。
- 位置仍由 Layer IR / Layout IR 记录，后续允许手动调。

指标，均为与 source crop 的平均 RGB delta：

- 当前独立 sprite 重建：45.20
- crop proxy 上限：0.00
- 拆分真实生成 + Text Node：45.64
- cleanup/inpaint 按钮底板 + 复用 icon/Text：47.56
- visual extract 贴回 source 背景：0.00
- visual extract 贴回当前重建底图：4.63
- visual extract 贴回当前重建底图，只看 alpha mask 区域：1.56

这次结果说明：如果目标从“干净可复用工程拆分资产”改成“生成图至少要像效果图”，源图像素保留 + 非矩形透明提取是明显更有效的路线。它的代价是复用性和可编辑性下降，因为文字、icon 和状态被烘焙进了同一张视觉态 sprite。

### Build Nav Button Layered Source Extract Experiment

随后按“先识别图层关系，再拆分还原”的目标做了一次真正分层实验：

```text
examples/output/slg_main_build_nav_button_layered_source_extract/
```

拆分关系：

```text
build_nav_button_group
  build_button_bg_source_clean
  build_hammer_icon_source_extract
  build_badge_dot_source_extract
  build_label Text Node
  build_label_fixed_art_source_extract  # optional fidelity check
```

这次不是整按钮视觉态，也不是矩形 crop，而是：

- `build_button_bg_source_clean.png`：保留源图可见底板像素，只对锤子、红点、BUILD 文字遮挡区域做局部补洞。
- `build_hammer_icon_source_extract.png`：从源图非矩形 mask 提取锤子。
- `build_badge_dot_source_extract.png`：从源图非矩形 mask 提取红点。
- `build_label`：默认仍是 Text Node。
- `build_label_fixed_art_source_extract.png`：额外输出的固定文字层，只用于判断文字渲染漂移影响。
- `reference_package/`：保存源局部截图、target mask、exclude mask 和后续 crop + prompt + mask 增强生成所需材料。

指标，均为与 source crop 的平均 RGB delta：

- 当前独立 sprite 重建：45.20
- 拆分真实生成 + Text Node：45.64
- cleanup/inpaint 按钮底板 + 复用 icon/Text：47.56
- 整组件 visual state extract：4.63
- layered source extract + Text Node：28.69
- layered source extract + fixed text：22.66

这说明 layer-first source extract 明显优于纯 AI 重新生成，但仍不如整组件视觉态。主要残差来自两个地方：

- 底板被锤子和文字遮挡的区域无法从扁平图真实恢复，只能局部补洞。
- Text Node 字体与源图固定文字存在差异；改用 fixed text 后 delta 从 28.69 降到 22.66，但会牺牲可编辑性。

因此这条路线适合继续发展为 `visual_state_sprite + engineering_layers + reference_package` 的双轨方案：既保留可还原的图层关系，又给每个困难 layer 留出 crop + mask + prompt 的增强入口。

### Build Nav Button SAM/rembg Extract Experiment

为了验证第三方工具是否能改善“手工 mask 粗糙”的问题，又做了一次最小闭环实验：

```text
examples/output/slg_main_build_nav_button_sam_rembg_extract/
```

本轮使用本机 Python 3.12 临时环境，跑通：

- `facebook/sam2.1-hiera-tiny`：用于 promptable segmentation，设备为 Apple Silicon MPS。
- `rembg u2netp`：用于 hammer、badge 和整按钮视觉态的 alpha/edge refine。
- OpenCV / 区域采样填充：只用于底板被锤子、红点和文字遮挡后的非生成式近似补洞。
- 未使用 LaMa，也没有做生成式 inpaint。

拆分关系仍然保持工程层结构：

```text
build_nav_button_group
  build_button_bg_sam_clean
  build_hammer_icon_sam_rembg_extract
  build_badge_dot_sam_rembg_extract
  build_label Text Node
  build_label_fixed_art_sam_extract      # optional fidelity check
  build_nav_button_visual_state_sam_rembg # diagnostic only
```

关键输出：

- `sprite_plan.md`
- `sprite_manifest.json`
- `layer_ir.json`
- `layout_ir.json`
- `bbox_overlay.png`
- `sprite_overview.png`
- `focused_sam_rembg_extract_comparison.png`
- `debug/sam2_candidate_mask_overview.png`
- `reference_package/`

指标，均为与 source crop 的平均 RGB delta：

- 当前独立 sprite 重建：45.20
- previous layered source extract + Text Node：28.69
- previous layered source extract + fixed text：22.66
- SAM/rembg layered + Text Node：21.89
- SAM/rembg layered + fixed text：15.84
- SAM/rembg visual-state diagnostic：10.24
- SAM/rembg visual-state diagnostic，只看 alpha mask 区域：0.97

这次结果说明：

- SAM2 对 `hammer_icon`、`badge_dot`、`label` 这类可见前景层有明显帮助，比手工 mask 稳定。
- rembg 适合作为 alpha/edge refine，不适合单独决定图层语义。
- fixed text 对照从 22.66 降到 15.84，说明前景层 mask/refine 确实改善了图层拆分质量。
- 默认 Text Node 从 28.69 降到 21.89，但仍受字体、描边、字重匹配影响。
- 视觉态诊断的 alpha-mask delta 只有 0.97，说明“源图像素 + 非矩形 mask”仍是视觉还原上限最高的低成本路线。
- 底板的隐藏像素仍然无法由 SAM/rembg 恢复。`build_button_bg_sam_clean.png` 可以成为独立底板近似资产，但遮挡区域只能采样/补洞，不能等同于真实 PSD 背后图层。

因此这轮实验的结论不是“第三方工具能直接自动 PSD 化”，而是：**SAM/rembg 值得接入 layer-first workflow，用来降低 mask 粗糙度；但底板补洞仍需要 LaMa/人工修图/设计源文件等另一类能力单独解决。**

### Build Nav Button LaMa Inpaint Experiment

在 SAM/rembg 已经改善前景 mask 后，又做了一次更窄的 LaMa 实验：

```text
examples/output/slg_main_build_nav_button_lama_inpaint_extract/
```

本轮只替换 `button_bg` 的遮挡补洞，不重新生成整按钮，也不重新生成锤子、红点或文字：

- `build_button_bg_lama_clean.png`：用 SAM button mask + child exclude mask + LaMa 补洞得到的底板。
- `build_hammer_icon_sam_rembg_extract.png`：复用上一轮 SAM/rembg 锤子层。
- `build_badge_dot_sam_rembg_extract.png`：复用上一轮 SAM/rembg 红点层。
- `build_label`：默认仍为 Text Node。
- `build_label_fixed_art_sam_extract.png`：只作为 fixed text 指标对照。

工具环境：

- `simple-lama-inpainting 0.1.2`
- `big-lama.pt`
- Apple Silicon MPS
- 临时 Python 环境中安装时会拉低 Pillow/Numpy 版本，后续若保留应单独建 LaMa 环境，不要和 rembg/SAM 共用一个默认环境。

指标，均为与 source crop 的平均 RGB delta：

- 当前独立 sprite 重建：45.20
- manual layered + Text Node：28.69
- SAM/rembg layered + Text Node：21.89
- LaMa layered + Text Node：20.67
- manual layered + fixed text：22.66
- SAM/rembg layered + fixed text：15.84
- LaMa layered + fixed text：14.59
- visual-state diagnostic：10.24

LaMa 相比 SAM/rembg 的提升是存在的，但幅度不大：

- Text Node：21.89 -> 20.67
- fixed text：15.84 -> 14.59

观察结论：

- LaMa 能让底板遮挡洞比区域采样更自然一点。
- 但它仍然是根据上下文“猜”隐藏像素，不是恢复真实底板图层。
- 如果 mask 没有覆盖锤子的投影/阴影，`button_bg` 里仍会残留暗影痕迹；这不是 LaMa 自动能判断的图层归属问题。
- 扩大 mask 会删除更多阴影，但也更容易重画金边、面板纹理和材质，产生新的漂移。

因此 LaMa 更适合作为**困难底板的小范围补洞候选**，不应该成为默认的整组件重画方案。后续如果继续提升，需要先把 `shadow` 明确成跟随锤子的子层或单独 shadow layer，再决定是否由 LaMa 补掉底板上的投影残留。

### Build Nav Button Hammer Shadow Layer Attribution Experiment

随后按 `hammer_icon + hammer_shadow + button_bg` 做了一次 layer 归属实验：

```text
examples/output/slg_main_build_nav_button_shadow_layer_extract/
```

本轮目标不是继续换模型，而是验证一件更具体的事：

```text
button_bg_shadow_clean
hammer_shadow
hammer_icon
badge_dot
BUILD Text Node / fixed text optional
```

实验做法：

- 用上一轮最终 `hammer_icon` alpha 保护锤子本体。
- 在锤子附近寻找源图相对 clean bg 更暗的区域，生成 `hammer_shadow_mask_small` / `hammer_shadow_mask_medium` 两个候选。
- `button_bg_shadow_clean` 使用 LaMa 对“实体 + shadow”区域补洞，尝试得到不带锤子投影的底板。
- `hammer_shadow` 作为独立半透明暗色层，放在 `button_bg` 与 `hammer_icon` 之间。
- 锤子、红点、fixed text 仍复用上一轮 SAM/rembg 资产。

指标，均为与 source crop 的平均 RGB delta：

- previous LaMa + Text Node：20.67
- shadow small + Text Node：20.80
- shadow medium + Text Node：21.42
- previous LaMa + fixed text：14.59
- shadow small + fixed text：14.71
- shadow medium + fixed text：15.33
- visual-state diagnostic：10.24

这次是一个负向/边界实验：**自动拆 shadow 没有提升，反而略差**。

原因：

- 自动 shadow mask 很难只抓投影；small 太弱，medium 会抓到不该重画的暗部。
- 一旦把 shadow 也从底板里 mask 掉，LaMa 会在底板上产生新的伪影。
- 单独的 `hammer_shadow` 半透明层很难用简单暗色 overlay 精确复现源图的接触阴影、软边和局部材质变化。
- 指标和肉眼都说明：在当前自动方案下，shadow 单独成层不比“让少量 shadow 残留在底板/图标关系中”更好。

因此当前更稳的工程结论是：

- 不要自动把所有 shadow 都拆成独立 sprite。
- 对小按钮这类紧密组合控件，如果没有 PSD/人工修图，shadow 更适合作为人工确认项。
- 高保真优先时继续使用 `visual_state_sprite`。
- 工程拆分优先时，保持 `button_bg + hammer_icon`，但把 shadow 归属标为 `needs_manual_shadow_review`，不要让程序自动决定。

## 当前方案边界

这里的“当前方案”指：

```text
AI UI 效果图
  -> Sprite Plan
  -> sprite_manifest / Layer IR / Layout IR
  -> 独立重生成 assets_png
  -> fit 到 assets_fit_raw
  -> Text Node 回贴重建
```

### 能做到

- 锁定布局位置、尺寸、层级和 Text Node。
- 明确区分 `assets_png` 源素材和 `assets_fit_raw` 布局实例。
- 生成干净、透明、语义命名的独立 PNG 素材。
- 将动态文字、数字、进度值、按钮文案保留为可编辑 Text Node。
- 支持同一源素材复用到多个布局实例。
- 输出 `bbox_overlay.png`、`sprite_overview.png`、`reconstruction.png`、`comparison.png` 供人工审核。
- 让结果达到“工程结构可复盘、可迭代、可定位问题”的状态。
- 生成风格相近的游戏 UI 素材族，适合做 mock、原型或二次美术参考。
- 接入 SAM/rembg 这类第三方工具后，可以更稳定地获得非矩形前景 mask、alpha 边缘和视觉态 sprite。

### 确定做不好

- 不能保证重新生成的独立 sprite 与原图像素级一致。
- 不能稳定复刻原图那次全局生成中的精确笔触、统一光照、材质颗粒、阴影和描边。
- 不能从单张扁平图中恢复被文字、icon、其它 UI 遮挡住的真实底板内容。
- SAM/rembg 只能分割和 refine 可见像素，不能恢复被遮挡的隐藏图层。
- 不能靠简单 bbox fit 解决所有比例问题，尤其是资源条、按钮、面板金边这类需要九宫格或精确设计稿的元素。
- 不能同时最大化“最细粒度复用”和“整屏几乎等同源图”。拆得越细，组合后的视觉漂移通常越明显。
- 不能保证 AI 生成的固定艺术字、字体描边、投影和原图一致；高保真标题更适合单独作为 fixed art text 或使用真实字体资产。

### 未知问题

- LaMa 或其它 inpaint 工具是否能在小范围底板遮挡补洞上稳定优于区域采样和 OpenCV。
- 哪些组件应该保持组合控件，哪些组件拆细后仍然收益更高。
- 组合控件 sprite 与动态 Text Node 覆盖之间的最佳边界。
- 是否需要引入九宫格元数据，还是只对少量高价值底板手工标记即可。
- 对不同 UI 类型，当前独立 sprite 流程的视觉漂移阈值是否一致。

`build_nav_button` 的真实生成实验已经说明：至少对一个小型底部按钮来说，单次组合控件生成没有接近 crop proxy 上限。这个结果不代表组合控件路线无效，但说明它需要更强约束或更细的边界选择。

后续的 `button_bg + hammer_icon + badge_dot + Text Node` 实验进一步说明：更细的工程边界能恢复可编辑性，但并不能自动提高视觉相似度；如果底层生成素材本身漂移，最终回贴仍会漂。

后续的 `build_button_bg_cleanup` 实验继续说明：局部 crop 参考 + edit/cleanup/inpaint 可以得到更干净的工程 sprite，但仍可能被模型重画成“标准按钮模板”，并不稳定复刻源图的厚度、比例、磨损和材质密度。

`top_resource_strip_frame` 的实验说明：换成不同类型的宽 HUD 资源条后，组合控件真实生成有小幅改善，但仍会把多槽位布局重新排版，并且会改变 icon identity 与颜色。也就是说，问题不只存在于底部按钮类控件。

`build_nav_button_visual_state` 的实验说明：如果允许使用源图像素并输出视觉态 sprite，就能显著接近原效果图。这个策略不是 AI 重新生成，也不是矩形 crop，而是非矩形 mask 提取。它适合视觉还原优先的场景，但不适合需要动态文字、多语言和高度复用的正式工程资产。

`build_nav_button_layered_source_extract` 的实验说明：在保持图层关系的前提下，source extract 可以显著降低视觉漂移，但只要底板存在大面积遮挡，干净底板仍然需要补洞；补洞质量会成为主要瓶颈。局部截图 + mask + prompt 的增强生成应该只作用在这些困难 layer 上，而不是重新生成整张组件。

`build_nav_button_sam_rembg_extract` 的实验说明：第三方 segmentation/refine 能显著改善前景层 mask，把 layered + Text Node 从 28.69 降到 21.89，把 layered + fixed text 从 22.66 降到 15.84；但它仍不能恢复底板被遮挡的真实像素。下一步若继续，应只对 `button_bg` 的遮挡洞测试 LaMa/人工修图，不要再把整组件交给生成模型重画。

`build_nav_button_lama_inpaint_extract` 的实验说明：LaMa 对 `button_bg` 遮挡洞有小幅改善，把 SAM/rembg layered + Text Node 从 21.89 降到 20.67，把 fixed text 从 15.84 降到 14.59；但视觉上仍没有接近 visual-state diagnostic 的 10.24。它还暴露了一个更具体的问题：锤子的投影/阴影如果没有被识别为子层，底板 sprite 仍会残留暗影。因此下一步不应该继续盲目换 inpaint 模型，而应该先把 shadow 归属纳入 Layer IR。

`build_nav_button_shadow_layer_extract` 的实验说明：把 `hammer_shadow` 自动拆成独立层并没有提升，previous LaMa + fixed text 为 14.59，shadow small + fixed text 为 14.71，shadow medium + fixed text 为 15.33。也就是说，当前自动 shadow mask + LaMa 补洞会引入新的底板伪影，不能作为默认方案。shadow 归属必须成为人工确认项，或依赖 PSD/人工修图。

### 低复杂度迭代建议

优先不要全屏返工。`build_nav_button` 已经连续验证了三条低成本真实生成路径：

- 整按钮真实生成。
- `button_bg + hammer_icon + badge_dot + Text Node` 拆分生成。
- 局部 crop 参考下的按钮底板 cleanup/inpaint。

三者都没有接近 crop proxy 上限，所以不建议继续在同一个按钮上堆更多 prompt 细节。`top_resource_strip` 作为不同组件类型也只带来小幅收益，没有改变整体判断。

当前更合理的结论是：不要把全屏自动生成式高保真还原作为主要路线。后续若继续，应转向更确定的替代方案，例如人工修图/PSD 化、从原图做受控分割 + 手工补遮挡、建立 style/material sheet 后重新设计整套资产，或只把当前流程定位为 mock/原型资产生成。

如果目标调整为“先看起来像效果图，位置和复用性可以后续手动处理”，则应优先尝试 `visual_state_extract`：

- 对关键按钮、资源条、徽章、任务面板等先提取视觉态 sprite。
- 动态文字和可复用拆分资产作为第二套工程化输出，不强行和视觉态输出合并。
- 在计划中明确区分 `visual_state_sprite` 和 `engineering_sprite`，避免误把视觉态资产当成长期可复用组件。

如果目标是继续工程化拆层，则优先把 SAM/rembg 固化为 mask/refine 辅助步骤，再只针对少数被遮挡底板做 LaMa/人工修图小实验。不要在前景 mask 已经可用时继续堆 prompt 生成整按钮。

## 核心数据结构

### Layer IR

描述拆图阶段的问题：

- 元素 id
- role
- bbox
- asset_strategy
- 是否透明
- 是否去文字
- 是否被子元素遮挡
- 是否九宫格候选
- 是否是 Text Node

常见策略：

- `direct_crop`
- `segmentation_extract`
- `regenerate`
- `regenerate_or_inpaint`
- `inpaint_background`
- `text_node`
- `vector_shape`
- `ignore`

### Layout IR

描述引擎重建阶段的问题：

- UI 节点
- 节点类型
- rect
- asset 引用
- text 内容
- anchor
- children hint

后续可以接 Unity、Cocos、UE UMG 等 exporter。

## Known Issues 机制

`.codex/skills/ui-sprite-regenerator/references/known_issues.md` 用于记录实际运行中的坑。

已记录的问题包括：

- 矩形 crop 不是 sprite
- 必须先出 Sprite Plan
- Sprite Plan 之后必须补 Layout/Layer IR 锁定大小、位置和层级
- `assets_png` 源素材和 `assets_fit_raw` 布局实例不能混淆
- raw 图和标准化图不要混用
- 动态文字不要生成 PNG
- 重建前素材必须齐全且尺寸匹配
- prepare/rebuild 不要并发写同一目录
- chroma-key 颜色冲突风险

后续每次遇到会导致返工、误解或结果不可用的问题，都应该按模板补充进去。

## 当前非目标

当前阶段不追求：

- 全自动识别所有 UI 元素
- 一键生成可上线 Prefab
- 完美 matting / alpha
- 完美 inpaint
- 完美九宫格识别
- 完全替代美术或 UI 程序审核

当前阶段追求的是：

- 流程可审核
- 中间产物结构化
- 错误可以被定位
- 直接裁图、重生成、Text Node 的边界清晰
- 能逐步接入真实 AI 生图和引擎 exporter

## 推荐使用方式

1. 放入一张 AI UI 效果图。
2. 先用 `ui-sprite-regenerator` 输出 Sprite Plan。
3. 人工确认需要拆分和生成的元素。
4. 补 `sprite_manifest.json`、`layer_ir.json` 和 `layout_ir.json`，锁定 bbox、层级、锚点和 Text Node。
5. 生成 `bbox_overlay.png`，人工检查 bbox 是否合理。
6. 使用 Codex 或其它图像生成能力逐个生成独立 sprite 到 `assets_png/`。
7. 把独立 sprite fit 到 IR bbox，生成 `assets_fit_raw/`。
8. 用 Python pipeline 重建并输出 comparison。
9. 将新问题写入 Known Issues。

这个项目的价值不在于“一次生成完美资产”，而在于把 AI UI 图拆解这件事变成一个可复盘、可审核、可迭代的工程流程。
