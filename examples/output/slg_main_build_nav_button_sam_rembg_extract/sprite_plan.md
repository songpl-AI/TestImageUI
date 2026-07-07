# Sprite Plan - Build Nav Button SAM/rembg Extract

Source image: `examples/input/slg_main.png` (`1280x720`)
Reference crop: `examples/output/slg_main_fidelity_experiment/reference_crops/build_nav_button_source_reference_crop.png`
Component bbox: `[320, 560, 130, 152]`

This experiment validates whether third-party segmentation/refine tools can replace the rough manual masks used in the previous layered source extraction.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| build_button_bg_sam_clean | button_bg | `assets_png/build_button_bg_sam_clean.png` | SAM2 button mask + rembg edge + OpenCV local fill | 底板必须独立透明且去掉锤子/红点/文字；本轮不使用 LaMa |
| build_hammer_icon_sam_rembg_extract | icon | `assets_png/build_hammer_icon_sam_rembg_extract.png` | SAM2 mask + rembg alpha refine + source extract | 锤子是前景可见层，适合非矩形提取 |
| build_badge_dot_sam_rembg_extract | badge_dot | `assets_png/build_badge_dot_sam_rembg_extract.png` | SAM2 mask + rembg alpha refine + source extract | 红点边界清楚，适合验证小物件分割 |
| build_label | dynamic_text | 不生成 PNG | text_node | 默认工程层仍保持文字可编辑 |

## 对照项

| id | 类型 | 输出 | 处理方式 | 用途 |
|---|---|---|---|---|
| build_label_fixed_art_sam_extract | fixed_art_text_optional | `assets_png/build_label_fixed_art_sam_extract.png` | SAM2 source extract | 排除 Text Node 字体漂移，判断 mask 上限 |
| build_nav_button_visual_state_sam_rembg | visual_state_sprite_diagnostic | `assets_png/build_nav_button_visual_state_sam_rembg.png` | SAM2 whole mask + rembg alpha | 视觉态上限诊断，不作为最终工程拆分 sprite |

## 实验约束

- 不把矩形 crop 当最终 sprite。
- 不使用 LaMa / generative inpaint；底板遮挡洞只用 OpenCV 小半径局部补洞。
- Text Node 是默认工程方案，fixed text 只做视觉指标对照。

## 实验结果

- current independent delta: `45.2`
- previous layered + Text Node delta: `28.69`
- previous layered + fixed text delta: `22.66`
- SAM/rembg layered + Text Node delta: `21.89`
- SAM/rembg layered + fixed text delta: `15.84`
- SAM/rembg visual-state diagnostic delta: `10.24`

结论：SAM/rembg 明显提升了前景层 mask 和视觉态提取；真正的剩余瓶颈是底板被锤子/文字遮挡后的隐藏像素恢复，非生成式补洞只能近似。
