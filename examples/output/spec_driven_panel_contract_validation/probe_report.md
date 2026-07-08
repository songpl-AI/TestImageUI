# spec_driven_panel_split_contract Contract Validation

## Result

`spec_driven_panel_split_contract` validation result: **pass**.

## Evidence

- Board size: `1536x1024`.
- Asset cells: `6`.
- Primary asset: `panel_base`.
- Primary source cell: `358x365`.
- Primary transparent candidate: `312x335`.
- Primary corner alpha: `[0, 0, 0, 0]`.
- Validation errors: `0`.
- Failed checks: `0`.

## Contract Checks

```json
{
  "panel_base_has_low_green_decor_signal": {
    "asset_id": "panel_base",
    "metric": "green_ratio",
    "op": "<=",
    "value": 0.02,
    "actual": 0.0004,
    "pass": true
  },
  "panel_base_has_low_red_ribbon_signal": {
    "asset_id": "panel_base",
    "metric": "red_ratio_hsv",
    "op": "<=",
    "value": 0.01,
    "actual": 0.0,
    "pass": true
  },
  "panel_base_has_gold_border_signal": {
    "asset_id": "panel_base",
    "metric": "gold_ratio",
    "op": ">=",
    "value": 0.08,
    "actual": 0.1637,
    "pass": true
  },
  "title_plate_has_green_material_signal": {
    "asset_id": "panel_top_title_plate",
    "metric": "green_ratio",
    "op": ">=",
    "value": 0.35,
    "actual": 0.6728,
    "pass": true
  },
  "bottom_leaves_cell_has_green_signal": {
    "asset_id": "panel_bottom_leaves",
    "metric": "green_ratio",
    "op": ">=",
    "value": 0.45,
    "actual": 0.7543,
    "pass": true
  },
  "panel_base_has_clean_corners": {
    "asset_id": "panel_base",
    "metric": "corner_alpha_max",
    "op": "==",
    "value": 0.0,
    "actual": 0.0,
    "pass": true
  },
  "manual_visual_check": {
    "panel_base_excludes_title_plate": {
      "status": "pass",
      "description": "The panel base cell contains no green title plate."
    },
    "panel_base_excludes_flowers_and_leaves": {
      "status": "pass",
      "description": "The panel base cell contains no flower or leaf decorations."
    },
    "separate_decoration_cells_present": {
      "status": "pass",
      "description": "Flower and leaf decorations are present as separate cells."
    }
  }
}
```

## Interpretation

This validates whether explicit decoration ownership can prevent the main panel base from baking in title plate and floral layers.

## Files

- `layer_contract.json`: copied input contract.
- `production_board.png`: copied source board.
- `bbox_overlay.png`: board with asset-cell boxes.
- `asset_cells/*.png`: source cell crops for audit.
- `assets_png/*.png`: transparent candidates extracted from source cells.
- `assets_fit_raw/*.png`: rough layout instances when rough reconstruction is configured.
- `sprite_overview.png`: transparent candidate overview.
- `focused_split_comparison.png`: cell-to-transparent-candidate comparison.
- `rough_reconstruction.png`: rough reconstruction when configured.
- `rough_reconstruction_comparison.png`: source / reconstruction / reference comparison when configured.
- `probe_metrics.json`: machine-readable metrics.
- `sprite_manifest.json`, `layer_ir.json`, `layout_ir.json`: validation metadata.

## Verdict

```text
panel split contract: pass when all configured checks pass
```
