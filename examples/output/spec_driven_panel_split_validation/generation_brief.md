# Panel Split Validation Brief

## Goal

Validate whether a stronger natural-language + JSON-style layer contract can make a generated production board separate the main shop panel into engineering-oriented layers instead of baking decorations into `main_panel_bg`.

## Hypothesis

If the prompt explicitly declares layer ownership, sibling exclusions, and asset-sheet equivalence to the full-effect layers, then the model may produce separate asset cells for:

- `panel_base`
- `panel_top_title_plate`
- `panel_corner_flowers`
- `panel_bottom_leaves`
- `panel_inner_texture`

## Hard Acceptance Checks

- `panel_base` contains only the cream rounded panel body and gold border.
- `panel_base` does not contain the green top title plate.
- `panel_base` does not contain flowers, leaves, ribbon, product cards, buttons, icon, text, or shadows from other layers.
- `panel_top_title_plate` is separated and contains no title text.
- `panel_corner_flowers` and `panel_bottom_leaves` are separated decoration layers, not baked into `panel_base`.
- Dynamic text remains in the full UI only and is not required in asset cells.

## Failure Signals

- The `panel_base` cell includes the title plate.
- The `panel_base` cell includes flowers or bottom leaves.
- The right-side asset cells are just a pretty style sheet rather than layer-equivalent assets.
- The full UI follows one panel design, but asset cells show different variants.
