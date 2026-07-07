# Spec Validation Report

## Summary

- Screen: `spec_driven_shop_bundle`
- Canvas: 720x1280
- Layers: 33
- Image layers: 21
- Text nodes: 12
- Reusable assets: 15
- Assets reused by multiple layers: 3
- Validation errors: 0
- Validation warnings: 2

## Contract Check

- JSON is the layout source of truth.
- Dynamic text is represented as Text Node layers.
- Sprite source assets and fitted layout instances are separated.
- Stretchable backgrounds carry `scale_mode` metadata.
- Prompts explicitly forbid rectangular crop semantics.

## Errors
- None

## Warnings
- offline validation only: no real full_effect or sprite PNG was generated
- variant mismatch remains possible between full_effect and independent asset prompts

## Reuse Map
- `discount_badge_bg` -> product_card_1_discount_badge_bg, product_card_2_discount_badge_bg, product_card_3_discount_badge_bg
- `price_tag_bg` -> product_card_1_price_tag_bg, product_card_2_price_tag_bg, product_card_3_price_tag_bg
- `product_card_bg` -> product_card_1_bg, product_card_2_bg, product_card_3_bg

## Validation Result

This validates the spec contract and artifact graph only. The next test should generate one production board or 1-2 representative assets, then compare the reconstruction against the full effect.
