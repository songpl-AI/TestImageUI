# Sprite Plan - Build Nav Button Hammer Shadow Layer Attribution

Source image: `examples/input/slg_main.png` (`1280x720`)
Reference crop: `examples/output/slg_main_fidelity_experiment/reference_crops/build_nav_button_source_reference_crop.png`
Component bbox: `[320, 560, 130, 152]`

This experiment tests whether the hammer shadow should be separated from `button_bg` and owned by the hammer stack.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| build_button_bg_shadow_clean | button_bg | `assets_png/build_button_bg_shadow_clean.png` | SAM button mask + LaMa inpaint entity+shadow holes | 底板应去掉锤子、文字、红点以及锤子投影残留 |
| hammer_shadow | drop_shadow | `assets_png/hammer_shadow.png` | source darkening shadow layer | 验证 shadow 是否应跟随 hammer stack，而不是烘焙在 button_bg 内 |
| build_hammer_icon_sam_rembg_extract | icon | `assets_png/build_hammer_icon_sam_rembg_extract.png` | reuse previous SAM/rembg extract | 前景锤子层已验证，本轮不重做 |
| build_badge_dot_sam_rembg_extract | badge_dot | `assets_png/build_badge_dot_sam_rembg_extract.png` | reuse previous SAM/rembg extract | 前景红点层已验证，本轮不重做 |
| build_label | dynamic_text | 不生成 PNG | text_node | 默认工程层保持文字可编辑 |

## 对照项

| id | 类型 | 输出 | 用途 |
|---|---|---|---|
| build_label_fixed_art_sam_extract | fixed_art_text_optional | `assets_png/build_label_fixed_art_sam_extract.png` | 排除 Text Node 字体漂移 |
| build_nav_button_visual_state_sam_rembg | visual_state_sprite_diagnostic | `assets_png/build_nav_button_visual_state_sam_rembg.png` | 视觉上限诊断 |

## 实验结果

- previous LaMa + Text Node delta: `20.67`
- shadow layer `small` + Text Node delta: `20.8`
- previous LaMa + fixed text delta: `14.59`
- shadow layer `small` + fixed text delta: `14.71`
- selected shadow variant: `small`
- visual-state diagnostic delta: `10.24`

Conclusion: see `focused_shadow_layer_fixed_comparison.png`, `focused_shadow_ablation_comparison.png`, and `sprite_overview.png`.
