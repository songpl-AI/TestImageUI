# Product Card Split Validation Brief

## Goal

Validate whether a stronger natural-language + JSON-style parent/child layer contract can make a generated production board separate a shop product card into engineering-oriented layers.

This follows the successful `panel_base` split validation and targets a harder nested component:

```text
product_card_base
reward_icon
quantity_pill_bg
discount_badge_bg
price_tag_bg
dynamic Text Nodes
```

## Hypothesis

If the prompt explicitly declares parent/child ownership and sibling exclusions, the asset sheet may produce a clean `product_card_base` without baking in the reward icon, quantity text, discount badge, or price tag.

## Hard Acceptance Checks

- `product_card_base` contains only the cream/gold rounded card frame and inner surface.
- `product_card_base` does not contain item art, quantity text, discount badge, price tag, shadow from child layers, or any dynamic text.
- `reward_icon_basket` contains only the fruit basket reward art and does not include the card frame.
- `quantity_pill_bg`, `discount_badge_bg`, and `price_tag_bg` are text-free.
- Dynamic text remains text nodes: `x25`, `-30%`, `$1.99`.
- `full_product_card_composite_reference` may show the assembled empty card module, but is marked reference-only.

## Failure Signals

- The asset sheet gives a `product_card_base` that still includes apples, text, badge, or price.
- The reward icon includes the card background or quantity row.
- The badge or price tag cell contains baked text.
- The full UI uses one visual variant, but asset cells show a different card style.
