# Sprite Plan

Source: spec-driven plan for `spec_driven_shop_bundle`.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| background_scene | background_scene | assets_png/background_scene.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| buy_button_bg | button_background | assets_png/buy_button_bg.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| close_button | close_button | assets_png/close_button.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| coin_icon | currency_icon | assets_png/coin_icon.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| currency_bar_bg | currency_bar_background | assets_png/currency_bar_bg.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| discount_badge_bg | discount_badge_background | assets_png/discount_badge_bg.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| hot_deal_ribbon_bg | subtitle_ribbon_background | assets_png/hot_deal_ribbon_bg.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| main_panel_bg | panel_background | assets_png/main_panel_bg.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| price_tag_bg | price_tag_background | assets_png/price_tag_bg.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| product_card_bg | product_card_background | assets_png/product_card_bg.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| reward_icon_1 | reward_item_icon | assets_png/reward_icon_1.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| reward_icon_2 | reward_item_icon | assets_png/reward_icon_2.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| reward_icon_3 | reward_item_icon | assets_png/reward_icon_3.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| title_board | title_board | assets_png/title_board.png | standalone_sprite | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴，禁止烘焙动态文字 |
| title_logo | fixed_art_text | assets_png/title_logo.png | fixed_art_text | 独立 UI 素材，由 JSON bbox 和 scale_mode 回贴 |
| currency_amount_text | dynamic_text_currency_amount | 不生成 PNG | text_node | 动态文字保持可编辑：3200 |
| hot_deal_text | dynamic_text_subtitle | 不生成 PNG | text_node | 动态文字保持可编辑：HOT DEAL |
| product_card_1_discount_text | dynamic_text_discount | 不生成 PNG | text_node | 动态文字保持可编辑：20% |
| product_card_1_count_text | dynamic_text_item_count | 不生成 PNG | text_node | 动态文字保持可编辑：x50 |
| product_card_1_price_text | dynamic_text_price | 不生成 PNG | text_node | 动态文字保持可编辑：$3 |
| product_card_2_discount_text | dynamic_text_discount | 不生成 PNG | text_node | 动态文字保持可编辑：40% |
| product_card_2_count_text | dynamic_text_item_count | 不生成 PNG | text_node | 动态文字保持可编辑：x3 |
| product_card_2_price_text | dynamic_text_price | 不生成 PNG | text_node | 动态文字保持可编辑：$6 |
| product_card_3_discount_text | dynamic_text_discount | 不生成 PNG | text_node | 动态文字保持可编辑：60% |
| product_card_3_count_text | dynamic_text_item_count | 不生成 PNG | text_node | 动态文字保持可编辑：x1 |
| product_card_3_price_text | dynamic_text_price | 不生成 PNG | text_node | 动态文字保持可编辑：$9 |
| buy_button_text | dynamic_text_button_label | 不生成 PNG | text_node | 动态文字保持可编辑：BUY |

## 需要人工确认

| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| title_logo | fixed_art_text / text_node | 当前按 fixed_art_text | 标题是否需要本地化会影响是否图片化 |
| main_panel_bg | whole_panel / split_parts | 当前按 whole_panel + child layers | 面板角装饰未来可能需要单独复用 |
| discount_badge_bg | baked ribbon / split decoration | 当前按 reusable badge bg | 折扣样式是否所有商品共用需要确认 |
| production_board | full_effect + asset_sheet | 推荐用于真实生图小实验 | 可降低但不能消除整图和单图 variant mismatch |

## 尺寸与位置规则

- `ui_spec.json` / `layer_ir.json` 是尺寸、位置、层级的来源。
- `assets_png` 是可复用源素材，不能把自然尺寸当工程尺寸。
- `assets_fit_raw` 是每个 layer 的 bbox 实例，重建时引用它。
- 真实生成后必须输出 reconstruction / comparison 再判断是否推广。
