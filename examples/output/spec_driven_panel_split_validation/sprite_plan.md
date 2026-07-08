# Sprite Plan

Source image: `production_board.png` (`1536x1024`)
Scope: validate the main panel split contract from a production board. This is not a final production sprite export.

## Automatically Confirmed

| id | type | output | processing | reason |
|---|---|---|---|---|
| panel_base | panel_bg | assets_png/panel_base.png | source_preserving_validation_extract | Test whether base panel excludes sibling layers. |
| panel_top_title_plate | title_plate_bg | assets_png/panel_top_title_plate.png | source_preserving_validation_extract | Title plaque should be separate and text-free. |
| panel_corner_flowers | decoration | assets_png/panel_corner_flowers.png | source_preserving_validation_extract | Flower clusters should not be baked into panel_base. |
| panel_bottom_leaves | decoration | assets_png/panel_bottom_leaves.png | source_preserving_validation_extract | Bottom leaves should not be baked into panel_base. |
| panel_inner_texture | material_tile | assets_png/panel_inner_texture.png | source_preserving_validation_extract | Inner parchment material should be separate from border/decorations. |
| full_panel_composite_reference | visual_reference | assets_png/full_panel_composite_reference.png | reference_only | Useful audit reference, not a clean reusable base layer. |

## Needs Human Confirmation Before Production

| id | recommendation | why |
|---|---|---|
| panel_base | accept split direction, regenerate or manually refine for production | Current PNG is extracted from a rendered board cell, not a model-native transparent asset. |
| panel_top_title_plate | confirm whether title text remains Text Node or fixed art title | The plaque is text-free; actual title styling still needs product decision. |
| panel_corner_flowers / panel_bottom_leaves | confirm decoration ownership and reuse | Decorations are separate, but exact positions and reuse rules need Layer IR. |
| panel_inner_texture | confirm if material tile is needed | It may be useful for nine-slice/inpainting, but not required if panel_base is used as a whole nine-slice sprite. |
