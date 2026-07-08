# Panel Split No-Label Fixtures

These fixtures preserve the minimal inputs for the `grid_cell_foreground_safe_bbox`
regression test:

- `run_*/production_board.png`
- `run_*/layer_contract_fixed_bbox.json`
- `run_*/layer_contract_auto_detect.json`

They intentionally exclude generated validation outputs, contact sheets, and
reports. The test regenerates validation artifacts in a temporary directory and
asserts that fixed bboxes fail while grid-cell auto detection passes.
