# Panel Split Contract Validation

## Result

The split-contract production board is a **meaningful improvement** over the previous `main_panel_bg` probe.

The new asset sheet produced a `panel_base` cell that is visually separated from the title plaque and floral/leaf decorations. This directly addresses the earlier layer-ownership drift where `main_panel_bg` baked the title plate and decorations into one composite asset.

## Evidence

- Board size: `1536x1024`.
- Asset sheet layout: `2x3` grid with six requested cells.
- `panel_base` source cell: `358x365`.
- `panel_base` transparent candidate: `312x335`.
- `panel_base` corner alpha after hole-fill extraction: `[0, 0, 0, 0]`.
- `panel_base` green decoration signal: `0.0004`.
- `panel_base` true red ribbon signal: `0.0`.
- `panel_base` gold-border signal: `0.1637`.

## Contract Checks

```json
{
  "panel_base_has_low_green_decor_signal": true,
  "panel_base_has_low_red_ribbon_signal": true,
  "panel_base_has_gold_border_signal": true,
  "title_plate_has_green_material_signal": true,
  "decor_flowers_cell_has_green_signal": true,
  "bottom_leaves_cell_has_green_signal": true,
  "inner_texture_has_low_green_signal": true,
  "manual_visual_check": {
    "panel_base_excludes_title_plate": "pass",
    "panel_base_excludes_flowers_and_leaves": "pass",
    "panel_top_title_plate_excludes_title_text": "pass",
    "separate_decoration_cells_present": "pass",
    "full_panel_composite_reference_contains_assembled_empty_panel": "pass"
  }
}
```

## Interpretation

This validates the narrow claim that a stronger prompt contract can improve asset-sheet layer ownership for the main panel:

```text
main_panel_bg composite cell -> split cells for panel_base, title_plate, flowers, leaves, inner_texture
```

It does **not** prove that the board directly exports production-ready sprites. These assets are still extracted from a rendered production board, and exact engine placement, nine-slice boundaries, and soft alpha need a production pass.

## Files

- `production_board.png`: generated split-contract board.
- `bbox_overlay.png`: board with audited asset-cell boxes.
- `asset_cells/*.png`: source cell crops for audit.
- `assets_png/*.png`: transparent candidates extracted from the source cells.
- `sprite_overview.png`: transparent candidate overview.
- `focused_split_comparison.png`: cell-to-transparent-candidate comparison.
- `rough_panel_reconstruction_vs_reference.png`: rough assembly sanity check, not final layout proof.
- `probe_metrics.json`: machine-readable metrics.
- `sprite_manifest.json`, `layer_ir.json`, `layout_ir.json`: focused validation metadata.

## Verdict

```text
panel split contract: pass for layer-ownership direction
panel_base as clean production sprite: not yet; candidate only
next validation: repeat with stricter transparent/native per-asset generation or product_card parent-child split
```
