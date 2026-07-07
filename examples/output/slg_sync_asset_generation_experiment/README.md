# SLG Sync Effect + Asset Generation Experiment

This experiment tests the proposed direction:

```text
Asset / Layer Plan
  -> synchronized full effect image
  -> synchronized asset family / standalone assets
  -> local chroma cleanup
  -> Layer IR fit
  -> reconstruction check
```

## Key Outputs

- `generated_src/production_board.png`: generated production board with full HUD and asset family sheet.
- `generated_src/full_hud.png`: generated full SLG HUD used as this round's source.
- `generated_src/*_chroma.png`: generated standalone assets on magenta chroma.
- `assets_png/`: local chroma-key cleaned standalone assets.
- `assets_fit_raw/`: assets fitted into the BUILD button source crop layout.
- `focused_build_button_sync_comparison.png`: source crop vs synchronized assets reconstruction.
- `sprite_overview.png`: generated standalone asset overview.
- `experiment_manifest.json`: selected bboxes, natural asset sizes, and rough metrics.
- `sprite_plan.md`: Sprite Plan for this small validation.
- `layer_ir.json` / `layout_ir.json`: minimal IR for the BUILD button reconstruction.

## What Worked

- The generated standalone assets are visually from the same family as the full HUD.
- `bottom_nav_button_bg`, `build_hammer_icon`, and `red_badge_dot` are clean independent assets after chroma removal.
- The BUILD button can be reconstructed from generated assets + Text Node without relying on source crop pixels.
- This is a better starting point than trying to infer hidden button layers from a flat screenshot.

## What Did Not Fully Work Yet

- The full HUD and standalone assets are still generated variants, not exact PSD siblings.
- Text Node style does not automatically match the generated full HUD text.
- Fit bbox and icon scale still need tuning.
- Shadow ownership remains ambiguous.
- RGB delta is not a fair sole metric for this first round because source crop background and generated transparent reconstruction differ structurally.

## Current Judgment

Promising, but not solved.

The route should continue with stricter generation constraints:

1. Emit a machine-readable Asset / Layer Plan before image generation.
2. Generate a full effect image and asset sheet that explicitly reuse the same asset ids.
3. Use a strict asset sheet grid with chroma-key background and no overlap.
4. Validate a few representative components, not only BUILD.
5. Separate `visual_state_sprite` and `engineering_sprite` outputs.

This branch is the first proof that "generate assets together with the effect image" is more plausible than post-hoc recovery from one flattened UI image.
