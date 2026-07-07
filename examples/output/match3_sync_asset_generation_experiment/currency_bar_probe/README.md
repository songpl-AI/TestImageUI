# Currency Bar Probe

This probe tests the second engineering loop for the pastoral match-3 production board:

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
- `sprite_plan.md`: Sprite Plan for this probe.
- `sprite_manifest.json`, `layer_ir.json`, `layout_ir.json`: machine-readable probe metadata.
- `metrics.json`: comparison metrics.

## Metrics

| reconstruction | full-crop mean RGB delta | UI-mask mean RGB delta |
|---|---:|---:|
| asset assembly, contain bg | 66.34 | 66.34 |
| asset assembly, stretch bg | 67.39 | 67.39 |
| visual-state proxy, not sprite | 0.00 | 0.00 |

The visual-state proxy is only the source crop copied back as an upper bound. It is not a valid reusable sprite.

## Result

The asset-sheet reconstruction fails for a different reason than the `PLAY` button probe.

For the `PLAY` button, the generated asset was the right semantic object but needed better layout metadata, especially `scale_mode` and likely `nine_slice`.

For this currency bar, the asset identity itself is wrong:

- Full effect uses a dark brown capsule currency slot.
- Asset sheet provides a cream rounded panel with small leaves.
- `contain` and `stretch` both preserve the wrong asset variant.
- `nine_slice` would help only if the correct dark brown bar asset existed first.

The heart icon and plus button are structurally usable, but the bar background prevents the composed control from matching the full-effect UI.

## Key Conclusion

Synchronized generation is still useful, but the prompt must do more than list asset ids in a fixed grid. It must require that each `asset_sheet` cell is the exact reusable base layer used by `full_effect` for the matching layer id.

Future prompts should explicitly say:

```text
For every full_effect layer id, the matching asset_sheet cell must contain the same art variant, same silhouette, same material, same color family, and same border style, only with dynamic text and child elements removed.
```

This probe should be treated as a prompt-contract failure, not a sprite-extraction failure.
