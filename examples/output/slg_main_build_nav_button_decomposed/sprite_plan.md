# Sprite Plan - Build Nav Button Decomposed

Source: `examples/input/slg_main.png`
Reference crop: `examples/output/slg_main_fidelity_experiment/reference_crops/build_nav_button_source_reference_crop.png`

## 自动确认
| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| build_button_bg | button_bg | assets_png/build_button_bg.png | standalone_sprite | 按钮底图应去掉 icon、红点和文字，保持可复用 |
| build_hammer_icon | icon | assets_png/build_hammer_icon.png | standalone_sprite | hammer 是独立功能 icon，应可单独替换和调尺寸 |
| build_badge_dot | badge_dot | assets_png/build_badge_dot.png | standalone_sprite | 通知红点应复用，不应烘焙进按钮底图 |
| build_label | dynamic/fixed label | 不生成 PNG | text_node | 本实验验证文字不烘焙，避免 AI 字体漂移 |

## 需要人工确认
无。本轮是用户确认后的最小实验，只验证 `button_bg + hammer_icon + badge_dot + Text Node` 是否优于整按钮生成。

## 注意
`reference_crops/` 和 crop proxy 仍只是对照，不是最终 sprite。
