# Spec-Driven UI Generation Workflow

This experiment validates a spec-first route for generating a full UI mockup and its reusable sprite plan from the same contract.

```text
natural-language brief
  -> ui_spec.json
  -> full_effect_prompt.txt
  -> production_board_prompt.txt
  -> sprite_manifest.json + asset_prompts/
  -> layer_ir.json + layout_ir.json
```

## Why This Exists

The full effect image and standalone sprites should not independently decide size, position, or layer order. The JSON spec is the source of truth. Generated images are visual candidates that must be fitted back into the IR and checked through reconstruction.

## Current MVP

Run:

```bash
python3 -m src.main \
  --mode plan-spec \
  --brief examples/input/spec_driven_shop_request.json \
  --output examples/output/spec_driven_shop_plan
```

The command writes:

- `ui_spec.json`: the full contract with canvas, style, layers, bbox, z-order, asset ids, text nodes, prompts, and scale modes.
- `full_effect_prompt.txt`: prompt for generating the whole UI effect image.
- `production_board_prompt.txt`: prompt for generating a combined full-effect and asset-sheet board.
- `sprite_manifest.json`: reusable source sprite list plus the fitted layout instances that reference each asset.
- `asset_prompts/`: one prompt per reusable sprite.
- `layer_ir.json`: compatible Layer IR for the existing pipeline.
- `layout_ir.json`: Layout IR that references `assets_fit_raw`.
- `sprite_plan.md`: human-readable plan with automatic assumptions and confirmation items.
- `spec_validation_report.md`: contract checks and known risks.

## Validation Boundary

This validates the artifact graph and spec contract, not final visual quality. The next meaningful test is to generate one production board or a small subset of representative assets, fit them into `assets_fit_raw`, and compare reconstruction against the generated full effect.

Known risks carried into this workflow:

- A generated asset sheet can still produce a different visual variant from the full effect.
- Image models do not strictly obey bbox coordinates.
- Natural sprite dimensions must not be treated as engineering dimensions.
- Stretchable backgrounds need explicit `scale_mode` and later nine-slice metadata.
- Dynamic text stays as Text Node; only fixed title art may be generated as image text.

