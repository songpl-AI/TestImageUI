# Build Nav Button Decomposed Realgen Experiment

This experiment tests `button_bg + hammer_icon + badge_dot + Text Node` for the SLG BUILD nav button.

It is different from the previous whole-button experiment:

- button background is generated alone, with no icon, badge, or text.
- hammer icon is generated alone.
- red badge dot is generated alone.
- `BUILD` is drawn as a Text Node.

Metrics, mean absolute RGB delta to the source crop:

- Current independent sprite reconstruction: `45.2`
- Crop proxy upper bound: `0.0`
- Whole-button realgen: `53.61`
- Decomposed realgen + Text Node: `45.64`

Review:

- `focused_decomposed_comparison.png`
- `full_decomposed_comparison.png`
- `sprite_overview.png`
- `bbox_overlay.png`
- `sprite_manifest.json`
