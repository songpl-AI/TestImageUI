# Buy Button Background Probe

## Goal

Validate whether a production-board asset-sheet cell can become a usable engineering sprite:

```text
production_board asset cell
  -> transparent source sprite
  -> fit into spec bbox
  -> add Text Node
  -> compare with full-effect button crop
```

This probe only covers `buy_button_bg`. It does not validate the full screen.

## Inputs

- Source asset cell: `../spec_driven_realgen_validation/asset_cells/buy_button_bg.png`
- Full-effect reference crop: `../spec_driven_realgen_validation/full_crops/buy_button_bg.png`
- Spec source: `../spec_driven_shop_plan/ui_spec.json`

## Outputs

- `assets_png/buy_button_bg.png`: transparent source sprite extracted from the asset-sheet cell.
- `assets_fit_raw/buy_button_bg_contain.png`: source sprite fitted into the spec bbox with contain scaling.
- `assets_fit_raw/buy_button_bg_stretch.png`: source sprite fitted into the spec bbox with stretch scaling.
- `reconstruction_contain.png`: contain fit plus Text Node `BUY`.
- `reconstruction_stretch.png`: stretch fit plus Text Node `BUY`.
- `focused_button_probe_comparison.png`: local comparison of reference, source cell, transparent sprite, and both reconstructions.
- `sprite_overview.png`: checkerboard preview of the transparent source sprite.
- `layer_ir.json` / `layout_ir.json`: focused IR for the button probe.
- `sprite_manifest.json`: focused asset manifest.
- `probe_metrics.json`: extraction and comparison metrics.

## Result

The probe passes the minimum engineering check:

- The result is an RGBA PNG, not a rectangular RGB crop.
- All four corners are transparent.
- The button label is not baked into `assets_png/buy_button_bg.png`.
- The source sprite can be fitted into the JSON bbox `274x109`.
- Text Node `BUY` can be overlaid separately.

`stretch` is marginally closer than `contain` for this asset because the generated asset-sheet button already has a similar aspect ratio to the target bbox.

## Metrics

```text
source asset cell: 315x125
transparent source sprite: 315x124
target bbox: 274x109
text bbox relative to button: [58, 18, 158, 58]
corner alpha: [0, 0, 0, 0]
transparent pixel ratio: 0.2194
mean absolute delta vs scaled full crop:
  contain + Text Node: 56.76
  stretch + Text Node: 56.12
```

The numeric delta should be treated as a rough diagnostic only. The full-effect crop came from a generated production board region, not a strict `720x1280` source canvas, and the Text Node font is an approximation.

## Limitations

- This is still source-preserving extraction from an asset-sheet cell, not model-native transparent generation.
- The button includes leaf and flower decorations baked into the button asset. That is acceptable for this visual probe but should be confirmed as decoration ownership before engine production.
- The alpha extraction is hard-edged enough for a probe; a production pass should add soft-edge matte handling or use a cleaner chroma-key/native-alpha generation route.
- Text style is approximate. A production Text Node needs font, stroke, shadow, and vertical alignment calibration.

## Next Step

Repeat the same probe for `currency_bar_bg` or `price_tag_bg`. If two or three simple controls pass, then test a harder layer such as `main_panel_bg` with explicit decoration ownership split into `panel_base`, `title_board`, and `corner_decoration`.

