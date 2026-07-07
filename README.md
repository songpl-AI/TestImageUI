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
先输出 Sprite Plan，人工确认后再生成独立透明 PNG。
运行前读取 known_issues.md，遇到新坑要记录。
```

典型输出结构：

```text
output/<screen>_single_sprites/
  sprite_plan.md
  generated_src/
    <id>_chroma.png
  assets_png/
    <id>.png
  assets_fit_raw/
    <id>.png
  sprite_overview.png
```

其中：

- `generated_src/` 保存原始生成图，通常是 chroma-key 背景。
- `assets_png/` 保存最终独立透明 PNG。
- `assets_fit_raw/` 保存按目标 rect 装进透明画布后的版本，方便回贴。
- `sprite_overview.png` 用棋盘格背景展示每个独立 sprite。

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
4. 使用 Codex 或其它图像生成能力逐个生成独立 sprite。
5. 用 Python pipeline 重建并输出 comparison。
6. 将新问题写入 Known Issues。

这个项目的价值不在于“一次生成完美资产”，而在于把 AI UI 图拆解这件事变成一个可复盘、可审核、可迭代的工程流程。
