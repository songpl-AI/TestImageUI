# Product Card Split Contract Validation

## Result

The product-card parent/child split contract is a **pass for layer-ownership direction** in this sample.

The generated asset sheet produced a `product_card_base` cell that is visually separated from the reward icon, quantity text, discount badge, and price tag. The child backgrounds also appear as text-free layer candidates.

## Evidence

- Board size: `1536x1024`.
- Asset sheet layout: `2x3` grid with six requested cells.
- `product_card_base` source cell: `358x365`.
- `product_card_base` transparent candidate: `280x329`.
- `product_card_base` corner alpha: `[0, 0, 0, 0]`.
- `product_card_base` red child signal: `0.0`.
- `product_card_base` green icon signal: `0.0`.
- `product_card_base` dark text-like signal: `0.0`.
- `product_card_base` cream surface signal: `0.9333`.

## Contract Checks

```json
{
  "product_card_base_has_low_red_child_signal": true,
  "product_card_base_has_low_green_icon_signal": true,
  "product_card_base_has_low_dark_text_signal": true,
  "product_card_base_has_cream_surface_signal": true,
  "reward_icon_has_red_apple_signal": true,
  "reward_icon_has_green_leaf_signal": true,
  "quantity_pill_bg_has_low_dark_text_signal": true,
  "discount_badge_bg_has_red_material_signal": true,
  "price_tag_bg_has_gold_material_signal": true,
  "manual_visual_check": {
    "product_card_base_excludes_reward_icon": "pass",
    "product_card_base_excludes_quantity_text": "pass",
    "product_card_base_excludes_discount_badge": "pass",
    "product_card_base_excludes_price_tag": "pass",
    "reward_icon_excludes_card_base": "pass",
    "quantity_pill_bg_excludes_text": "pass",
    "discount_badge_bg_excludes_text": "pass",
    "price_tag_bg_excludes_text": "pass"
  }
}
```

## Interpretation

This validates the next step after `panel_base` splitting: a stronger parent/child prompt contract can also improve nested component layer ownership.

```text
product card composite -> card_base + reward_icon + quantity_pill_bg + discount_badge_bg + price_tag_bg + Text Nodes
```

It still does **not** prove that the production board directly exports final engine-ready sprites. These PNGs are transparent candidates extracted from rendered asset cells. Production still needs exact engine bboxes, scale modes, font/stroke metadata, soft alpha polish, and preferably model-native or edit-assisted per-asset output.

## Files

- `production_board.png`: generated product-card split-contract board.
- `bbox_overlay.png`: board with audited asset-cell boxes and full-effect product-card crop.
- `asset_cells/*.png`: source cell crops for audit.
- `assets_png/*.png`: transparent candidates extracted from source cells.
- `assets_fit_raw/*.png`: rough layout instances for the probe reconstruction.
- `sprite_overview.png`: transparent candidate overview.
- `focused_split_comparison.png`: cell-to-transparent-candidate comparison.
- `rough_product_card_reconstruction.png`: rough reconstruction assembled from split assets and Text Nodes.
- `rough_product_card_reconstruction_comparison.png`: source crop / rough reconstruction / composite reference comparison.
- `probe_metrics.json`: machine-readable metrics.
- `sprite_manifest.json`, `layer_ir.json`, `layout_ir.json`: focused validation metadata.

## Verdict

```text
product card parent/child split contract: pass for layer-ownership direction
product_card_base as clean production sprite: candidate only, not final
next validation: formalize the JSON schema/prompt template or test one per-asset native transparent generation pass
```
