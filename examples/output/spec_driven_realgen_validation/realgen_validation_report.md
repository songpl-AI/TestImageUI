# Spec-Driven Real Generation Validation

## Scope

This is a real image-generation test for the spec-driven route:

```text
ui_spec / prompt contract
  -> one generated production board
  -> full_effect region + asset_sheet region
  -> 8 component audit crops
```

The generated crops are evidence for visual auditing. They are not final engine-ready transparent sprites.

## Artifacts

- `production_board.png`: generated production board copied from the built-in image generation output.
- `production_board_split_overlay.png`: coarse full-effect / asset-sheet split guide.
- `full_effect_region.png`: left-side full UI region.
- `asset_sheet_region.png`: right-side asset sheet region.
- `component_variant_comparison.png`: side-by-side audit for 8 representative components.
- `asset_cells/*.png`: cropped asset-sheet cells for audit only.
- `full_crops/*.png`: matching full-effect component crops for audit only.
- `production_board_prompt_used.txt`: exact prompt used for this generation.

## Result

The production-board approach is useful for style synchronization, but it is not sufficient by itself to produce final engineering sprites.

Passed or mostly passed:

- The generated board produced a coherent full UI and a matching asset sheet in one image.
- Buy button, currency bar, discount badge, price tag, coin icon, and close button are broadly the same visual family as their full-effect counterparts.
- Asset-sheet cells mostly removed dynamic text and child content for the tested components.
- The right-side cells are large enough to serve as reference material for the next extraction or regeneration step.

Partial or failed:

- The board did not preserve the requested exact full-effect data. For example, the currency became `1,250` instead of the spec value `3200`, prices and discounts also drifted.
- The output canvas is `1536x1024`; the left full UI is a composed region, not a true `720x1280` engineering canvas.
- `main_panel_bg` is not a clean base panel. The asset cell includes a top title plaque and floral/leaf decoration that should probably be separate layers.
- `product_card_bg` is close in style, but its full-effect counterpart includes foreground item and text layers, so it still needs a clean extraction/regeneration path before reconstruction.
- Asset cells are RGB crops with light backgrounds and shadows, not transparent PNG sprites.

## Interpretation

This validates the central hypothesis only partially:

```text
One prompt can produce a visually coherent full UI plus matching asset candidates.
```

It does not validate the stronger production claim:

```text
One prompt can directly produce final, correctly layered, transparent engine sprites.
```

The next production-safe step is to treat the generated asset cells as a style/material sheet, then run a separate extraction or per-asset generation step that enforces:

- transparent output,
- no dynamic text,
- explicit decoration ownership,
- `scale_mode` / nine-slice metadata,
- reconstruction against the generated full-effect region.

## Component Verdicts

| component | verdict | note |
|---|---|---|
| `main_panel_bg` | partial | Same family, but merged title board and floral decorations into the base panel. |
| `product_card_bg` | partial | Same family, but needs clean no-child version before reconstruction. |
| `buy_button_bg` | pass | Strong same-family match; still needs text-free transparent extraction. |
| `currency_bar_bg` | pass | Strong same-family match; exact text/number belongs to Text Node. |
| `discount_badge_bg` | pass | Good text-free badge candidate. |
| `price_tag_bg` | pass | Good text-free price tag candidate. |
| `coin_icon` | pass | Good same-family icon candidate. |
| `close_button` | pass | Good same-family close button candidate. |

