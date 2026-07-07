# Sprite Plan - Pastoral Match-3 PLAY Button Probe

Source production board: `../pastoral_match3_production_board.png`

This probe validates whether the asset sheet's reusable `play_button_bg` can reconstruct the `PLAY` button in the full-effect UI with a Text Node.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| play_button_bg | button_bg | `assets_png/play_button_bg.png` | asset_sheet_extract_then_alpha_clean | asset sheet 中已有无文字按钮底，符合可复用底板目标 |
| play_button_text | dynamic_text | 不生成 PNG | text_node | `PLAY` 是按钮文案，应保持可编辑 |

## 需要人工确认

| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| play_button_flower_decorations | decoration / baked_into_button_bg | 推荐人工确认 | full_effect 按钮左右有白花装饰，但 asset_sheet 的 `play_button_bg` 只保留叶子端点，装饰归属不一致 |
| play_button_scale_mode | contain / stretch / nine_slice | 推荐 nine_slice | 普通 contain fit 明显过短，stretch fit 更接近，但会拉伸边角；正式工程应记录九宫格边界 |
| play_button_shadow | baked_shadow / separate_shadow | 推荐 baked_shadow + review | full_effect 中按钮阴影和周围草地交互明显，asset_sheet 无法自动表达阴影归属 |
| play_button_text_style | Text Node style | 需要调参 | 当前 Text Node 字重、描边、阴影接近但不等同 full_effect |

## Metrics

Mean RGB delta, lower is closer:

| reconstruction | full crop delta | alpha mask delta | 结论 |
|---|---:|---:|---|
| contain fit + Text Node | 112.09 | 81.62 | 失败，按钮底太短 |
| stretch fit + Text Node | 84.30 | 61.21 | 明显改善，但仍缺花朵/阴影/九宫格 |

## Conclusion

This validates the synchronized-generation direction as a useful production path, but also exposes a new requirement:

- asset sheet backgrounds need `scale_mode` metadata, usually `nine_slice`, not only bbox fit.
- asset plan must explicitly say whether decorative flowers/leaves are part of `play_button_bg` or separate decoration layers.
- full_effect and asset_sheet are visually related, but not exact PSD layers.

The next recommended component is `top_currency_bar`, because it tests `bar_bg + icon + plus_button + Text Node` composition and exposes whether the asset sheet `top_currency_bar_bg` matches the full-effect currency bars.
