---
name: ui-sprite-regenerator
description: Generate clean standalone game UI sprite assets from AI-generated UI mockups or effect images. Use when the user asks to split, extract, regenerate, create sprites, 切图, 单图, 贴图, UI 素材, or engine-ready PNG assets from a composed UI image; especially when they want each UI element as its own reusable transparent PNG rather than rectangular crops of the source image.
---

# UI Sprite Regenerator

## Core Rule

Do not treat rectangular crops as final sprites.

A valid output sprite is an independent UI asset: clean, reusable, usually transparent, and containing only the intended element. Examples:

- clean panel background without child elements
- title board without title text
- fixed title art as its own image
- button background without label text
- reward icon without card background
- progress bar background without numbers
- currency bar without icon, plus button, or number

Rectangular crops are allowed only as references, bbox/debug artifacts, or reconstruction checks.

## Workflow

1. Inspect the source UI image.
2. Identify semantic elements, not crop rectangles:
   - background
   - main panel
   - title board
   - fixed art title
   - cards and badges
   - buttons
   - icons
   - progress bars
   - decorative ornaments
   - dynamic text nodes
3. For each element, decide:
   - `standalone_sprite`: generate a clean independent PNG
   - `fixed_art_text`: generate as an image, preserving exact wording
   - `dynamic_text`: do not generate a PNG; keep as engine text
   - `passthrough`: only acceptable for already-isolated simple buttons/icons when the user allows it
4. Use the source image as a visual reference. Ask image generation to create each standalone sprite separately.
5. For transparent output with the built-in image tool, generate on a flat chroma-key background and remove it locally.
6. Save generated source images and final transparent PNGs separately.
7. Create an overview sheet on a checkerboard background so the user can verify these are independent sprites.
8. If a layout IR exists, also create fitted versions inside target-size transparent canvases for later reconstruction.

## What To Generate

Prefer these outputs for a composed game UI:

- `main_panel.png`
- `title_board.png`
- `title_logo.png` for fixed art title
- `subtitle_ribbon.png`
- `reward_card_bg.png`
- `reward_icon.png`
- `button_bg.png`
- `progress_bar_bg.png`
- `badge_bg.png`
- `currency_bar_bg.png`
- `currency_icon.png`
- `close_button.png`
- `plus_button.png`
- `decoration_*.png`

Use descriptive names from the UI role, not crop coordinates.

## Prompt Pattern

Use prompts like:

```text
Generate a clean standalone <element> sprite inspired by the provided UI mockup.
Subject: <exact element only>.
Style: match the source image's game UI style, colors, trim, lighting, and polish.
Composition: centered single asset only, generous padding.
Constraints: no unrelated UI elements, no background scene, no watermark.
If this is a background asset: no text, no letters, no numbers, no child elements.
If this is fixed title art: include exactly "<text>" and no extra words.
Create on a perfectly flat solid #00ff00 chroma-key background for background removal. The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation. Do not use #00ff00 anywhere in the subject.
```

For green/teal subjects, use a different key such as `#ff00ff`.

## Transparency

When using the built-in image generation tool:

1. Generate with a flat chroma-key background.
2. Copy the generated source into a project folder such as `generated_src/`.
3. Remove the key color:

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/.system/imagegen/scripts/remove_chroma_key.py" \
  --input <generated_chroma.png> \
  --out <asset.png> \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

4. Verify the final image is `RGBA` and has transparent corners.

## Output Structure

Use this structure unless the project already has a stronger convention:

```text
output/<screen>_single_sprites/
  generated_src/
    <id>_chroma.png
  assets_png/
    <id>.png
  assets_fit_raw/
    <id>.png
  sprite_overview.png
```

- `generated_src/`: original generated images, often chroma-keyed.
- `assets_png/`: final standalone transparent sprites.
- `assets_fit_raw/`: optional sprites scaled into transparent canvases matching IR target rects.
- `sprite_overview.png`: checkerboard preview sheet.

## Validation

Before reporting success:

- Confirm assets are generated/regenerated, not merely rectangular crops.
- Confirm background/label/button assets do not contain dynamic text.
- Confirm dynamic text is listed separately as text nodes.
- Confirm each final asset is PNG with alpha where expected.
- Show or create a checkerboard overview image.
- Mention any assets that are still crop-based or need another generation pass.

## Failure Modes

If the result is a rectangular piece of the source image with neighboring pixels, text, occlusions, or background baked in, call it a reference crop, not a sprite.

If the user asks for “每一张单图”, “sprite 贴图”, “工程切图”, or “可复用素材”, default to standalone regeneration. Do not stop after bbox crop extraction.
