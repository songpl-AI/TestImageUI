from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from src.core.types import LayerIR, LayerItem


def reconstruct(
    layer_ir: LayerIR,
    assets_dir: Path,
    output_path: Path,
    *,
    draw_text: bool,
) -> Path:
    canvas = Image.new("RGBA", (layer_ir.canvas_width, layer_ir.canvas_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    for layer in layer_ir.layers:
        if layer.asset_strategy == "ignore":
            continue

        asset_path = assets_dir / f"{layer.id}.png"
        if asset_path.exists():
            asset = Image.open(asset_path).convert("RGBA")
            canvas.alpha_composite(asset, (layer.bbox.x, layer.bbox.y))
        elif draw_text and layer.asset_strategy == "text_node":
            _draw_text_node(draw, layer)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path)
    return output_path


def build_comparison(original_path: Path, direct_path: Path, regenerated_path: Path, output_path: Path) -> Path:
    original = Image.open(original_path).convert("RGB")
    direct = Image.open(direct_path).convert("RGB")
    regenerated = Image.open(regenerated_path).convert("RGB")
    width, height = original.size
    header_height = 54

    comparison = Image.new("RGB", (width * 3, height + header_height), (0, 0, 0))
    labels = ["Original effect image", "Rebuild from direct crops", "Rebuild from clean assets"]
    font = _load_font(30, bold=True)
    draw = ImageDraw.Draw(comparison)

    for index, (label, image) in enumerate(zip(labels, [original, direct, regenerated], strict=True)):
        x = index * width
        comparison.paste(image, (x, header_height))
        draw.text((x + 20, 12), label, fill=(255, 255, 255), font=font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    comparison.save(output_path)
    return output_path


def _draw_text_node(draw: ImageDraw.ImageDraw, layer: LayerItem) -> None:
    text = layer.text or ""
    role = layer.role.lower()
    font_size = max(18, min(layer.bbox.height - 8, 46))
    font = _load_font(font_size, bold=True)

    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=2)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = layer.bbox.x + max(0, (layer.bbox.width - text_width) // 2)
    y = layer.bbox.y + max(0, (layer.bbox.height - text_height) // 2) - 4

    if "button" in role:
        fill = (255, 255, 255)
        stroke = (20, 103, 53)
    elif "reward_count" in layer.id:
        fill = (255, 255, 255)
        stroke = (83, 45, 132)
    elif "coin_amount" in layer.id:
        fill = (255, 255, 255)
        stroke = (55, 93, 158)
    elif "price" in layer.id or "dynamic" in role:
        fill = (132, 76, 38)
        stroke = None
    else:
        fill = (255, 255, 255)
        stroke = (78, 45, 117)

    draw.text((x, y), text, fill=fill, font=font, stroke_width=2 if stroke else 0, stroke_fill=stroke)


def _load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()
