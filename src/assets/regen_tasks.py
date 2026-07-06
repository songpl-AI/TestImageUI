from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image

from src.core.types import LayerIR, LayerItem


CODEX_IMAGE_STRATEGIES = {
    "regenerate",
    "regenerate_or_inpaint",
    "inpaint_background",
    "segmentation_extract",
}


def export_regenerate_tasks(
    source_image: Image.Image,
    layer_ir: LayerIR,
    output_dir: Path,
    *,
    source_image_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    tasks_dir = output_dir / "regen_tasks"
    assets_dir = output_dir / "assets_regenerated"
    tasks_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)

    tasks: list[dict[str, Any]] = []
    passthrough_assets: list[dict[str, Any]] = []
    for layer in layer_ir.layers:
        if layer.asset_strategy not in CODEX_IMAGE_STRATEGIES and layer.asset_strategy not in {"text_node", "ignore"}:
            target_asset = assets_dir / f"{layer.id}.png"
            crop = source_image.crop((layer.bbox.x, layer.bbox.y, layer.bbox.right, layer.bbox.bottom))
            crop.save(target_asset)
            passthrough_assets.append(
                {
                    "id": layer.id,
                    "role": layer.role,
                    "asset_strategy": layer.asset_strategy,
                    "target_asset": str(target_asset),
                }
            )
            continue

        if layer.asset_strategy not in CODEX_IMAGE_STRATEGIES:
            continue

        task_dir = tasks_dir / layer.id
        task_dir.mkdir(parents=True, exist_ok=True)

        reference_crop = task_dir / "reference_crop.png"
        crop = source_image.crop((layer.bbox.x, layer.bbox.y, layer.bbox.right, layer.bbox.bottom))
        crop.save(reference_crop)

        target_asset = assets_dir / f"{layer.id}.png"
        prompt = build_prompt(layer)
        prompt_path = task_dir / "prompt.txt"
        prompt_path.write_text(prompt + "\n", encoding="utf-8")

        task = {
            "id": layer.id,
            "role": layer.role,
            "asset_strategy": layer.asset_strategy,
            "bbox": layer.bbox.as_list(),
            "target_size": {
                "width": layer.bbox.width,
                "height": layer.bbox.height,
            },
            "transparent": layer.transparent,
            "remove_text": layer.remove_text,
            "remove_occluding_children": layer.remove_occluding_children,
            "source_image": str(source_image_path),
            "reference_crop": str(reference_crop),
            "prompt": str(prompt_path),
            "target_asset": str(target_asset),
        }
        (task_dir / "task.json").write_text(json.dumps(task, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tasks.append(task)

    _write_manifest(tasks, passthrough_assets, output_dir / "regen_tasks_manifest.md")
    return tasks, passthrough_assets


def build_prompt(layer: LayerItem) -> str:
    role = layer.role.lower()
    width = layer.bbox.width
    height = layer.bbox.height

    base = [
        f"Create a clean game UI asset for role `{layer.role}`.",
        f"Use the provided reference crop as the visual reference.",
        f"Output size must be exactly {width}x{height} pixels.",
        "Output should be a PNG asset suitable for a game engine.",
    ]

    if layer.transparent:
        base.append("Use a transparent background.")
    else:
        base.append("Use an opaque background matching the reference.")

    if layer.remove_text:
        base.append("Do not include any text, letters, numbers, or labels.")
    if layer.remove_occluding_children:
        base.append("Remove all child UI elements, icons, labels, buttons, and occluding objects.")

    if "button" in role:
        base.extend(
            [
                "Generate only the button background.",
                "Preserve the reference color, rounded shape, outline, highlight, and shadow style.",
                "Do not add icons or decorative elements.",
            ]
        )
    elif "panel" in role:
        base.extend(
            [
                "Generate only the clean panel background and border.",
                "Remove all internal content while preserving the frame style.",
                "Keep it usable as a nine-slice candidate.",
            ]
        )
    elif "card" in role:
        base.extend(
            [
                "Generate only the clean card background.",
                "Remove item icons, text, glow, and other foreground content.",
            ]
        )
    elif "glow" in role:
        base.extend(
            [
                "Generate only the glow or light effect.",
                "Use soft alpha edges and no solid background.",
                "Do not include icons, text, or panels.",
            ]
        )
    elif "icon" in role:
        base.extend(
            [
                "Generate or extract only the standalone icon object.",
                "Remove the surrounding UI background.",
                "Keep clean transparent edges and any natural object shadow.",
            ]
        )
    elif "art_text" in role:
        base.extend(
            [
                f"Generate the fixed art title text `{layer.text or ''}` as a transparent PNG.",
                "Preserve the reference style, fill color, outline, and game UI feel.",
                "This is fixed title art, not editable engine text.",
            ]
        )
    elif "title" in role:
        base.extend(
            [
                "Generate only the clean title board or title plate.",
                "Do not include title text unless the role explicitly asks for art text.",
            ]
        )
    else:
        base.append("Preserve the reference visual style while removing unrelated surrounding content.")

    return "\n".join(f"- {line}" for line in base)


def _write_manifest(tasks: list[dict[str, Any]], passthrough_assets: list[dict[str, Any]], output_path: Path) -> None:
    lines = [
        "# Codex Regenerate Tasks",
        "",
        "Generate each target asset from its reference crop and prompt, then place the PNG at `target_asset`.",
        "After all target assets exist, run the pipeline in `rebuild` mode.",
        "",
        "## Tasks",
    ]

    if not tasks:
        lines.append("- No Codex image tasks are required.")
    else:
        for task in tasks:
            lines.extend(
                [
                    f"### {task['id']}",
                    f"- Role: `{task['role']}`",
                    f"- Strategy: `{task['asset_strategy']}`",
                    f"- Size: `{task['target_size']['width']}x{task['target_size']['height']}`",
                    f"- Reference: `{task['reference_crop']}`",
                    f"- Prompt: `{task['prompt']}`",
                    f"- Target: `{task['target_asset']}`",
                    "",
                ]
            )

    lines.extend(["", "## Passthrough Assets"])
    if not passthrough_assets:
        lines.append("- None")
    else:
        for asset in passthrough_assets:
            lines.append(
                f"- `{asset['id']}` ({asset['role']}, {asset['asset_strategy']}): `{asset['target_asset']}`"
            )

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
