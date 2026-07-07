# PLAY Button Probe

This probe tests the first engineering loop for the pastoral match-3 production board:

```text
full_effect PLAY button
  vs
asset_sheet play_button_bg + Text Node
```

## Outputs

- `split/full_effect.png`: top full UI section.
- `split/asset_sheet.png`: bottom 4x4 asset sheet section.
- `asset_sheet_grid_overlay.png`: asset sheet cells with planned ids.
- `reference_cells/`: cell crops, kept only as references, not final sprites.
- `assets_png/play_button_bg.png`: alpha-cleaned sprite from the asset sheet cell.
- `assets_fit_raw/play_button_bg.png`: contain-fit layout instance.
- `assets_fit_raw/play_button_bg_stretch_fit.png`: stretch-fit layout instance.
- `focused_play_button_comparison.png`: source vs contain fit reconstruction.
- `focused_play_button_fit_strategy_comparison.png`: source vs contain vs stretch.
- `sprite_plan.md`: Sprite Plan and manual confirmation items.
- `sprite_manifest.json`, `layer_ir.json`, `layout_ir.json`: machine-readable probe metadata.

## Result

The first contain-fit reconstruction failed visually because `play_button_bg` became too short. A stretch-fit version was much closer, which means the important next requirement is not another image generation attempt; it is better layout metadata.

## Key Conclusion

The synchronized `full_effect + asset_sheet` route is promising, but reusable backgrounds need explicit fit strategy:

- `contain` is wrong for wide button backgrounds.
- `stretch` is closer, but can distort corners and leaves.
- `nine_slice` is the likely correct engine representation.

The probe also shows that full-effect flower decorations are not represented in the asset sheet `play_button_bg`. Future Asset / Layer Plans should explicitly say whether flower decorations are part of the button background or separate decoration sprites.
