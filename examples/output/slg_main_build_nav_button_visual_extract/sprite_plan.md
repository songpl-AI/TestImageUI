# Sprite Plan - Build Nav Button Visual Extract

Source image: `examples/input/slg_main.png` (`1280x720`)
Reference crop: `examples/output/slg_main_fidelity_experiment/reference_crops/build_nav_button_source_reference_crop.png`
Component bbox: `[320, 560, 130, 152]`

This experiment tests a source-preserving extraction strategy. The final sprite is not a rectangular crop: map/background pixels outside the semantic button silhouette are transparent, while the visible button state keeps source pixels.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| build_nav_button_visual_state | visual_state_sprite | `assets_png/build_nav_button_visual_state.png` | source_preserving_mask_extract | 当前目标是让生成图像效果图，不优先追求文字可编辑或底板复用 |

## 需要人工确认

| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| build_nav_button_visual_state | visual_state_sprite / engineering_split | 本轮推荐 visual_state_sprite | 它保留 BUILD 文字、锤子和红点，牺牲复用性换取视觉接近源图 |

## 实验结果

- 已生成透明 PNG：`assets_png/build_nav_button_visual_state.png`。
- 它保留按钮区域源图像素，周围地图背景通过非矩形 alpha mask 去掉。
- 局部 delta：current independent 45.20；decomposed 45.64；cleanup 47.56；visual extract on source bg 0.00；visual extract on current bg 4.63。
- alpha-mask 区域 delta：visual extract on current bg 1.56。
- 结论：source-preserving visual sprite 能显著保留源图视觉，但不是高度可复用工程拆分资产。
