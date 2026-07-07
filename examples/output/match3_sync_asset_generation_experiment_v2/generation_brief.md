# Generation Brief - Pastoral Match-3 Sync Asset Generation V2

## Goal

Generate a second pastoral match-3 production board to validate whether stricter layer-to-asset binding reduces asset variant mismatch.

The specific validation target is:

```text
full_effect top currency bars
  must match
asset_sheet top_currency_bar_bg + heart_icon + coin_icon + gem_icon + plus_button
```

## What Changed From V1

V1 had a usable `full_effect + asset_sheet` structure, but the `top_currency_bar_bg` asset did not match the full-effect currency bars:

- full_effect: dark brown capsule currency slots
- asset_sheet: cream rounded panel

V2 adds an explicit rule that every asset-sheet base layer must be the same art variant used in full_effect, with only dynamic text and child layers removed.

## Validation Components

Primary:

- `top_currency_bar_bg`
- `heart_icon`
- `plus_button`
- `heart_count_text`

Secondary:

- `play_button_bg`
- `play_button_text`

## Success Criteria

- The production board clearly has two sections: `full_effect` and `asset_sheet`.
- Asset sheet uses a fixed 4x4 grid with one isolated asset per cell.
- `top_currency_bar_bg` in the asset sheet is the same dark-brown capsule base art used by the full-effect currency bars, with no text, no icon, and no plus button.
- `play_button_bg` in the asset sheet is the same green primary button base used by the full-effect PLAY button, with no text.
- Dynamic text remains short and readable in the full-effect section.
- Asset sheet cells are isolated enough for local sprite extraction experiments.

## Known Risks

- The image model may still treat asset_sheet as a same-style asset catalog instead of a strict layer reference table.
- It may include labels, captions, or fake text in the sheet despite instructions.
- It may fail to preserve exact one-to-one variant identity for bars or buttons.
