# Build Nav Button Realgen Experiment

This experiment tests whether a real generated composite sprite can approach the crop-proxy upper bound for `build_nav_button`.

Important distinction:

- `assets_png/build_nav_button_composite.png` is a real generated transparent sprite.
- The earlier crop proxy remains only an upper-bound reference and is not a final reusable sprite.

Generated component:

- Includes button background, hammer icon, red notification dot, and fixed `BUILD` label.
- Fits into bbox `[320, 560, 130, 152]` as `assets_fit_raw/build_nav_button_composite.png`.

Metrics, mean absolute RGB delta to the source crop:

- Current independent sprite reconstruction: `45.2`
- Crop proxy upper bound: `0.0`
- Real generated composite: `53.61`

Read:

The first real generated composite is structurally coherent, but it is visually more polished, larger, and bulkier than the source. It does not approach the crop proxy upper bound yet. This is useful evidence: component-level generation reduces some assembly drift, but a single generic generation pass is still not enough for source-like fidelity.

Review:

- `focused_realgen_comparison.png`
- `full_realgen_comparison.png`
- `sprite_overview.png`
- `experiment_manifest.json`
