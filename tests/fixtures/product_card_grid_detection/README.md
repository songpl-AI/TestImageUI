# Product Card Grid Detection Fixture

This fixture preserves the minimal input that caught an edge-guard regression for
compact horizontal controls:

- `run_02/production_board.png`
- `run_02/layer_contract_auto_detect.json`

The test rewrites the contract to `grid_cell_foreground_safe_bbox` in a temporary
directory and verifies that `price_tag_bg` stays tightly detected instead of
expanding to the full coarse asset-sheet cell height.
