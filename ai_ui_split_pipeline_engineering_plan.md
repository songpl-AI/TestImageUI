# AI UI 效果图拆解与跨引擎 Layout IR 工程化实验方案

> 目标：验证“AI 生成 UI 效果图 → 生成 Layer IR / Asset Plan → 直接抠图或语义重生成散图 → 重建对比 → 生成跨引擎 Layout IR”的可行性。  
> 适用场景：游戏 UI、活动页、弹窗、商城礼包页、任务面板、战令界面等。  
> 实验目标不是一次性全自动上线，而是先做出可审核、可迭代、可扩展的 MVP。

---

## 1. 背景与核心判断

团队当前讨论的关键问题是：

```text
方案 A：从 AI 效果图中直接抠图 / 裁图
方案 B：根据 AI 效果图中的部件语义，重新生成干净的切图
```

结论：

```text
不要二选一。
正确路线应该是：
先理解 UI 结构 → 生成 Layer IR / Asset Plan → 再决定每个元素用哪种资产生产策略。
```

原因：

```text
AI 效果图不是 PSD / Figma / Spine。
它没有真实图层，没有真实 alpha，没有父子层级，没有组件语义。

直接抠图只能拿到“可见像素”。
但游戏 UI 工程需要的是“可编辑、可复用、可组合、可适配”的资源和结构。
```

因此，本实验的核心不是“把图切开”，而是验证：

```text
Pixel Image
  ↓
Layer IR / Asset Plan
  ↓
Asset Extraction / Asset Regeneration
  ↓
Layout IR
  ↓
Engine Adapter
```

---

## 2. 实验目标

### 2.1 MVP 目标

实现一个本地脚本或 CLI，输入一张 UI 效果图，输出：

```text
output/
  original.png
  layer_ir.json
  layout_ir.json
  assets_direct/
  assets_regenerated/
  reconstruction_direct.png
  reconstruction_regenerated.png
  comparison.png
  report.md
```

其中：

- `assets_direct/`：直接从原图裁切 / 抠图得到的资源。
- `assets_regenerated/`：根据 Layer IR 语义重新生成或程序化生成的干净资源。
- `layer_ir.json`：描述每个视觉层如何拆、是否需要重生成、是否是文本、是否需要 inpaint。
- `layout_ir.json`：描述 UI 节点树、组件类型、资源引用、文本内容、布局信息。
- `comparison.png`：原图、直接拆图还原、重生成资产还原三图对比。
- `report.md`：自动生成本次拆解质量分析报告。

### 2.2 非目标

第一版不追求：

```text
1. 完全自动识别所有 UI 元素
2. 自动生成可上线 Prefab
3. 完美 alpha 抠图
4. 完美 inpaint 背景修复
5. 完美九宫格识别
6. 完全替代美术 / 程序审核
```

第一版追求：

```text
1. 有结构化中间产物
2. 能对比两种拆图路线
3. 能证明哪些元素适合直接抠，哪些适合重生成
4. 能为后续 Unity / Cocos / UE Adapter 提供稳定输入
```

---

## 3. 总体架构

```text
输入：
  UI 效果图 original.png
  可选：人工标注 / 模型检测结果 / Prompt / UI 类型

流程：
  1. 元素候选识别
  2. 生成 Layer IR / Asset Plan
  3. 按元素策略生成资产
      - direct_crop
      - segmentation_extract
      - regenerate
      - inpaint_background
      - text_node
      - vector_shape
      - ignore
  4. 根据 Layer IR 重建 UI 预览图
  5. 生成 Layout IR
  6. 输出对比图与报告
  7. 后续接 Unity / Cocos / UE Adapter
```

推荐 pipeline：

```text
original.png
  ↓
detect_elements()
  ↓
build_layer_ir()
  ↓
generate_assets()
  ↓
reconstruct_preview()
  ↓
build_layout_ir()
  ↓
export_engine_ui()
```

---

## 4. 目录结构建议

```text
ai-ui-split-pipeline/
  README.md
  requirements.txt
  pyproject.toml

  examples/
    input/
      shop_popup.png
    output/

  src/
    main.py

    core/
      types.py
      pipeline.py
      config.py

    detection/
      manual_detector.py
      simple_cv_detector.py
      multimodal_detector.py

    ir/
      layer_ir.py
      layout_ir.py
      validators.py

    assets/
      direct_crop.py
      matting_extract.py
      regenerate.py
      inpaint.py
      text_asset.py
      vector_asset.py

    reconstruction/
      renderer.py
      diff.py

    exporters/
      unity_exporter.py
      cocos_exporter.py
      ue_umg_exporter.py

    report/
      markdown_report.py

  tests/
    test_layer_ir.py
    test_asset_plan.py
    test_reconstruction.py
```

---

## 5. 核心数据结构

### 5.1 Layer IR

`Layer IR` 服务于拆图阶段，回答：

```text
这个元素是什么？
在哪里？
应该怎么生成资产？
是否透明？
是否需要去掉文字？
是否被遮挡？
是否需要背景修复？
是否应该转 Text？
是否可能九宫格？
```

示例：

```json
{
  "version": "0.1",
  "canvas": {
    "width": 720,
    "height": 1280
  },
  "source_image": "original.png",
  "layers": [
    {
      "id": "panel_main_bg",
      "role": "panel_background",
      "bbox": [70, 210, 580, 875],
      "asset_strategy": "regenerate_or_inpaint",
      "output": "assets_regenerated/panel_main_bg.png",
      "transparent": true,
      "remove_occluding_children": true,
      "nine_slice_candidate": true,
      "children_hint": [
        "title_board",
        "reward_card",
        "buy_button",
        "coin_bar"
      ]
    },
    {
      "id": "btn_buy_bg",
      "role": "button_background",
      "bbox": [190, 890, 340, 125],
      "asset_strategy": "regenerate",
      "output": "assets_regenerated/btn_buy_bg.png",
      "transparent": true,
      "remove_text": true,
      "nine_slice_candidate": true
    },
    {
      "id": "btn_buy_text",
      "role": "button_label",
      "bbox": [250, 920, 220, 60],
      "asset_strategy": "text",
      "text": "BUY NOW",
      "font_hint": {
        "size": 44,
        "bold": true,
        "stroke": true
      }
    }
  ]
}
```

### 5.2 Layout IR

`Layout IR` 服务于引擎生成阶段，回答：

```text
UI 节点树是什么？
谁是谁的子节点？
节点类型是什么？
资源引用哪个？
文本内容是什么？
坐标、尺寸、锚点是什么？
```

示例：

```json
{
  "version": "0.1",
  "screen": {
    "name": "ShopPopup",
    "canvas": {
      "width": 720,
      "height": 1280
    },
    "nodes": [
      {
        "id": "Panel_Main",
        "type": "Panel",
        "rect": [70, 210, 580, 875],
        "asset": "assets_regenerated/panel_main_bg.png",
        "anchor": "center",
        "children": [
          {
            "id": "Btn_Buy",
            "type": "Button",
            "rect": [190, 890, 340, 125],
            "asset": "assets_regenerated/btn_buy_bg.png",
            "children": [
              {
                "id": "Txt_Buy",
                "type": "Text",
                "text": "BUY NOW",
                "rect": [250, 920, 220, 60]
              }
            ]
          }
        ]
      }
    ]
  }
}
```

---

## 6. 元素资产策略

每个元素必须选择一种策略：

```text
direct_crop
segmentation_extract
regenerate
inpaint_background
text_node
vector_shape
ignore
```

### 6.1 direct_crop

直接从原图裁切矩形区域。

适合：

```text
1. 独立关闭按钮
2. 独立 icon
3. 不需要复用的装饰
4. 边界清晰的静态元素
```

风险：

```text
1. 包含背景污染
2. 包含其他子元素
3. 没有真实透明通道
4. 后续不可复用
```

### 6.2 segmentation_extract

使用 mask / matting 抠出透明图。

适合：

```text
1. 独立 icon
2. 角色头像
3. 宝箱、金币、道具等明确对象
```

风险：

```text
1. 半透明边缘脏
2. 光效和阴影归属不清
3. 被遮挡部分无法恢复
```

### 6.3 regenerate

根据原图局部语义重新生成干净资产。

适合：

```text
1. 按钮底图
2. 面板背景
3. 光效
4. 被文字覆盖的按钮
5. 被 icon 覆盖的底板
6. 需要透明背景的可复用素材
```

风险：

```text
1. 风格跑偏
2. 颜色不一致
3. 形状不完全一致
4. 需要更强的 prompt / reference control
```

### 6.4 inpaint_background

把前景元素 mask 掉，修复背景。

适合：

```text
1. 背景板被 icon / text 遮挡
2. 卡片底图需要去掉内容
3. 按钮底图需要去掉文字
```

风险：

```text
1. 修复纹理可能不一致
2. 渐变可能断裂
3. 边框可能变形
```

### 6.5 text_node

不生成图片，转成引擎 Text / Label / TextBlock。

适合：

```text
1. 价格
2. 数量
3. 倒计时
4. 按钮文案
5. 玩家昵称
6. 任务进度
7. 普通标题
```

风险：

```text
1. 引擎字体无法完全还原艺术效果
2. 描边、渐变、阴影需要额外参数
```

### 6.6 vector_shape

使用引擎绘制或程序化绘制。

适合：

```text
1. 纯色矩形
2. 圆角背景
3. 简单进度条
4. 半透明遮罩
```

风险：

```text
1. 与 AI 原图视觉不完全一致
2. 复杂美术效果无法还原
```

---

## 7. 各类 UI 元素推荐策略

| 元素类型 | 推荐策略 | 说明 |
|---|---|---|
| 独立关闭按钮 | direct_crop / regenerate | MVP 可整张按钮裁出 |
| 按钮背景 | regenerate / inpaint_background | 不建议带文字裁出 |
| 按钮文字 | text_node | 默认保持动态 |
| 面板背景 | regenerate / inpaint_background | 通常被子元素遮挡 |
| 奖励 icon | segmentation_extract / regenerate | 看边缘和遮挡情况 |
| 金币 / 道具 | segmentation_extract | 独立时可直接抠 |
| 光效 | regenerate | alpha 反推困难 |
| 阴影 | 跟随对象或单独 layer | 需要规则判断 |
| 艺术字标题 | direct_crop / regenerate | 固定标题可图片化 |
| 普通标题 | text_node | 多语言友好 |
| 价格 / 数字 | text_node | 禁止默认切成 PNG |
| 进度条背景 | regenerate / vector_shape | 需要可拉伸 |
| 进度条填充 | vector_shape / regenerate | 需要动态裁切 |
| 列表 item 背景 | regenerate | 需要复用和九宫格 |
| 装饰花纹 | direct_crop / segmentation_extract | 可作为 Decoration |

---

## 8. 关键原则

### 8.1 不要把所有东西都切成 PNG

错误做法：

```text
BUY NOW → buy_now.png
1888 → number_1888.png
$6 → price_6.png
倒计时 → countdown.png
```

正确做法：

```text
按钮底图 → PNG
按钮文字 → Text
价格 → Text
数量 → Text
倒计时 → Text
```

### 8.2 视觉还原不等于工程可用

极端例子：

```text
把整张 UI 切成 full_screen.png
再贴回去
视觉还原 100%
工程价值 0%
```

所以评估时不能只看视觉 diff，还要看：

```text
1. 可编辑性
2. 可复用性
3. 动态文本保留率
4. 组件分类准确率
5. 人工修正成本
```

### 8.3 先生成 Asset Plan，再拆图

错误流程：

```text
原图 → 盲目切图 → 猜 Layout IR
```

推荐流程：

```text
原图 → Layer IR / Asset Plan → 按策略拆图/重生成 → Layout IR
```

### 8.4 Layer IR 是拆图阶段的最小必要结构

即使不做完整 Layout IR，也必须先做 Layer IR。

否则无法判断：

```text
1. 文字是否应该保留为 Text
2. 背景是否需要补全
3. icon 是否要单独导出
4. 光效是否要单独层
5. 按钮是否需要去文字
6. 面板是否候选九宫格
```

---

## 9. MVP 实现步骤

### Step 1：准备输入

输入一张 UI 效果图：

```text
examples/input/shop_popup.png
```

要求：

```text
1. 竖屏 720x1280 或 1080x1920
2. 包含至少一个面板
3. 包含按钮和文字
4. 包含 icon 压背景
5. 包含标题
6. 包含光效或装饰
```

### Step 2：人工或半自动生成 Layer IR

第一版允许手写 `layer_ir.json`。

不要一开始追求自动识别。

```bash
python src/main.py \
  --input examples/input/shop_popup.png \
  --layer-ir examples/input/shop_popup.layer_ir.json \
  --output examples/output/shop_popup
```

### Step 3：生成直接裁切资产

对所有 layer 执行 direct crop：

```text
assets_direct/
  panel_main_bg_direct.png
  btn_buy_direct.png
  reward_card_direct.png
```

### Step 4：生成语义资产

根据 `asset_strategy` 分发：

```text
asset_strategy == direct_crop            → crop
asset_strategy == segmentation_extract   → mask extract
asset_strategy == regenerate             → image generation / procedural placeholder
asset_strategy == inpaint_background     → inpaint
asset_strategy == text_node              → 不导出图片，只写入 Layout IR
asset_strategy == vector_shape           → 生成 vector metadata
```

MVP 中如果没有图像生成 API，可以先用程序化 mock 代替 `regenerate`，验证结构链路。

### Step 5：重建预览图

用两套资产分别重建：

```text
reconstruction_direct.png
reconstruction_regenerated.png
```

### Step 6：生成对比图

输出：

```text
comparison.png
```

格式：

```text
原始效果图 | 直接裁切还原 | 语义重生成还原
```

### Step 7：生成 Layout IR

将 Layer IR 转为 Layout IR：

```text
Panel / Button / Text / Image / Decoration
```

### Step 8：生成报告

输出 `report.md`，包含：

```text
1. 资产数量
2. 直接裁切资产列表
3. 重生成资产列表
4. Text 节点列表
5. 九宫格候选
6. 可能有风险的元素
7. 人工审核建议
```

---

## 10. CLI 设计

建议入口：

```bash
python src/main.py \
  --input examples/input/shop_popup.png \
  --layer-ir examples/input/shop_popup.layer_ir.json \
  --output examples/output/shop_popup \
  --mode full
```

参数：

```text
--input       原始 UI 效果图
--layer-ir    手写或模型生成的 Layer IR
--output      输出目录
--mode        direct | regenerate | full
--debug       输出调试中间图
```

---

## 11. Python 类型定义建议

```python
from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Any

AssetStrategy = Literal[
    "direct_crop",
    "segmentation_extract",
    "regenerate",
    "regenerate_or_inpaint",
    "inpaint_background",
    "text_node",
    "vector_shape",
    "ignore",
]

@dataclass
class BBox:
    x: int
    y: int
    width: int
    height: int

@dataclass
class LayerItem:
    id: str
    role: str
    bbox: BBox
    asset_strategy: AssetStrategy
    output: Optional[str] = None
    transparent: bool = True
    text: Optional[str] = None
    remove_text: bool = False
    remove_occluding_children: bool = False
    nine_slice_candidate: bool = False
    children_hint: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LayerIR:
    version: str
    canvas_width: int
    canvas_height: int
    source_image: str
    layers: List[LayerItem]
```

---

## 12. 资产生成模块接口

```python
class AssetGenerator:
    def generate(self, source_image: Image.Image, layer: LayerItem, output_dir: Path) -> Optional[Path]:
        raise NotImplementedError
```

### DirectCropGenerator

```python
class DirectCropGenerator(AssetGenerator):
    def generate(self, source_image, layer, output_dir):
        crop = source_image.crop((
            layer.bbox.x,
            layer.bbox.y,
            layer.bbox.x + layer.bbox.width,
            layer.bbox.y + layer.bbox.height,
        ))
        output = output_dir / f"{layer.id}.png"
        crop.save(output)
        return output
```

### TextNodeGenerator

```python
class TextNodeGenerator(AssetGenerator):
    def generate(self, source_image, layer, output_dir):
        return None
```

### RegenerateGenerator

MVP 阶段可以先做 placeholder：

```python
class MockRegenerateGenerator(AssetGenerator):
    def generate(self, source_image, layer, output_dir):
        # TODO: 接入 GPT Image / Gemini / SD / 内部图像模型
        # 第一版先生成透明底图或程序化圆角图，用于验证 pipeline。
        pass
```

后续真实接入时，输入应包含：

```text
1. 原图
2. bbox 局部图
3. layer role
4. 目标尺寸
5. 是否透明
6. 是否去文字
7. 风格描述
8. 输出格式
```

---

## 13. Regenerate Prompt 模板

### 13.1 按钮底图

```text
根据参考图中的按钮区域，重新生成一张游戏 UI 按钮底图。

要求：
- 尺寸：{width}x{height}
- 透明背景 PNG
- 不包含任何文字
- 保留参考图中的颜色、圆角、描边、高光、阴影风格
- 适合作为游戏引擎 Button 背景
- 边缘干净
- 不要额外图标
- 不要额外装饰
```

### 13.2 面板背景

```text
根据参考图中的主面板区域，重新生成一张干净的游戏 UI 面板背景。

要求：
- 尺寸：{width}x{height}
- 透明背景 PNG
- 移除所有子元素、文字、icon、按钮
- 只保留面板底板、边框、基础装饰
- 风格、颜色、圆角、边框厚度尽量与参考图一致
- 适合作为游戏 UI 弹窗背景
- 可作为九宫格候选
```

### 13.3 奖励 icon

```text
根据参考图中的奖励图标，重新生成一张独立透明 PNG 图标。

要求：
- 尺寸：{width}x{height}
- 透明背景
- 保留参考图中的物体类型和风格
- 不包含背景板
- 可包含自身合理阴影
- 边缘干净
- 适合作为游戏道具 icon
```

### 13.4 光效

```text
根据参考图中的光效，重新生成一张独立透明 PNG 光效资源。

要求：
- 尺寸：{width}x{height}
- 透明背景
- 只包含光效
- 柔边自然
- 不包含 icon、文字、背景板
- 适合作为游戏 UI 装饰层
```

---

## 14. 重建渲染器

重建渲染器用于验证资产是否可还原原图。

输入：

```text
source_image
layer_ir
assets_direct/
assets_regenerated/
```

输出：

```text
reconstruction_direct.png
reconstruction_regenerated.png
comparison.png
```

核心规则：

```text
1. direct 模式：按 bbox 把 direct asset 贴回去
2. regenerated 模式：按 bbox 把 regenerated asset 贴回去
3. text_node：用临时字体绘制文字
4. vector_shape：用程序化形状绘制
5. ignore：跳过
```

---

## 15. 评估指标

### 15.1 视觉还原指标

```text
Visual Reconstruction Score
```

对比：

```text
original.png vs reconstruction_direct.png
original.png vs reconstruction_regenerated.png
```

可先用：

```text
1. pixel MSE
2. SSIM
3. 人工肉眼评分
```

注意：视觉还原不是唯一指标。

### 15.2 工程可用性指标

更重要的是：

```text
1. Text Preservation Rate
   动态文字是否保留为 Text

2. Component Correctness
   Button / Panel / Icon / Text 分类是否正确

3. Asset Cleanliness
   透明边缘是否干净

4. Reusability
   资产是否可复用

5. Occlusion Handling
   被遮挡背景是否补全

6. Node Economy
   是否过度拆分导致节点爆炸

7. Human Fix Cost
   人工修到可用需要多久
```

### 15.3 推荐报告格式

```markdown
# UI Split Report

## Summary
- Layers: 12
- Direct assets: 8
- Regenerated assets: 6
- Text nodes: 4
- Nine-slice candidates: 3
- Risk items: 5

## Risk Items
| id | role | issue | suggestion |
|---|---|---|---|
| btn_buy_bg | button_background | direct crop contains text | use regenerate |
| panel_main_bg | panel_background | occluded by children | use inpaint/regenerate |
| price_text | dynamic_text | should not be PNG | use Text node |
```

---

## 16. Unity / Cocos / UE Adapter 设计

### 16.1 Adapter 输入

统一吃 `layout_ir.json`：

```text
layout_ir.json
assets/
```

### 16.2 Unity Adapter

映射关系：

| Layout IR | Unity |
|---|---|
| Panel | GameObject + RectTransform + Image |
| Image | GameObject + RectTransform + Image |
| Button | GameObject + RectTransform + Image + Button |
| Text | GameObject + RectTransform + TMP_Text |
| Decoration | GameObject + RectTransform + Image |
| ScrollView | ScrollRect + Viewport + Content |
| ProgressBar | Bg Image + Fill Image |

### 16.3 Cocos Adapter

映射关系：

| Layout IR | Cocos |
|---|---|
| Panel | Node + Sprite |
| Image | Node + Sprite |
| Button | Node + Button + Sprite |
| Text | Node + Label |
| Decoration | Node + Sprite |
| ScrollView | ScrollView |
| ProgressBar | ProgressBar |

### 16.4 UE UMG Adapter

映射关系：

| Layout IR | UE UMG |
|---|---|
| Panel | CanvasPanel / Border / Image |
| Image | Image Widget |
| Button | Button + Image |
| Text | TextBlock |
| Decoration | Image |
| ScrollView | ScrollBox |
| ProgressBar | ProgressBar |

---

## 17. Codex 执行任务拆分

### Task 1：创建项目骨架

要求：

```text
创建 Python 项目结构。
实现 src/main.py。
支持命令行参数：
--input
--layer-ir
--output
--mode
```

验收：

```bash
python src/main.py --help
```

可以正常显示参数。

---

### Task 2：实现 Layer IR 读取与校验

要求：

```text
1. 定义 LayerIR / LayerItem / BBox 类型
2. 从 JSON 读取
3. 校验 bbox 不越界
4. 校验 id 唯一
5. 校验 asset_strategy 合法
```

验收：

```bash
python src/main.py \
  --input examples/input/shop_popup.png \
  --layer-ir examples/input/shop_popup.layer_ir.json \
  --output examples/output/shop_popup \
  --mode validate
```

输出：

```text
Layer IR validation passed.
```

---

### Task 3：实现 direct_crop

要求：

```text
根据每个 layer 的 bbox 裁切原图。
输出到 assets_direct/。
```

验收：

```text
assets_direct/
  panel_main_bg.png
  btn_buy_bg.png
  reward_icon.png
```

---

### Task 4：实现 mock regenerate

要求：

```text
不接真实 AI 图像模型。
先根据 role 生成程序化 placeholder：
- button_background → 圆角按钮
- panel_background → 圆角面板
- reward_card → 圆角卡片
- text_node → 不生成图片
- icon → 直接 crop 或简单 placeholder
```

目的：

```text
先验证 pipeline，而不是卡在图像模型 API。
```

---

### Task 5：实现 reconstruction renderer

要求：

```text
1. direct 模式重建
2. regenerated 模式重建
3. 输出 reconstruction_direct.png
4. 输出 reconstruction_regenerated.png
5. 输出 comparison.png
```

---

### Task 6：实现 Layout IR 生成

要求：

```text
根据 Layer IR 生成初版 Layout IR。
规则：
- role 包含 button → Button
- role 包含 text / label → Text
- role 包含 panel / background → Panel 或 Image
- role 包含 icon → Image
- role 包含 decoration / glow → Decoration
```

第一版可以不完美，但必须输出可读 JSON。

---

### Task 7：实现 report.md

要求：

```text
输出：
1. layer 数量
2. 资产策略统计
3. text_node 列表
4. nine_slice_candidate 列表
5. 风险提示
```

风险提示规则：

```text
1. button_background 如果使用 direct_crop，提示可能包含文字
2. panel_background 如果 direct_crop，提示可能包含子元素遮挡
3. dynamic_text 如果不是 text_node，提示风险
4. glow 如果 direct_crop，提示 alpha 风险
```

---

## 18. 推荐初始测试用例

`examples/input/shop_popup.layer_ir.json`：

```json
{
  "version": "0.1",
  "canvas": {
    "width": 720,
    "height": 1280
  },
  "source_image": "shop_popup.png",
  "layers": [
    {
      "id": "panel_main_bg",
      "role": "panel_background",
      "bbox": [70, 210, 580, 875],
      "asset_strategy": "regenerate_or_inpaint",
      "transparent": true,
      "remove_occluding_children": true,
      "nine_slice_candidate": true
    },
    {
      "id": "title_board",
      "role": "title_board",
      "bbox": [150, 150, 420, 135],
      "asset_strategy": "regenerate",
      "transparent": true,
      "remove_text": true
    },
    {
      "id": "title_logo",
      "role": "title_art_text",
      "bbox": [150, 172, 420, 90],
      "asset_strategy": "regenerate",
      "transparent": true,
      "text": "LIMITED GIFT"
    },
    {
      "id": "close_button",
      "role": "close_button",
      "bbox": [590, 170, 80, 80],
      "asset_strategy": "direct_crop",
      "transparent": true
    },
    {
      "id": "reward_card_bg",
      "role": "reward_card_background",
      "bbox": [160, 390, 400, 345],
      "asset_strategy": "regenerate",
      "transparent": true,
      "remove_occluding_children": true
    },
    {
      "id": "reward_glow",
      "role": "decoration_glow",
      "bbox": [200, 405, 320, 320],
      "asset_strategy": "regenerate",
      "transparent": true
    },
    {
      "id": "reward_chest_icon",
      "role": "reward_icon",
      "bbox": [230, 480, 260, 230],
      "asset_strategy": "segmentation_extract",
      "transparent": true
    },
    {
      "id": "reward_count_text",
      "role": "dynamic_text",
      "bbox": [250, 680, 220, 55],
      "asset_strategy": "text_node",
      "text": "x100"
    },
    {
      "id": "price_text",
      "role": "dynamic_text",
      "bbox": [185, 770, 350, 65],
      "asset_strategy": "text_node",
      "text": "Special Price: $6"
    },
    {
      "id": "buy_button_bg",
      "role": "button_background",
      "bbox": [190, 890, 340, 125],
      "asset_strategy": "regenerate",
      "transparent": true,
      "remove_text": true,
      "nine_slice_candidate": true
    },
    {
      "id": "buy_button_label",
      "role": "button_label",
      "bbox": [245, 922, 230, 60],
      "asset_strategy": "text_node",
      "text": "BUY NOW"
    },
    {
      "id": "coin_bar_bg",
      "role": "currency_bar_background",
      "bbox": [205, 1040, 310, 85],
      "asset_strategy": "regenerate",
      "transparent": true,
      "remove_text": true
    },
    {
      "id": "coin_icon",
      "role": "currency_icon",
      "bbox": [225, 1048, 70, 70],
      "asset_strategy": "segmentation_extract",
      "transparent": true
    },
    {
      "id": "coin_amount_text",
      "role": "dynamic_text",
      "bbox": [315, 1055, 140, 55],
      "asset_strategy": "text_node",
      "text": "1888"
    }
  ]
}
```

---

## 19. 实验验收标准

### 19.1 第一阶段验收

必须完成：

```text
1. 能读取原图和 layer_ir.json
2. 能输出 direct assets
3. 能输出 regenerated/mock assets
4. 能输出两张重建图
5. 能输出 comparison.png
6. 能输出 layout_ir.json
7. 能输出 report.md
```

### 19.2 判断实验是否有价值

满足以下任意三项，即说明路线值得继续：

```text
1. 程序能基于 Layout IR 快速生成草稿 UI
2. 重生成资产比直接裁切资产更干净
3. Text 节点保留后，UI 更适合动态数据
4. 人工修改成本低于从零搭建
5. 同一份 Layout IR 能被 Unity / Cocos / UE 消费
```

---

## 20. 后续增强方向

### 20.1 接入真实图像模型

将 `MockRegenerateGenerator` 替换为真实图像模型。

需要支持：

```text
1. reference image
2. crop image
3. mask
4. transparent output
5. strict size
6. remove text
7. style consistency
```

### 20.2 接入检测 / 分割

可选模型：

```text
1. OCR：识别文字区域
2. SAM / SAM2：生成 mask 候选
3. GroundingDINO：按文本找对象
4. 多模态模型：判断 UI 语义和拆分策略
```

注意：

```text
分割模型只提供候选边界。
最终怎么拆必须由 Layer IR / Asset Plan 决定。
```

### 20.3 自动生成 Layer IR

后续可以让多模态模型输出初版 Layer IR：

```text
输入：
- 原图
- UI 类型
- 项目组件 schema
- 拆图规则

输出：
- layer_ir.json
```

但必须保留人工审核。

### 20.4 可视化审核工具

建议做一个简单 Web UI：

```text
左侧：原图
右侧：Layer IR 列表
功能：
- 查看 bbox
- 修改 role
- 修改 asset_strategy
- 修改 text
- 标记 nine_slice
- 重新生成单个 asset
- 查看重建差异
```

---

## 21. Codex 总任务说明

请根据本文档实现一个 Python MVP。

优先级：

```text
P0:
1. 项目骨架
2. Layer IR 类型和校验
3. Direct crop
4. Mock regenerate
5. Reconstruction
6. Comparison image
7. Layout IR 输出
8. Report 输出

P1:
1. 简单 cv 检测
2. 简单 OCR 接口预留
3. Unity exporter stub
4. Cocos exporter stub
5. UE exporter stub

P2:
1. 接真实图像生成 API
2. 接 SAM / OCR
3. 可视化审核工具
```

代码要求：

```text
1. Python 3.10+
2. 使用 Pillow 处理图片
3. 结构清晰，模块化
4. 每个阶段都可以单独运行
5. 输出文件可人工检查
6. 不要把模型 API 写死，使用接口抽象
7. 所有 JSON 使用 UTF-8
8. 出错时给出明确错误信息
```

---

## 22. 最终判断

这个实验的核心价值是证明：

```text
AI 效果图不是最终资产。
直接抠图不是万能方案。
语义重生成资产比盲目抠图更接近游戏 UI 工程化。
但语义重生成必须由 Layer IR / Asset Plan 指导。
Layout IR 不是后置小事，而是跨引擎导入的核心中间结构。
```

最终推荐路线：

```text
AI UI 效果图
  ↓
Layer IR / Asset Plan
  ↓
按元素选择：
  - direct crop
  - segmentation extract
  - regenerate
  - inpaint
  - text node
  - vector shape
  ↓
散图资源 + metadata
  ↓
Layout IR
  ↓
Unity / Cocos / UE Adapter
  ↓
人工审核 + 反馈闭环
```
