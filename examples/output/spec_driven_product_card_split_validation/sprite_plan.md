# Sprite Plan

Source image: pending generated `production_board.png`.
Scope: validate product card parent/child layer ownership from a production board. This is not a final production sprite export.

## Automatically Confirmed

| id | type | output | processing | reason |
|---|---|---|---|---|
| product_card_base | card_bg | assets_png/product_card_base.png | source_preserving_validation_extract | Parent card background must exclude all children. |
| reward_icon_basket | reward_icon | assets_png/reward_icon_basket.png | source_preserving_validation_extract | Item art should be independent and reusable. |
| quantity_pill_bg | small_badge_bg | assets_png/quantity_pill_bg.png | source_preserving_validation_extract | Quantity value is dynamic text, not baked into PNG. |
| discount_badge_bg | badge_bg | assets_png/discount_badge_bg.png | source_preserving_validation_extract | Discount value is dynamic text, not baked into PNG. |
| price_tag_bg | price_bg | assets_png/price_tag_bg.png | source_preserving_validation_extract | Price value is dynamic text, not baked into PNG. |
| full_product_card_composite_reference | visual_reference | assets_png/full_product_card_composite_reference.png | reference_only | Useful audit reference, not a clean reusable base. |

## Text Nodes

| id | text | reason |
|---|---|---|
| quantity_text | x25 | Dynamic reward amount. |
| discount_text | -30% | Dynamic promotion value. |
| price_text | $1.99 | Dynamic store price. |

## Needs Human Confirmation Before Production

| id | recommendation | why |
|---|---|---|
| product_card_base | accept/reject split direction before production regeneration | Current validation uses board-cell extraction, not final native transparent generation. |
| reward_icon_basket | confirm whether basket + apples is one icon or basket and apples should be split | Depends on inventory reuse requirements. |
| quantity_pill_bg | confirm if quantity should be plain Text Node directly on card or on a small pill background | The source visual may use a small bg behind text. |
| discount_badge_bg / price_tag_bg | confirm scale mode and text style metadata | Text layout and nine-slice details need engine-specific metadata. |
