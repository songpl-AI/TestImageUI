# spec_driven_product_card_split_contract Contract Validation

## Result

`spec_driven_product_card_split_contract` validation result: **pass**.

## Evidence

- Board size: `1536x1024`.
- Asset cells: `6`.
- Primary asset: `product_card_base`.
- Primary source cell: `358x365`.
- Primary transparent candidate: `280x329`.
- Primary corner alpha: `[0, 0, 0, 0]`.
- Validation errors: `0`.
- Failed checks: `0`.

## Contract Checks

```json
{
  "product_card_base_has_low_red_child_signal": {
    "asset_id": "product_card_base",
    "metric": "red_ratio_hsv",
    "op": "<=",
    "value": 0.01,
    "actual": 0.0,
    "pass": true
  },
  "product_card_base_has_low_green_icon_signal": {
    "asset_id": "product_card_base",
    "metric": "green_ratio",
    "op": "<=",
    "value": 0.01,
    "actual": 0.0,
    "pass": true
  },
  "product_card_base_has_low_dark_text_signal": {
    "asset_id": "product_card_base",
    "metric": "dark_text_like_ratio",
    "op": "<=",
    "value": 0.01,
    "actual": 0.0,
    "pass": true
  },
  "product_card_base_has_cream_surface_signal": {
    "asset_id": "product_card_base",
    "metric": "cream_ratio",
    "op": ">=",
    "value": 0.25,
    "actual": 0.9333,
    "pass": true
  },
  "reward_icon_has_red_apple_signal": {
    "asset_id": "reward_icon_basket",
    "metric": "red_ratio_hsv",
    "op": ">=",
    "value": 0.2,
    "actual": 0.3194,
    "pass": true
  },
  "quantity_pill_bg_has_low_dark_text_signal": {
    "asset_id": "quantity_pill_bg",
    "metric": "dark_text_like_ratio",
    "op": "<=",
    "value": 0.02,
    "actual": 0.0,
    "pass": true
  },
  "discount_badge_bg_has_red_material_signal": {
    "asset_id": "discount_badge_bg",
    "metric": "red_ratio_hsv",
    "op": ">=",
    "value": 0.45,
    "actual": 0.8022,
    "pass": true
  },
  "price_tag_bg_has_gold_material_signal": {
    "asset_id": "price_tag_bg",
    "metric": "gold_ratio",
    "op": ">=",
    "value": 0.35,
    "actual": 0.9106,
    "pass": true
  },
  "product_card_base_has_clean_corners": {
    "asset_id": "product_card_base",
    "metric": "corner_alpha_max",
    "op": "==",
    "value": 0.0,
    "actual": 0.0,
    "pass": true
  },
  "manual_visual_check": {
    "product_card_base_excludes_reward_icon": {
      "status": "pass",
      "description": "The product card base cell contains no apples or basket."
    },
    "product_card_base_excludes_quantity_discount_price": {
      "status": "pass",
      "description": "The product card base cell contains no quantity text, discount badge, or price tag."
    },
    "child_backgrounds_exclude_text": {
      "status": "pass",
      "description": "Quantity pill, discount badge, and price tag cells are text-free."
    }
  }
}
```

## Interpretation

This validates whether the production-board asset sheet respects nested product-card parent/child ownership. It does not prove final engine-ready sprite quality.

## Files

- `layer_contract.json`: copied input contract.
- `production_board.png`: copied source board.
- `bbox_overlay.png`: board with asset-cell boxes.
- `asset_cells/*.png`: source cell crops for audit.
- `assets_png/*.png`: transparent candidates extracted from source cells.
- `assets_fit_raw/*.png`: rough layout instances when rough reconstruction is configured.
- `sprite_overview.png`: transparent candidate overview.
- `focused_split_comparison.png`: cell-to-transparent-candidate comparison.
- `rough_reconstruction.png`: rough reconstruction when configured.
- `rough_reconstruction_comparison.png`: source / reconstruction / reference comparison when configured.
- `probe_metrics.json`: machine-readable metrics.
- `sprite_manifest.json`, `layer_ir.json`, `layout_ir.json`: validation metadata.

## Verdict

```text
product card parent/child split contract: pass when all configured checks pass
```
