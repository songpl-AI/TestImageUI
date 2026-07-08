# Currency Bar Grid Detection Fixture

This fixture preserves the minimal input for validating `currency_bar_bg` as a
formal Layer Contract case:

- `production_board.png`
- `layer_contract_grid_detect.json`

The contract checks that the currency bar background remains text-free and
icon-free, keeps dynamic amount text as a Text Node, and uses
`grid_cell_foreground_safe_bbox` to avoid expanding the compact horizontal bar
back to the full asset-sheet cell.
