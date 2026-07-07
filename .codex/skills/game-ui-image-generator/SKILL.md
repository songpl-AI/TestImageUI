---
name: game-ui-image-generator
description: 生成面向游戏 UI 的 AI 效果图，并约束其适合后续 Sprite Plan、Layer IR、独立 sprite 生成和 UI 重建。用户提到生成游戏 UI、AI UI 效果图、活动弹窗、商城礼包页、任务面板、战令界面、奖励领取页、抽卡界面、HUD、游戏 UI mockup、用于后续切图或拆 sprite 的 UI 图时使用。必须优先遵守游戏 UI 生图最佳实践，避免生成难以拆解、文字混乱、元素粘连或工程不可用的图片。
---

# Game UI Image Generator

## 目标

生成一张“好看但也能工程化”的游戏 UI 效果图。

这个 skill 负责前一环：从需求生成 UI 效果图。它和 `ui-sprite-regenerator` 分工如下：

- `game-ui-image-generator`：生成适合后续拆解的 UI 效果图。
- `ui-sprite-regenerator`：从 UI 效果图规划并生成独立 sprite 单图。

## 使用前先读

执行前阅读：

- `references/best_practices.md`：游戏 UI 生图最佳实践。
- `references/prompt_templates.md`：常用 prompt 模板。
- `references/known_issues.md`：已知问题和防错规则。

如果本次运行中出现可复用的新问题，按 `known_issues.md` 模板追加记录。

## 核心原则

1. 不只追求视觉漂亮，还要让后续拆解可行。
2. UI 元素必须语义清楚、边界清楚、层级清楚。
3. 不要让所有元素粘在一起；要给后续 sprite 拆分留空间。
4. 动态文字要少、清晰、准确；能用 Text Node 的文字不要过度艺术化。
5. 固定艺术字标题可以图片化，但要明确它是 fixed art text。
6. 背景要服务 UI，不要抢主体，不要让 UI 边缘淹没在复杂背景里。
7. 一张图最好聚焦一个屏幕 / 一个弹窗 / 一个核心玩法界面，不要塞太多状态。

## 推荐工作流

1. 明确用途：
   - 只是概念图
   - 用于后续 Sprite Plan
   - 用于拆独立 sprite
   - 用于验证 Layout IR / 重建
2. 输出或内部整理一份 `generation_brief`：
   - UI 类型
   - 画布尺寸
   - 主题和风格
   - 必须出现的 UI 元素
   - 精确文字
   - 动态文字列表
   - 固定艺术字列表
   - 后续拆解约束
3. 根据 brief 组织 prompt。
4. 使用内置 image generation 生成图。
5. 保存源图到项目，例如：

```text
examples/input/<screen_name>_raw.png
examples/input/<screen_name>.png
```

6. 检查图像是否满足后续拆解要求。
7. 如果发现新问题，记录到 `references/known_issues.md`。

## 生成前必须考虑的问题

如果用户没有说明，可以合理假设；但以下问题会明显影响结果时，要先问或在 brief 中写明假设：

- UI 类型：弹窗、商城、任务、战令、抽卡、HUD、结算、活动页？
- 目标比例：竖屏 `720x1280` / `1080x1920`，还是横屏？
- 游戏品类：休闲、SLG、RPG、二次元、卡牌、欧美魔幻、科幻等？
- 必须出现哪些组件？
- 哪些文字必须精确出现？
- 生成结果是否要用于后续 sprite 拆分？
- 是否需要多语言友好？

## 输出要求

项目内生成结果默认保存为：

```text
examples/input/<screen_name>_raw.png
examples/input/<screen_name>.png
```

如果需要记录 prompt 和 brief，可保存：

```text
examples/input/<screen_name>.generation_brief.md
examples/input/<screen_name>.prompt.txt
```

## 验收标准

生成后检查：

- 画布比例正确，主体没有被裁切。
- UI 主体、背景、按钮、卡片、icon、文字的层级清楚。
- 关键文字准确、可读，没有乱码。
- 元素之间有足够边界，后续能做 Sprite Plan。
- 动态文字没有过度艺术化。
- 背景没有压过 UI，也没有穿插到关键 UI 边界里。
- 没有 watermark、品牌 logo、设备边框。
- 风格统一，材质和光照一致。

如果图像只是好看但难以拆 sprite，要明确说明它更适合概念图，不适合作为工程化源图。
