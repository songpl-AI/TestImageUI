from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from src.core.types import LayerIR, LayerItem


def build_layout_ir(layer_ir: LayerIR, asset_base: str = "assets_regenerated") -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    for layer in layer_ir.layers:
        if layer.asset_strategy == "ignore":
            continue

        node: dict[str, Any] = {
            "id": layer.id,
            "type": _node_type(layer),
            "role": layer.role,
            "rect": layer.bbox.as_list(),
            "anchor": "top_left",
        }
        if layer.asset_strategy == "text_node":
            node["text"] = layer.text
        else:
            node["asset"] = f"{asset_base}/{layer.id}.png"

        if layer.nine_slice_candidate:
            node["nine_slice_candidate"] = True
        if layer.children_hint:
            node["children_hint"] = layer.children_hint

        nodes.append(node)

    return {
        "version": layer_ir.version,
        "screen": {
            "name": Path(layer_ir.source_image).stem or "GeneratedUIScreen",
            "canvas": {
                "width": layer_ir.canvas_width,
                "height": layer_ir.canvas_height,
            },
            "nodes": nodes,
        },
    }


def save_layout_ir(layout_ir: dict[str, Any], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(layout_ir, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return output_path


def _node_type(layer: LayerItem) -> str:
    role = layer.role.lower()
    if layer.asset_strategy == "text_node":
        return "Text"
    if "button" in role:
        return "Button"
    if "panel" in role:
        return "Panel"
    if "glow" in role or "decoration" in role:
        return "Decoration"
    if "label" in role and not layer.output:
        return "Text"
    return "Image"
