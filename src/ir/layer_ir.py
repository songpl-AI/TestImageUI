from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.core.types import LayerIR, LayerItem


def load_layer_ir(path: Path) -> LayerIR:
    with path.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = json.load(f)

    canvas = raw.get("canvas") or {}
    layers = [LayerItem.from_json(item) for item in raw.get("layers", [])]
    return LayerIR(
        version=str(raw.get("version", "0.1")),
        canvas_width=int(canvas["width"]),
        canvas_height=int(canvas["height"]),
        source_image=str(raw.get("source_image", "")),
        layers=layers,
    )


def validate_layer_ir(layer_ir: LayerIR, image_size: tuple[int, int]) -> list[str]:
    errors: list[str] = []
    image_width, image_height = image_size

    if (layer_ir.canvas_width, layer_ir.canvas_height) != image_size:
        errors.append(
            "canvas size does not match source image: "
            f"ir={layer_ir.canvas_width}x{layer_ir.canvas_height}, "
            f"image={image_width}x{image_height}"
        )

    seen_ids: set[str] = set()
    for layer in layer_ir.layers:
        if not layer.id:
            errors.append("layer id cannot be empty")
        if layer.id in seen_ids:
            errors.append(f"duplicate layer id: {layer.id}")
        seen_ids.add(layer.id)

        if layer.bbox.width <= 0 or layer.bbox.height <= 0:
            errors.append(f"{layer.id}: bbox width/height must be positive")
        if layer.bbox.x < 0 or layer.bbox.y < 0:
            errors.append(f"{layer.id}: bbox x/y cannot be negative")
        if layer.bbox.right > image_width or layer.bbox.bottom > image_height:
            errors.append(f"{layer.id}: bbox exceeds source image bounds")
        if layer.asset_strategy == "text_node" and not layer.text:
            errors.append(f"{layer.id}: text_node requires text")

    if not layer_ir.layers:
        errors.append("Layer IR must contain at least one layer")

    return errors


def layer_ir_to_json(layer_ir: LayerIR) -> dict[str, Any]:
    return {
        "version": layer_ir.version,
        "canvas": {
            "width": layer_ir.canvas_width,
            "height": layer_ir.canvas_height,
        },
        "source_image": layer_ir.source_image,
        "layers": [
            {
                "id": layer.id,
                "role": layer.role,
                "bbox": layer.bbox.as_list(),
                "asset_strategy": layer.asset_strategy,
                "transparent": layer.transparent,
                "text": layer.text,
                "remove_text": layer.remove_text,
                "remove_occluding_children": layer.remove_occluding_children,
                "nine_slice_candidate": layer.nine_slice_candidate,
                "children_hint": layer.children_hint,
                "metadata": layer.metadata,
            }
            for layer in layer_ir.layers
        ],
    }
