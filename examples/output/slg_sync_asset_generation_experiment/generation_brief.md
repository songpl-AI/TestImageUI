# Synchronized Effect + Asset Generation Brief

## Purpose

验证新的生产方向：不要先生成完整 UI 再反向硬拆，而是先定义同一份 Asset / Layer Plan，然后在同一轮生成中产出：

- 完整 SLG 主界面 HUD 效果图
- 同风格 asset family sheet / standalone assets
- 后续可由 `ui-sprite-regenerator` 转成 manifest、Layer IR、Layout IR，并做回贴验证

## Experiment Scope

本轮只做一个最小闭环，不全屏推广：

- source component: bottom BUILD navigation button in generated SLG HUD
- generated standalone assets:
  - `bottom_nav_button_bg`
  - `build_hammer_icon`
  - `red_badge_dot`
  - `build_label` as Text Node
- diagnostic visual-state asset:
  - `build_button_visual_state`

## Why BUILD Button

BUILD 按钮是前面多轮实验中失败最多的组件，覆盖了几个关键风险：

- 按钮底板是否与效果图风格一致
- icon 是否和按钮同属一套美术
- badge 是否能独立但保持同风格
- Text Node 是否会成为主要误差
- 同步生成资产是否比后处理分割更稳定

## Generation Strategy

Prompt 让模型生成一张 game UI production board：

- LEFT: complete horizontal SLG HUD preview
- RIGHT: isolated asset family sheet
- shared style: deep blue enamel panels, beveled gold trim, warm highlights, red badges, polished fantasy SLG icons
- asset sheet items: no dynamic text baked into item backgrounds

实际生成结果不只一张 board，还输出了若干独立资产图。实验选用了：

- `generated_src/full_hud.png`: 完整 HUD source
- `generated_src/production_board.png`: 左效果图 + 右资产族 board
- `generated_src/bottom_nav_button_bg_chroma.png`: 无字底部按钮底
- `generated_src/build_hammer_icon_chroma.png`: 独立锤子 icon
- `generated_src/red_badge_dot_chroma.png`: 独立红点 badge
- `generated_src/build_button_visual_state_chroma.png`: 烘焙式完整 BUILD 按钮，diagnostic only

## Current Finding

这条路线比“先效果图、后硬拆/重生成”更有希望，因为 standalone assets 与 full HUD 至少来自同一轮 style brief，风格族一致性明显更好。

但它还没有达到 PSD 级别的一一对应：

- full HUD 中的 BUILD 按钮和 standalone button assets 仍有细微变体
- Text Node 的字体、描边、阴影还需要工程侧调参
- generated asset 自然尺寸不能直接作为工程尺寸，仍需 Layer IR bbox 锁定
- diagnostic visual-state 更接近单张状态，但会烘焙文字和 icon，不适合作为长期可编辑资产

## Practical Conclusion

这条路线值得继续，但下一步不应该继续从单张效果图后处理，而应该增强生图阶段的约束：

1. 先固定 Asset / Layer Plan 和 asset ids。
2. 要求生成 `full_effect` 与 `asset_sheet` 都引用这些 asset ids。
3. asset sheet 使用更严格的网格、统一 chroma-key 背景、无 cell overlap。
4. 对重点控件输出 `visual_state` 与 `engineering_layers` 两套资产。
5. 用回贴验证筛选哪些资产可以自动进入工程，哪些需要人工修图。
