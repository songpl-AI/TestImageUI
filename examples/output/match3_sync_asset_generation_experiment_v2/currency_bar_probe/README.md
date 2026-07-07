# Currency Bar Probe - V2

This probe tests:

```text
full_effect heart currency bar
  vs
asset_sheet top_currency_bar_bg + heart_icon + plus_button + Text Node("5")
```

## Outputs

- `crops/source_heart_currency_bar_crop.png`: source crop from the top HUD.
- `debug/full_effect_currency_bbox_overlay.png`: source bbox overlay.
- `debug/source_currency_layer_overlay.png`: local layer bbox overlay.
- `reference_cells/`: asset sheet cells kept as references, not final sprites.
- `assets_png/`: transparent sprites extracted from asset sheet cells.
- `assets_fit_raw/`: layout instances fitted to the IR bboxes.
- `focused_currency_bar_fit_strategy_comparison.png`: source vs contain vs stretch vs visual-state proxy.
- `sprite_overview.png`: transparent sprite overview on checkerboard.
- `sprite_plan.md`: Sprite Plan.
- `sprite_manifest.json`, `layer_ir.json`, `layout_ir.json`: machine-readable metadata.
- `metrics.json`: comparison metrics.

## Metrics

| reconstruction | full-crop mean RGB delta | UI-mask mean RGB delta |
|---|---:|---:|
| asset assembly, contain bg | 55.30 | 55.30 |
| asset assembly, stretch bg | 54.70 | 54.70 |
| visual-state proxy, not sprite | 0.00 | 0.00 |

## Result

V2 fixed the biggest V1 issue for this component.

- V1 `top_currency_bar_bg` was a cream panel while full_effect used a dark brown resource slot.
- V2 `top_currency_bar_bg` is now a dark brown capsule resource-slot base.
- The remaining mismatch is mostly scale/insets, Text Node style, and small icon differences.

## Key Conclusion

The stricter layer-to-asset binding prompt helped. The next implementation issue is not another broad prompt redesign; it is adding `nine_slice`/fit metadata and better layer insets to the IR.
