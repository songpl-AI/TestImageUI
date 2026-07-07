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

### 确定做不好

- 不能保证重新生成的独立 sprite 与原图像素级一致。
- 不能稳定复刻原图那次全局生成中的精确笔触、统一光照、材质颗粒、阴影和描边。
- 不能从单张扁平图中恢复被文字、icon、其它 UI 遮挡住的真实底板内容。
- 不能靠简单 bbox fit 解决所有比例问题，尤其是资源条、按钮、面板金边这类需要九宫格或精确设计稿的元素。
- 不能同时最大化“最细粒度复用”和“整屏几乎等同源图”。拆得越细，组合后的视觉漂移通常越明显。
- 不能保证 AI 生成的固定艺术字、字体描边、投影和原图一致；高保真标题更适合单独作为 fixed art text 或使用真实字体资产。

### 未知问题

- 用真实 AI 重新生成“组合控件 sprite”能否稳定接近 crop proxy 的上限。
- 哪些组件应该保持组合控件，哪些组件拆细后仍然收益更高。
- 组合控件 sprite 与动态 Text Node 覆盖之间的最佳边界。
- 是否需要引入九宫格元数据，还是只对少量高价值底板手工标记即可。
- 对不同 UI 类型，当前独立 sprite 流程的视觉漂移阈值是否一致。

`build_nav_button` 的真实生成实验已经说明：至少对一个小型底部按钮来说，单次组合控件生成没有接近 crop proxy 上限。这个结果不代表组合控件路线无效，但说明它需要更强约束或更细的边界选择。

后续的 `button_bg + hammer_icon + badge_dot + Text Node` 实验进一步说明：更细的工程边界能恢复可编辑性，但并不能自动提高视觉相似度；如果底层生成素材本身漂移，最终回贴仍会漂。

后续的 `build_button_bg_cleanup` 实验继续说明：局部 crop 参考 + edit/cleanup/inpaint 可以得到更干净的工程 sprite，但仍可能被模型重画成“标准按钮模板”，并不稳定复刻源图的厚度、比例、磨损和材质密度。

`top_resource_strip_frame` 的实验说明：换成不同类型的宽 HUD 资源条后，组合控件真实生成有小幅改善，但仍会把多槽位布局重新排版，并且会改变 icon identity 与颜色。也就是说，问题不只存在于底部按钮类控件。

### 低复杂度迭代建议

优先不要全屏返工。`build_nav_button` 已经连续验证了三条低成本真实生成路径：

- 整按钮真实生成。
- `button_bg + hammer_icon + badge_dot + Text Node` 拆分生成。
- 局部 crop 参考下的按钮底板 cleanup/inpaint。

三者都没有接近 crop proxy 上限，所以不建议继续在同一个按钮上堆更多 prompt 细节。`top_resource_strip` 作为不同组件类型也只带来小幅收益，没有改变整体判断。

当前更合理的结论是：不要把全屏自动生成式高保真还原作为主要路线。后续若继续，应转向更确定的替代方案，例如人工修图/PSD 化、从原图做受控分割 + 手工补遮挡、建立 style/material sheet 后重新设计整套资产，或只把当前流程定位为 mock/原型资产生成。

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
