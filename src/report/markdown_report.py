from __future__ import annotations

from collections import Counter
from pathlib import Path

from src.core.types import LayerIR, LayerItem


def build_report(layer_ir: LayerIR, output_path: Path) -> Path:
    strategy_counts = Counter(layer.asset_strategy for layer in layer_ir.layers)
    text_nodes = [layer for layer in layer_ir.layers if layer.asset_strategy == "text_node"]
    nine_slice = [layer for layer in layer_ir.layers if layer.nine_slice_candidate]
    risks = _risk_items(layer_ir)

    lines: list[str] = [
        "# UI Split Report",
        "",
        "## Summary",
        f"- Layers: {len(layer_ir.layers)}",
        f"- Image assets: {sum(1 for layer in layer_ir.layers if layer.asset_strategy != 'text_node' and layer.asset_strategy != 'ignore')}",
        f"- Text nodes: {len(text_nodes)}",
        f"- Nine-slice candidates: {len(nine_slice)}",
        f"- Risk items: {len(risks)}",
        "",
        "## Strategy Counts",
    ]

    for strategy, count in sorted(strategy_counts.items()):
        lines.append(f"- {strategy}: {count}")

    lines.extend(["", "## Text Nodes"])
    if text_nodes:
        for layer in text_nodes:
            lines.append(f"- `{layer.id}`: {layer.text}")
    else:
        lines.append("- None")

    lines.extend(["", "## Nine-Slice Candidates"])
    if nine_slice:
        for layer in nine_slice:
            lines.append(f"- `{layer.id}` ({layer.role})")
    else:
        lines.append("- None")

    lines.extend(["", "## Risk Items"])
    if risks:
        lines.extend(
            [
                "| id | role | issue | suggestion |",
                "|---|---|---|---|",
            ]
        )
        for layer, issue, suggestion in risks:
            lines.append(f"| `{layer.id}` | {layer.role} | {issue} | {suggestion} |")
    else:
        lines.append("- None")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return output_path


def _risk_items(layer_ir: LayerIR) -> list[tuple[LayerItem, str, str]]:
    risks: list[tuple[LayerItem, str, str]] = []
    for layer in layer_ir.layers:
        role = layer.role.lower()
        strategy = layer.asset_strategy

        if "button" in role and "background" in role and strategy == "direct_crop":
            risks.append((layer, "direct crop may contain label text", "use regenerate or inpaint_background"))
        if "panel" in role and strategy == "direct_crop":
            risks.append((layer, "panel direct crop may contain child occlusions", "use regenerate_or_inpaint"))
        if "dynamic_text" in role and strategy != "text_node":
            risks.append((layer, "dynamic text should not become a static PNG", "use text_node"))
        if "glow" in role and strategy == "direct_crop":
            risks.append((layer, "glow alpha is difficult to recover from a crop", "use regenerate"))
        if layer.remove_text and strategy == "direct_crop":
            risks.append((layer, "layer asks to remove text but uses direct crop", "use regenerate or inpaint_background"))
        if layer.remove_occluding_children and strategy == "direct_crop":
            risks.append((layer, "layer asks to remove occluding children but uses direct crop", "use regenerate_or_inpaint"))

    return risks
