# Sprite Plan - SLG Sync Effect + Asset Generation Experiment

Source effect image: `generated_src/full_hud.png`

This is not a normal post-hoc extraction test. The full HUD and the standalone assets were generated from the same production-board prompt/run, then the BUILD button was reconstructed from the generated standalone assets.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| bottom_nav_button_bg | button_bg | `assets_png/bottom_nav_button_bg.png` | synchronized_generated_sprite | 同步生成得到的无字按钮底，不是 source crop |
| build_hammer_icon | icon | `assets_png/build_hammer_icon.png` | synchronized_generated_sprite | 同步生成得到的独立 hammer icon |
| red_badge_dot | badge_dot | `assets_png/red_badge_dot.png` | synchronized_generated_sprite | 同步生成得到的独立红点 badge |
| build_label_text | dynamic_text | 不生成 PNG | text_node | BUILD 文案应保持可编辑 |

## 需要人工确认

| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| build_button_visual_state | visual_state_sprite / diagnostic | diagnostic only | 完整 BUILD 按钮更接近视觉状态，但烘焙了 icon、badge 和文字，不适合长期工程复用 |
| button_shadow | shadow / baked_into_bg / follow_icon | needs_manual_shadow_review | 同步生成资产仍无法自动确定接触阴影归属 |
| build_label_font | Text Node style | needs_text_style_tuning | 字体、描边和投影需要工程侧调参才能接近 source |

## Initial Metrics

See `experiment_manifest.json`.

The raw RGB delta is high because this first validation compares generated transparent assets on a checker/source background against a full source crop that contains local scene pixels and slightly different generated variants. The more useful observation in this phase is qualitative: style family consistency is much better than the previous isolated realgen attempts, but the generated assets are still not pixel-identical to the full HUD state.

## Conclusion

The synchronized generation direction is worth continuing. It does not remove the need for Layer IR, Text Node tuning, or manual review, but it changes the problem from "recover hidden layers from a flat image" to "generate a coherent asset family before reconstruction", which is a more controllable production path.
