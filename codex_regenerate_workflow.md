# Codex Regenerate Workflow

This MVP treats Codex image generation as the regenerate provider.

## 1. Prepare Tasks

```bash
python3 -m src.main \
  --input examples/input/shop_popup.png \
  --layer-ir examples/input/shop_popup.layer_ir.json \
  --output examples/output/shop_popup_codex \
  --mode prepare-regenerate
```

This writes:

- `assets_direct/`: direct crops for pixel reconstruction.
- `assets_regenerated/`: passthrough assets that do not need Codex generation.
- `regen_tasks/`: one folder per Codex image task.
- `regen_tasks_manifest.md`: task index for Codex or a human operator.
- `layout_ir.json`
- `report.md`

Each task folder contains:

- `reference_crop.png`
- `prompt.txt`
- `task.json`

## 2. Generate Assets With Codex

For each task in `regen_tasks_manifest.md`, generate a PNG from `reference_crop.png` and `prompt.txt`, then place it at the task's `target_asset` path.

Example target:

```text
examples/output/shop_popup_codex/assets_regenerated/buy_button_bg.png
```

Do not overwrite passthrough assets unless the Layer IR strategy changes.

## 3. Rebuild

After all target assets exist:

```bash
python3 -m src.main \
  --input examples/input/shop_popup.png \
  --layer-ir examples/input/shop_popup.layer_ir.json \
  --output examples/output/shop_popup_codex \
  --mode rebuild
```

This writes:

- `reconstruction_direct.png`
- `reconstruction_regenerated.png`
- `comparison.png`
- `layout_ir.json`
- `report.md`

## 4. Judge The Result

Use `comparison.png` to compare:

```text
Original effect image | Rebuild from direct crops | Rebuild from clean assets
```

Direct crops should prove pixel placement. Clean assets should prove whether the generated assets are reusable and close enough for engine reconstruction.
