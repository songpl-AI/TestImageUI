# Pastoral Match-3 Sync Asset Generation Experiment V2

This experiment regenerates the pastoral match-3 production board with a stricter layer-to-asset binding prompt.

The main V1 failure was:

```text
full_effect top currency bar = dark brown capsule
asset_sheet top_currency_bar_bg = cream panel
```

V2 explicitly required the asset sheet to contain the same base art variant used by the matching full-effect layer, with only dynamic text and child layers removed.

## Generated Image

- `pastoral_match3_production_board_v2.png`
- Size: `889 x 1770`
- Split:
  - `split/full_effect.png`: `889 x 1105`
  - `split/asset_sheet.png`: `889 x 665`

## Result Summary

V2 is a meaningful improvement over V1 for the specific asset variant problem.

- The asset sheet keeps a clear 4x4 grid.
- `top_currency_bar_bg` is now a dark brown capsule resource-slot base, matching the full-effect currency bars much better than V1.
- `heart_icon`, `coin_icon`, `gem_icon`, `plus_button`, and `play_button_bg` are isolated enough for local sprite experiments.
- Dynamic text is still mostly limited to the full-effect UI.

The remaining problems are no longer primarily "wrong asset variant"; they are now closer to production layout problems:

- Need `scale_mode` and likely `nine_slice` metadata for bars/buttons.
- Need decoration ownership for flowers/leaves/end caps.
- Need better Text Node style matching.
- Some metrics are sensitive to source crop background and decoration pixels, so visual inspection remains necessary.

## Probe Results

### `currency_bar_probe`

Target:

```text
top_currency_bar_bg + heart_icon + plus_button + Text Node("5")
```

| reconstruction | full-crop mean RGB delta | UI-mask mean RGB delta |
|---|---:|---:|
| contain bg | 55.30 | 55.30 |
| stretch bg | 54.70 | 54.70 |
| visual-state proxy, not sprite | 0.00 | 0.00 |

V1 currency bar delta was around `66`, so V2 improved the exact problem we were testing: the background asset is now the correct dark-brown family. The remaining mismatch comes from fit/insets, text rendering, and small icon scale differences.

### `play_button_probe`

Target:

```text
play_button_bg + Text Node("PLAY")
```

| reconstruction | full-crop mean RGB delta | UI-mask mean RGB delta |
|---|---:|---:|
| contain bg | 51.59 | 51.59 |
| stretch bg | 54.17 | 54.17 |
| visual-state proxy, not sprite | 0.00 | 0.00 |

For PLAY, the metric is less reliable because the source crop includes side flower decorations and garden background pixels. Visually, stretch better matches the wide button body, but the asset sheet does not include the side flower decorations as separate assets. This still points to the same production need: `nine_slice` plus explicit decoration ownership.

## Practical Conclusion

The stricter prompt is worth keeping.

It did not solve everything, but it moved the failure mode from:

```text
asset sheet generated the wrong variant
```

to:

```text
asset variant is mostly right, but layout metadata and decoration ownership are still required
```

That is a better engineering position because `scale_mode`, `nine_slice`, Text Node styling, and decoration ownership can be represented in Layer IR / Layout IR.

## Files

- `generation_brief.md`: why this V2 exists.
- `strict_match3_prompt_v2.txt`: exact prompt used for generation.
- `pastoral_match3_production_board_v2.png`: generated production board copied into the workspace.
- `split_manifest.json`: split and 4x4 grid coordinates.
- `asset_sheet_grid_overlay.png`: grid audit image.
- `currency_bar_probe/`: focused currency bar reconstruction probe.
- `play_button_probe/`: focused PLAY button reconstruction probe.
- `experiment_manifest.json`: machine-readable summary.
