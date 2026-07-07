# Sprite Plan - Build Nav Button Layered Source Extract

Source image: `examples/input/slg_main.png` (`1280x720`)
Reference crop: `examples/output/slg_main_fidelity_experiment/reference_crops/build_nav_button_source_reference_crop.png`
Component bbox: `[320, 560, 130, 152]`

This experiment validates the layer-first target: identify the BUILD button group, split it into layer assets, and reconstruct from Layer IR while preserving source visual style as much as possible.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| build_button_bg_source_clean | button_bg | `assets_png/build_button_bg_source_clean.png` | source_preserve_clean + local_fill | 保留可见源图像素，只补锤子/红点/文字遮挡区域 |
| build_hammer_icon_source_extract | icon | `assets_png/build_hammer_icon_source_extract.png` | source_mask_extract | 锤子图标可见，适合从源图非矩形提取 |
| build_badge_dot_source_extract | badge_dot | `assets_png/build_badge_dot_source_extract.png` | source_mask_extract | 红点可见且边界明确 |
| build_label | dynamic_text | 不生成 PNG | text_node | 文字应可编辑，回贴时按 IR 绘制 |

## 需要人工确认

| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| build_button_bg_source_clean | source_clean / AI inpaint | 本轮先 source_clean + local_fill | 锤子遮挡区域较大，若要求更干净底板，后续可用 reference_package 中的 crop + mask 做 AI inpaint |
| build_hammer_icon_source_extract | source_extract / generated_icon | 推荐 source_extract | 它最接近源图，但边缘 mask 需要人工可调 |

## 实验结果

- 已输出 3 个透明 sprite 和 1 个 Text Node。
- 已输出 reference package：`reference_package/`，包含局部截图、target mask、exclude mask，可用于后续 crop + prompt + mask 增强生成。
- 局部 delta：current independent 45.20；decomposed 45.64；cleanup 47.56；visual state 4.63；layered source extract 28.45。
- layer mask delta：layered source extract 25.83。
- 结论：layer-first 拆分能保留图层关系并明显优于纯 AI 重新生成；但 Text Node 字体和底板补洞仍是主要残差。


## fixed text 对照

- 默认工程还原仍使用 `build_label` Text Node。
- 另外输出了可选 `build_label_fixed_art_source_extract.png`，用于判断文字渲染漂移对还原的影响。
- layered + Text Node delta：28.69。
- layered + fixed text delta：22.66。
