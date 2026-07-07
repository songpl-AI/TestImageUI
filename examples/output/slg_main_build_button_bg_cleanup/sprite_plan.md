# Sprite Plan

Source image: `examples/input/slg_main.png` (`1280x720`)
Reference crop: `examples/output/slg_main_fidelity_experiment/reference_crops/build_nav_button_source_reference_crop.png`
Component bbox: `[320, 560, 130, 152]`

This is a narrow fidelity experiment for the BUILD nav button background. The source crop is only an edit target / reference. It is not a final sprite.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| build_button_bg_cleanup | button_bg | `assets_png/build_button_bg_cleanup.png` | edit_cleanup_inpaint_to_standalone_sprite | 验证从局部源图清理/补全按钮底板是否比从零生成更接近源图 |
| build_hammer_icon | icon | 复用上一轮 `build_hammer_icon.png` | reuse_existing_realgen_sprite | 本轮只隔离测试底板，不扩大变量 |
| build_badge_dot | badge_dot | 复用上一轮 `build_badge_dot.png` | reuse_existing_realgen_sprite | 本轮只隔离测试底板，不扩大变量 |
| build_label | dynamic_text | 不生成 PNG | text_node | BUILD 文案应保持可编辑 |

## 需要人工确认

| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| build_button_bg_cleanup | cleanup / inpaint | 推荐继续当前小实验 | 被锤子、红点和文字遮挡的区域无法从单张扁平图真实恢复，只能由生成模型补全；需要实验判断补全漂移是否低于从零生成 |

## 验证问题

- 与上一轮 decomposed realgen 相比，仅替换按钮底板后，局部平均 RGB delta 是否下降。
- 清理结果是否仍是独立透明 sprite，而不是带原背景、文字、icon、红点的矩形 crop。
- 如果不下降，说明 edit cleanup 仍不能稳定解决源图级视觉还原，需要考虑更偏人工/PSD/风格表/局部修图的方案。

## 实验结果

- 已生成 `assets_png/build_button_bg_cleanup.png`，它是透明独立按钮底板，不是源图 crop。
- 已输出 `sprite_overview.png`、`bbox_overlay.png`、`focused_cleanup_comparison.png`、`full_cleanup_comparison.png` 和 `experiment_manifest.json`。
- 局部平均 RGB delta：当前独立 sprite 45.20，crop proxy 0.00，整按钮真实生成 53.61，拆分真实生成 45.64，cleanup/inpaint 47.56。
- 结论：本次 cleanup/inpaint 没有接近 crop proxy 上限。模型补全出了更标准、更厚、更高清的按钮底板，工程上干净，但视觉上仍偏离源图。
