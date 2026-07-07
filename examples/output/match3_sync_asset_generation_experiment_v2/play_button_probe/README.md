# PLAY Button Probe - V2

This probe tests:

```text
full_effect PLAY button
  vs
asset_sheet play_button_bg + Text Node("PLAY")
```

## Outputs

- `crops/source_play_button_crop.png`: source crop from the lower primary button.
- `debug/full_effect_play_bbox_overlay.png`: source bbox overlay.
- `debug/source_play_layer_overlay.png`: local layer bbox overlay.
- `reference_cells/`: asset sheet cell kept as reference, not final sprite.
- `assets_png/play_button_bg.png`: transparent button base extracted from the asset sheet cell.
- `assets_fit_raw/`: contain/stretch layout instances and Text Node preview.
- `focused_play_button_fit_strategy_comparison.png`: source vs contain vs stretch vs visual-state proxy.
- `sprite_overview.png`: transparent sprite overview on checkerboard.
- `sprite_plan.md`: Sprite Plan.
- `sprite_manifest.json`, `layer_ir.json`, `layout_ir.json`: machine-readable metadata.
- `metrics.json`: comparison metrics.

## Metrics

| reconstruction | full-crop mean RGB delta | UI-mask mean RGB delta |
|---|---:|---:|
| asset assembly, contain bg | 51.59 | 51.59 |
| asset assembly, stretch bg | 54.17 | 54.17 |
| visual-state proxy, not sprite | 0.00 | 0.00 |

The numeric metric is not very reliable for this crop because the source includes side flower decorations and garden background pixels. Visually, stretch better matches the wide green button body, while contain is obviously too small.

## Result

V2 provides the correct primary green button base, but it still does not provide the side flower decorations as separate assets.

This is no longer mainly an asset-variant mismatch. It is a production representation problem:

- button base should be `nine_slice`
- side flowers should be separate decoration sprites or explicitly baked into a visual-state button
- `PLAY` should remain a Text Node with tuned font/stroke/shadow

## Key Conclusion

The V2 prompt helped for base-asset identity, but it did not eliminate the need for explicit decoration ownership and scale metadata.
