# Pastoral Match-3 Sync Asset Generation Experiment

This experiment upgrades the previous production-board prompt into a stricter:

```text
Asset / Layer Plan
  -> full_effect
  -> fixed-grid asset_sheet
```

The generated image is:

- `pastoral_match3_production_board.png`

## Result Summary

This round is a positive result for the synchronized-generation direction.

Compared with the previous SLG prompt, the stricter prompt produced a much more usable production board:

- The top `FULL_EFFECT` section is a complete vertical match-3 home UI.
- The bottom `ASSET_SHEET` section follows a clear 4x4 grid.
- Most asset cells contain one isolated asset with padding.
- Dynamic text such as `PLAY`, `128`, `12,450`, and `320` appears only in the full UI area.
- Reusable asset cells do not contain fake labels or asset id captions.
- The pastoral style is consistent across the full UI and asset sheet.

## What Worked

- **Stable board structure**: the image clearly separates full UI and asset sheet.
- **Fixed grid compliance**: the bottom asset sheet uses 4 rows x 4 columns with cell boundaries.
- **Text separation**: asset sheet backgrounds avoid baked dynamic text.
- **Style family consistency**: rounded wood, cream panels, green leaves, fruit accents, and honey-gold highlights are consistent.
- **Useful planned assets**: icons, buttons, panels, level nodes, avatar frame, and nav icons are easy to identify.

## Still Imperfect

- `top_currency_bar_bg` in the asset sheet is closer to a cream panel than the brown currency bars used in the full UI.
- The asset sheet follows the requested order mostly, but exact role fidelity still needs manual review.
- The asset sheet is part of the same bitmap, not individual transparent PNGs yet.
- The full UI and asset sheet are still generated siblings, not guaranteed exact PSD layers.
- Text accuracy is acceptable in this result, but image models can still drift on future runs.

## Practical Conclusion

The stricter `Asset / Layer Plan -> full_effect + asset_sheet` prompt is worth continuing.

The next iteration should:

1. Split this production board into `full_effect` and `asset_sheet` regions.
2. Create a Sprite Plan from the 4x4 asset sheet.
3. Extract or regenerate a few asset cells as transparent sprites.
4. Reconstruct one small UI section, such as the `PLAY` button or top currency bar.
5. Tighten prompts for assets whose sheet version does not match the full UI version.

## Probe Results

### `play_button_probe`

The `PLAY` button proved that the asset sheet can provide a useful standalone background, but wide UI backgrounds need explicit fit metadata.

- `contain` made the button background too short.
- `stretch` was closer.
- `nine_slice` is the likely correct production representation.
- Full-effect flower decorations were not represented in the asset cell, so decoration ownership must be explicit.

### `currency_bar_probe`

The heart currency bar exposed a different issue: the asset variant can be wrong even when the grid structure is correct.

- Full effect uses a dark brown capsule resource slot.
- Asset sheet provides a cream rounded panel for `top_currency_bar_bg`.
- `contain` delta: `66.34`.
- `stretch` delta: `67.39`.
- The issue is asset identity, not only scale mode.

This means the next prompt version should require the asset sheet to contain the exact reusable base layer used in the full effect, with only dynamic text and child elements removed.

## Files

- `strict_asset_layer_plan_template.md`: reusable strict prompt template.
- `asset_layer_plan.md`: this match-3 screen's planned assets and text nodes.
- `strict_match3_prompt.txt`: exact prompt used for generation.
- `pastoral_match3_production_board.png`: generated result copied into the workspace.
- `play_button_probe/`: first focused reconstruction probe.
- `currency_bar_probe/`: second focused reconstruction probe.
