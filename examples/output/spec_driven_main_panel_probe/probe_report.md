# Main Panel Background Probe

## Result

`main_panel_bg` **fails as a clean engineering panel background** in this production-board sample.

The generated asset-sheet cell is visually coherent with the full UI, but it is not the layer requested by the spec. It contains a title plaque and floral/leaf decoration, so it is a composite UI piece rather than a clean `main_panel_bg` base.

## What Was Tested

```text
asset_cells/main_panel_bg.png
  -> transparent composite sprite
  -> contain/stretch fit to spec bbox 600x922
  -> diagnostic crop removing the top title-plaque band
  -> focused comparison against the generated full-effect panel crop
```

## Evidence

- Source cell size: `334x298`
- Spec target bbox: `600x922`
- Full-effect crop size: `706x782`
- Composite sprite size: `319x298`
- Panel-base candidate size: `318x232`
- Composite stretch delta: `56.22`
- Panel-base candidate stretch delta: `70.93`

## Interpretation

This confirms the earlier `production-board-layer-ownership-drift` risk. The production board is useful as a style/material reference, but it cannot be trusted to export `main_panel_bg` as a correct layer. For this component, the next prompt/spec must split the panel into explicit children:

```text
panel_base
panel_corner_flowers
panel_bottom_leaves
panel_top_title_plate
panel_inner_texture
```

Only `panel_base` should be evaluated as the clean panel background. The current `main_panel_bg_composite` can be kept as a visual reference, not as an engine-ready sprite.

## Files

- `assets_png/main_panel_bg_composite.png`: transparent composite extracted from the asset cell.
- `assets_png/panel_base_candidate.png`: diagnostic crop after removing the top title-plaque band.
- `assets_fit_raw/main_panel_bg_composite_stretch.png`: composite fitted into `600x922`.
- `assets_fit_raw/panel_base_candidate_stretch.png`: diagnostic base candidate fitted into `600x922`.
- `focused_probe_comparison.png`: visual audit.
- `sprite_overview.png`: transparent sprite overview.
- `probe_metrics.json`: machine-readable measurements.

## Verdict

```text
main_panel_bg clean base: fail
main_panel_bg composite style reference: usable
panel_base_candidate: diagnostic only, not production-ready
```
