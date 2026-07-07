---
name: ui-sprite-regenerator
description: 从 AI 生成的游戏 UI 效果图或合成 UI 图中规划并生成干净、独立、可复用的 sprite / 单图 / 贴图 / UI 素材 / 工程切图，并用 Layout IR / Layer IR 锁定尺寸、位置、层级和回贴验证。用户提到切图、单图、sprite、贴图、UI 素材、工程切图、从效果图拆资产、生成独立 PNG、还原 UI 等任务时使用。必须先分析图片并输出待确认的 Sprite Plan，人工确认后先补 sprite manifest 与布局 IR，再生成透明 PNG；不要把原图矩形裁切块当成最终 sprite。
---

# UI Sprite Regenerator

## 核心规则

不要把原始 UI 图按矩形切开后，当成最终 sprite。

合格的 sprite 必须是一个独立 UI 素材：干净、可复用、通常带透明背景，并且只包含目标元素本身。例如：

- 干净面板底图，不包含子元素
- 标题牌底图，不包含标题文字
- 固定艺术字标题，单独作为图片
- 按钮底图，不包含按钮文案
- 奖励 icon，不包含卡片背景
- 进度条底图，不包含数字
- 货币条底图，不包含 icon、加号按钮或数字

矩形 crop 只能作为参考图、bbox 调试图或重建校验图，不能冒充最终 sprite。

AI 重新生成的 sprite 不负责决定最终尺寸和位置。尺寸、位置、层级、锚点、文字内容必须由 `Layout IR` / `Layer IR` 或等价结构锁定，再把独立 sprite fit 回固定 bbox 做回贴验证。

## 强制前置：Sprite Plan

处理任何 UI 图片前，先输出 `sprite_plan.md` 或等价清单，让人工确认。

不要直接开始生图，除非用户明确说“按你的判断直接执行”。

Sprite Plan 必须分成两类：

```markdown
# Sprite Plan

## 自动确认
| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| claim_button_bg | button_bg | claim_button_bg.png | standalone_sprite | 按钮底图必须去文字并可复用 |
| claim_button_label | dynamic_text | 不生成 PNG | text_node | 按钮文案应保持可编辑 |

## 需要人工确认
| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| title_logo | fixed_art_text / text_node | 推荐 fixed_art_text | 艺术字还原度优先，但多语言场景可能需要 Text |
| main_panel | whole_panel / split_parts | 推荐 whole_panel + 单独装饰 | 面板装饰是否需要复用不确定 |
```

## 强制前置：尺寸与位置计划

人工确认 Sprite Plan 后，不要直接批量生图。先补一份机器可执行的生成与布局计划：

- `sprite_manifest.json`：每个独立 sprite 的 id、输出路径、类型、生成策略、是否透明、是否禁止文字、prompt subject。
- `layer_ir.json` 或等价结构：每个 sprite / Text Node 在源图中的 bbox、层级、锚点、透明度、缩放策略。
- `layout_ir.json` 或等价结构：重建 UI 所需的屏幕尺寸、节点树、Text Node 内容、字体建议和资源引用。
- `bbox_overlay.png`：把 bbox 叠在源图上的人工审核图，复杂区域必须用它检查。

如果当前无法准确获得 bbox，必须明确标记为 `needs_bbox_confirmation`，不要假装知道大小和位置。

### 尺寸一致性规则

- 生成出的 `assets_png/<id>.png` 可以有自然尺寸和 padding 差异。
- `assets_png` 保存可复用源素材，命名按语义 asset id，例如 `star_slot.png`。
- `assets_fit_raw` 保存布局实例，命名按 layer id，例如 `star_slot_left.png`、`star_slot_center.png`。
- 工程回贴必须使用 `assets_fit_raw/<layer_id>.png`：把独立 sprite 缩放/居中/装入原始 bbox 尺寸的透明画布。
- `assets_fit_raw` 的画布尺寸必须来自 IR，而不是来自 AI 生成图本身。
- 多个 layer 可以复用同一个 `assets_png` 源素材，但每个 layer 必须有自己的 `assets_fit_raw` 实例。
- Text Node 不生成 PNG，但必须在 IR 中记录文本、bbox、层级和大致字体样式。
- 生成后必须用 IR 重建 `reconstruction.png` 或等价对比图，检查位置、尺寸、层级和视觉一致性。

### 自动确认规则

以下通常可以自动确认：

- 按钮底图：生成独立 sprite，去文字
- 按钮文字：Text Node，不生成 PNG
- 数字、价格、进度值、倒计时：Text Node，不生成 PNG
- 普通 label：默认 Text Node，除非明显是艺术字
- 关闭按钮、加号按钮：独立 sprite
- 明确 icon：独立 sprite
- 进度条底图：独立 sprite，去数字
- 货币条底图：独立 sprite，去数字、去 icon、去按钮
- 卡片/徽章/底板：独立 sprite，去内容

### 需要人工确认的情况

以下必须列入“需要人工确认”：

- 艺术字标题：图片 sprite 还是 Text Node
- 主面板：整体一张，还是拆成底板 + 装饰件
- 复杂奖励 icon：只要物品，还是物品 + 底座/外框一起
- 光效和阴影：跟随对象，还是单独层
- 装饰物：是否需要独立复用
- 多语言相关文字：保留为 Text，还是固定图片
- 任何边界不清、遮挡严重、元素归属不明确的区域

## 工作流

0. 先阅读 `references/known_issues.md`，把里面的防错规则纳入本次执行。
1. 查看源 UI 图片。
2. 识别语义元素，而不是只画裁切框：
   - 背景
   - 主面板
   - 标题牌
   - 固定艺术字
   - 卡片、徽章、底板
   - 按钮
   - icon
   - 进度条
   - 装饰件
   - 动态 Text Node
3. 输出 Sprite Plan，并等待人工确认。
4. 人工确认后，输出或更新 `sprite_manifest.json`，把自然语言确认转成可执行清单。
5. 建立 `layer_ir.json` / `layout_ir.json` 或等价结构，记录：
   - 源图尺寸
   - 每个 sprite / Text Node 的 bbox
   - 层级顺序
   - 锚点或 pivot
   - 资源引用
   - 可复用源素材 id 与布局实例 id 的关系
   - Text Node 内容和字体建议
   - 需要人工确认的 bbox 或层级
6. 生成 `bbox_overlay.png`，用源图叠加 bbox 供人工检查；复杂区域用 `metadata.confidence` 或 `needs_bbox_review` 标记。
7. 对每个元素选择策略：
   - `standalone_sprite`：生成干净独立 PNG
   - `fixed_art_text`：作为图片生成，保留准确文字
   - `dynamic_text`：不生成 PNG，保留为引擎 Text
   - `passthrough`：仅在元素已完全独立且用户允许时使用
8. 用源图作为风格参考，逐个生成独立 sprite。
9. 需要透明背景时，用 chroma-key 背景生成，再本地去底。
10. 分开保存生成源图和最终透明 PNG。
11. 生成棋盘格总览图，方便人工确认这些是真正单图。
12. 根据 IR 生成 `assets_fit_raw/`：把每个独立 sprite fit 到原始 bbox 尺寸的透明画布。
13. 根据 IR 重建 `reconstruction.png` / `comparison.png`，检查尺寸、位置、层级、Text Node 和视觉一致性。
14. 如果本次运行中发现新问题、返工原因或用户纠正，按 `references/known_issues.md` 的模板追加记录。

## 推荐输出素材

组合式游戏 UI 通常优先输出：

- `main_panel.png`
- `title_board.png`
- `title_logo.png`，固定艺术字标题
- `subtitle_ribbon.png`
- `reward_card_bg.png`
- `reward_icon.png`
- `button_bg.png`
- `progress_bar_bg.png`
- `badge_bg.png`
- `currency_bar_bg.png`
- `currency_icon.png`
- `close_button.png`
- `plus_button.png`
- `decoration_*.png`

命名使用 UI 语义，不使用坐标或裁切编号。

## Prompt 模板

生成单图素材时，用类似下面的 prompt：

```text
根据提供的 UI 效果图风格，生成一个干净的独立 <element> sprite。
主体：只包含 <exact element>。
风格：匹配源图的游戏 UI 风格、颜色、描边、材质、光照和精致度。
构图：单个素材居中，留出适当 padding。
约束：不要包含无关 UI 元素、不要背景场景、不要水印。
如果是底图类素材：不要文字、不要字母、不要数字、不要子元素。
如果是固定艺术字：只包含准确文字 “<text>”，不要额外文字。
尺寸：不要依赖生成图自然尺寸作为工程尺寸；后续会按 IR bbox fit 到固定透明画布。
请生成在纯色 #00ff00 chroma-key 背景上，方便去底。背景必须是完全均匀纯色，不要阴影、渐变、纹理、反射、地面或光照变化。主体中不要使用 #00ff00。
```

如果主体本身含绿色或青绿色，换用 `#ff00ff` 等不冲突的 key color。

## 透明背景处理

使用内置 image generation 工具时：

1. 先生成纯色 chroma-key 背景图。
2. 把生成源图复制到项目目录，例如 `generated_src/`。
3. 使用去底脚本：

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py" \
  --input <generated_chroma.png> \
  --out <asset.png> \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

4. 校验最终图片是 `RGBA`，并且四角透明。

## 输出结构

除非项目已有更明确规范，默认使用：

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

- `sprite_plan.md`：生成前的人工确认清单。
- `sprite_manifest.json`：人工确认后的可执行生成清单。
- `layer_ir.json`：源图 bbox、层级、策略和 Text Node 的结构数据。
- `layout_ir.json`：用于引擎或重建器消费的布局结构。
- `generated_src/`：原始生成图，通常是 chroma-key 版本。
- `assets_png/`：最终独立透明源 sprite。它按语义素材命名，允许被多个布局实例复用。
- `assets_fit_raw/`：按 IR 目标尺寸装入透明画布的布局实例，用于回贴验证和工程占位。
- `bbox_overlay.png`：bbox 人工审核图。
- `sprite_overview.png`：棋盘格总览图。
- `reconstruction.png`：用 `assets_fit_raw` 和 Text Node 按 IR 重建出的 UI。
- `comparison.png`：源图与重建图的并排或差异对比。

## 验收标准

汇报完成前必须确认：

- 已阅读并遵守 `references/known_issues.md`。
- 已先输出 Sprite Plan，并处理人工确认项。
- 已输出或更新 `sprite_manifest.json`。
- 已输出或更新 `layer_ir.json` / `layout_ir.json`，或明确说明哪些 bbox 仍需人工确认。
- 已输出 `bbox_overlay.png`，或说明本轮为何无法生成。
- 最终资产是生成/重生成的独立 sprite，不是原图矩形 crop。
- 背景、按钮、卡片、徽章类素材不包含动态文字。
- 动态文字已单独列为 Text Node。
- 需要透明的最终资产是 PNG 且带 alpha。
- 已提供棋盘格总览图。
- 已提供 `assets_fit_raw` 和基于 IR 的重建/对比图，或说明本轮只到计划阶段。
- 如果存在素材复用，已区分 `assets_png` 源素材和 `assets_fit_raw` 布局实例。
- 明确说明仍然 crop-based 或需要再次生成的资产。
- 如果出现新坑，已写入 Known Issues，或说明为什么暂不记录。

## 失败判定

如果结果是一块原图矩形，里面带有邻近像素、文字、遮挡、背景或其它 UI 元素，只能称为 reference crop，不能称为 sprite。

用户说“每一张单图”“sprite 贴图”“工程切图”“可复用素材”时，默认走独立重生成流程，并先出 Sprite Plan。不要停在 bbox crop 提取。

## Known Issues 机制

运行中遇到问题时，不要只在对话里道歉；要把可复用教训沉淀到 `references/known_issues.md`。

记录标准：

- 会导致用户返工、误解或结果不可用的问题，必须记录。
- 只是一次性拼写、小口误、不影响后续流程的问题，可以不记录。
- 记录要写“如何预防”，不要只写“发生了什么”。
