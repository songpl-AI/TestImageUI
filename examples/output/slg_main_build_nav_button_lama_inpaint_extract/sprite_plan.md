# Sprite Plan - Build Nav Button LaMa Inpaint Extract

Source image: `examples/input/slg_main.png` (`1280x720`)
Reference crop: `examples/output/slg_main_fidelity_experiment/reference_crops/build_nav_button_source_reference_crop.png`
Component bbox: `[320, 560, 130, 152]`

This experiment tests the next bottleneck after SAM/rembg: whether LaMa can improve only the hidden holes in `button_bg` while reusing the existing foreground sprite layers.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| build_button_bg_lama_clean | button_bg | `assets_png/build_button_bg_lama_clean.png` | SAM button mask + child exclude mask + LaMa inpaint | 只测试底板遮挡洞，不重新生成整个按钮 |
| build_hammer_icon_sam_rembg_extract | icon | `assets_png/build_hammer_icon_sam_rembg_extract.png` | reuse previous SAM/rembg extract | 前景层上一轮已验证，本轮不改变量 |
| build_badge_dot_sam_rembg_extract | badge_dot | `assets_png/build_badge_dot_sam_rembg_extract.png` | reuse previous SAM/rembg extract | 前景层上一轮已验证，本轮不改变量 |
| build_label | dynamic_text | 不生成 PNG | text_node | 默认工程层仍保持文字可编辑 |

## 对照项

| id | 类型 | 输出 | 处理方式 | 用途 |
|---|---|---|---|---|
| build_label_fixed_art_sam_extract | fixed_art_text_optional | `assets_png/build_label_fixed_art_sam_extract.png` | reuse previous SAM extract | 排除 Text Node 字体漂移 |
| build_nav_button_visual_state_sam_rembg | visual_state_sprite_diagnostic | `assets_png/build_nav_button_visual_state_sam_rembg.png` | reuse previous visual-state | 视觉上限诊断，不作为工程拆分 sprite |

## 实验结果

- current independent delta: `45.2`
- manual layered + Text Node delta: `28.69`
- SAM/rembg layered + Text Node delta: `21.89`
- LaMa layered + Text Node delta: `20.67`
- manual layered + fixed text delta: `22.66`
- SAM/rembg layered + fixed text delta: `15.84`
- LaMa layered + fixed text delta: `14.59`
- visual-state diagnostic delta: `10.24`
- selected LaMa variant: `B tighter mask`

结论：LaMa 对底板补洞有小幅改善，但没有改变根本判断：它只能生成一个合理近似，不是恢复真实隐藏图层。
