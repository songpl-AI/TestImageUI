# Strict Asset / Layer Plan -> Full Effect + Asset Sheet Template

Use this prompt structure when the goal is not only a pretty UI mockup, but a source image that can later be converted into Sprite Plan, Layer IR, Layout IR, and standalone sprites.

## Template

```text
Use case: ui-mockup
Asset type: game UI production board for a sprite split pipeline
Primary request: Generate a <portrait|landscape> <game type> <screen type> production board.

Canvas:
- <target canvas>, no device frame, no watermark
- Board sections:
  1. full_effect: complete playable-looking UI mockup
  2. asset_sheet: fixed grid of isolated reusable assets

Asset / Layer Plan:
- Stable asset ids must be represented visually and consistently:
  - <asset_id_01>: <role, e.g. panel_bg>
  - <asset_id_02>: <role, e.g. button_bg>
  - <asset_id_03>: <role, e.g. icon>
- Layer-to-asset binding:
  - Every full_effect layer that has a matching asset_sheet id must use the same base art variant.
  - The asset_sheet cell must be the reusable base layer from full_effect, with dynamic text and child elements removed.
  - Keep the same silhouette, color family, material, border thickness, corner style, lighting, and decoration ownership.
  - Do not invent a different but same-style replacement asset for the asset_sheet.
- Scale metadata:
  - Mark each background/panel/button/bar asset as <contain|stretch|nine_slice_expected>.
  - For nine-slice candidates, keep corners and decorative end caps visually separable from the stretchable center.
- Text Nodes:
  - <text_node_id>: exact text "<TEXT>", not baked into asset sheet backgrounds
- Visual-state exceptions:
  - <visual_state_id>: allowed to bake state only if explicitly listed

full_effect requirements:
- Use the planned assets in their intended roles.
- Keep UI hierarchy clear and orthographic.
- Dynamic text should be short, legible, and replaceable.
- Do not fuse UI edges into the background.

asset_sheet requirements:
- Fixed <rows>x<cols> grid with equal cells.
- One asset per cell, centered, with padding.
- Items must be the same art variant as the matching full_effect layer, not merely the same style family.
- No scene background inside cells.
- No dynamic text baked into reusable assets.
- No overlaps between cells.
- Use a flat neutral or chroma-key-like background.

Style:
- <game art direction>
- consistent material, outline thickness, lighting direction, and polish level

Avoid:
- garbled text, extra labels, excessive tiny text
- UI elements fused into the background
- shadows crossing cell boundaries
- cropped key elements
- brand logos, watermark, device frame
```

## Why This Exists

The previous post-hoc workflow tries to recover layers from one flattened effect image. This template moves the constraint earlier: the model is asked to produce a full UI and an asset family from the same plan, so later reconstruction is a fit/alignment problem rather than hidden-layer recovery.
