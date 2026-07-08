from __future__ import annotations

import json
import math
import operator
import shutil
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from src.ir.layer_ir import load_layer_ir, validate_layer_ir


@dataclass(frozen=True)
class LayerContractResult:
    output_dir: Path
    contract_path: Path
    board_path: Path
    copied_board_path: Path
    layer_ir_path: Path
    layout_ir_path: Path
    sprite_manifest_path: Path
    probe_metrics_path: Path
    probe_report_path: Path
    asset_count: int
    validation_errors: list[str]
    failed_checks: list[str]


def export_layer_contract_validation(contract_path: Path, output_dir: Path) -> LayerContractResult:
    contract = _load_json(contract_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    contract_base = contract_path.parent
    board_path = _resolve_path(str(contract.get("board_image", "")), contract_base)
    if not board_path.exists():
        raise FileNotFoundError(f"board_image does not exist: {board_path}")

    board = Image.open(board_path).convert("RGB")
    board_size = board.size
    expected_canvas = contract.get("canvas") or {}
    if expected_canvas:
        expected_size = (int(expected_canvas["width"]), int(expected_canvas["height"]))
        if expected_size != board_size:
            raise ValueError(f"contract canvas {expected_size} does not match board image {board_size}")

    copied_board_path = output_dir / "production_board.png"
    shutil.copy2(board_path, copied_board_path)
    _write_json(output_dir / "layer_contract.json", contract)

    _ensure_dirs(output_dir)
    _export_regions(board, contract, output_dir)
    _export_bbox_overlay(board, contract, output_dir)

    assets, metrics = _extract_assets(board, contract, output_dir)
    check_results, failed_checks = _evaluate_checks(contract, metrics)
    metrics["contract_checks"] = check_results
    probe_metrics_path = output_dir / "probe_metrics.json"
    _write_json(probe_metrics_path, metrics)

    sprite_manifest = _build_sprite_manifest(contract, assets)
    sprite_manifest_path = output_dir / "sprite_manifest.json"
    _write_json(sprite_manifest_path, sprite_manifest)

    layer_ir_path = output_dir / "layer_ir.json"
    layer_ir = _build_layer_ir(contract, board_size, assets)
    _write_json(layer_ir_path, layer_ir)
    validation_errors = validate_layer_ir(load_layer_ir(layer_ir_path), board_size)

    layout_ir_path = output_dir / "layout_ir.json"
    layout_ir = _build_layout_ir(contract, board_size, assets)
    _write_json(layout_ir_path, layout_ir)

    _export_sprite_overview(output_dir, assets)
    _export_focused_comparison(output_dir, assets)
    _export_rough_reconstruction(output_dir, contract)

    probe_report_path = output_dir / "probe_report.md"
    probe_report_path.write_text(
        _build_report(contract, metrics, validation_errors, failed_checks),
        encoding="utf-8",
    )

    return LayerContractResult(
        output_dir=output_dir,
        contract_path=contract_path,
        board_path=board_path,
        copied_board_path=copied_board_path,
        layer_ir_path=layer_ir_path,
        layout_ir_path=layout_ir_path,
        sprite_manifest_path=sprite_manifest_path,
        probe_metrics_path=probe_metrics_path,
        probe_report_path=probe_report_path,
        asset_count=len(assets),
        validation_errors=validation_errors,
        failed_checks=failed_checks,
    )


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError("layer contract must be a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _resolve_path(raw: str, base: Path) -> Path:
    if not raw:
        raise ValueError("path value cannot be empty")
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    return path.resolve()


def _ensure_dirs(output_dir: Path) -> None:
    for name in ("asset_cells", "assets_png", "assets_fit_raw", "diagnostics"):
        (output_dir / name).mkdir(parents=True, exist_ok=True)


def _bbox(value: Any) -> tuple[int, int, int, int]:
    if not isinstance(value, list) or len(value) != 4:
        raise ValueError("bbox must be [x, y, width, height]")
    x, y, width, height = (int(item) for item in value)
    if width <= 0 or height <= 0:
        raise ValueError("bbox width and height must be positive")
    return x, y, width, height


def _crop_box(value: Any) -> tuple[int, int, int, int]:
    x, y, width, height = _bbox(value)
    return x, y, x + width, y + height


def _export_regions(board: Image.Image, contract: dict[str, Any], output_dir: Path) -> None:
    split_x = contract.get("split_x")
    if split_x is not None:
        split = int(split_x)
        if 0 < split < board.width:
            board.crop((0, 0, split, board.height)).save(output_dir / "full_effect_region.png")
            board.crop((split, 0, board.width, board.height)).save(output_dir / "asset_sheet_region.png")

    for crop in contract.get("diagnostic_crops", []) or []:
        crop_id = str(crop["id"])
        board.crop(_crop_box(crop["bbox"])).save(output_dir / "diagnostics" / f"{crop_id}.png")


def _fonts() -> tuple[ImageFont.ImageFont, ImageFont.ImageFont, ImageFont.ImageFont]:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for path in candidates:
        try:
            return (
                ImageFont.truetype(path, 14),
                ImageFont.truetype(path, 18),
                ImageFont.truetype(path, 24),
            )
        except OSError:
            continue
    fallback = ImageFont.load_default()
    return fallback, fallback, fallback


def _export_bbox_overlay(board: Image.Image, contract: dict[str, Any], output_dir: Path) -> None:
    small_font, font, _title_font = _fonts()
    overlay = board.copy()
    draw = ImageDraw.Draw(overlay)
    colors = ["#ff3b30", "#007aff", "#34c759", "#ff9500", "#af52de", "#5856d6", "#00c7be"]

    split_x = contract.get("split_x")
    if split_x is not None:
        draw.line((int(split_x), 0, int(split_x), board.height), fill="#00aaff", width=3)

    for index, cell in enumerate(_asset_cells(contract), start=1):
        color = colors[(index - 1) % len(colors)]
        x, y, width, height = _bbox(cell["bbox"])
        box = (x, y, x + width, y + height)
        draw.rectangle(box, outline=color, width=4)
        label = f"{index}. {cell['id']}"
        text_box = draw.textbbox((0, 0), label, font=small_font)
        draw.rectangle((x, max(0, y - 24), x + text_box[2] + 10, y), fill=color)
        draw.text((x + 5, max(0, y - 22)), label, fill="white", font=small_font)

    for crop in contract.get("diagnostic_crops", []) or []:
        x, y, width, height = _bbox(crop["bbox"])
        draw.rectangle((x, y, x + width, y + height), outline="#00d084", width=4)
        label = str(crop.get("label") or crop["id"])
        draw.text((x + 5, max(0, y - 24)), label, fill="white", font=font, stroke_width=3, stroke_fill="#00a060")

    overlay.save(output_dir / "bbox_overlay.png")


def _asset_cells(contract: dict[str, Any]) -> list[dict[str, Any]]:
    cells = contract.get("asset_cells")
    if not isinstance(cells, list) or not cells:
        raise ValueError("contract must contain a non-empty asset_cells list")
    return [dict(item) for item in cells]


def _extract_assets(
    board: Image.Image,
    contract: dict[str, Any],
    output_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    metrics: dict[str, Any] = {
        "contract_id": str(contract.get("contract_id") or "layer_contract"),
        "board_size": [board.width, board.height],
        "asset_cells": {},
    }
    assets: list[dict[str, Any]] = []

    for cell in _asset_cells(contract):
        asset_id = str(cell["id"])
        crop = board.crop(_crop_box(cell["bbox"]))
        source_cell_path = output_dir / "asset_cells" / f"{asset_id}.png"
        crop.save(source_cell_path)

        rgba, background, trim = _extract_rgba(crop)
        asset_path = output_dir / "assets_png" / f"{asset_id}.png"
        rgba.save(asset_path)
        alpha_metrics = _alpha_metrics(rgba)
        color_metrics = _color_audit(rgba)

        cell_metrics = {
            "role": str(cell.get("role") or asset_id),
            "source_bbox_in_board": list(_bbox(cell["bbox"])),
            "source_cell_size": [crop.width, crop.height],
            "asset_png_size": [rgba.width, rgba.height],
            "background_estimate_rgb": [round(float(value), 2) for value in background],
            "trim_bbox_in_source_cell": trim,
            "alpha_validation": alpha_metrics,
            "color_audit_on_opaque_pixels": color_metrics,
        }
        metrics["asset_cells"][asset_id] = cell_metrics
        assets.append(
            {
                "id": asset_id,
                "role": str(cell.get("role") or asset_id),
                "source_cell": f"asset_cells/{asset_id}.png",
                "output": f"assets_png/{asset_id}.png",
                "transparent": bool(cell.get("transparent", True)),
                "forbid_text": bool(cell.get("forbid_text", False)),
                "scale_mode": str(cell.get("scale_mode") or "contain"),
                "nine_slice_candidate": bool(cell.get("nine_slice_candidate", False)),
                "bbox": list(_bbox(cell["bbox"])),
                "metadata": {
                    "parent_layer": cell.get("parent_layer"),
                    "children_excluded": list(cell.get("children_excluded") or []),
                    "notes": cell.get("notes"),
                },
            }
        )

    return assets, metrics


def _estimate_bg(arr: np.ndarray) -> np.ndarray:
    border = np.concatenate(
        [
            arr[:10, :, :].reshape(-1, 3),
            arr[-10:, :, :].reshape(-1, 3),
            arr[:, :10, :].reshape(-1, 3),
            arr[:, -10:, :].reshape(-1, 3),
        ],
        axis=0,
    )
    return np.median(border, axis=0)


def _extract_rgba(cell: Image.Image) -> tuple[Image.Image, np.ndarray, list[int] | None]:
    rgb = cell.convert("RGB")
    arr = np.asarray(rgb).astype(np.float32)
    background = _estimate_bg(arr)
    dist = np.linalg.norm(arr - background.reshape(1, 1, 3), axis=2)

    seed = dist > 26
    seed = _remove_small_components(seed, min_area=100)
    outside = _border_connected_background(seed)
    filled = ~outside
    mask = filled | (dist > 42)
    mask = _remove_small_components(mask, min_area=120)

    alpha = np.where(mask, 255, 0).astype(np.uint8)
    rgba = rgb.convert("RGBA")
    rgba.putalpha(Image.fromarray(alpha, "L"))
    bbox = Image.fromarray(alpha, "L").getbbox()
    if not bbox:
        return rgba, background, None

    pad = 8
    x0 = max(0, bbox[0] - pad)
    y0 = max(0, bbox[1] - pad)
    x1 = min(rgba.width, bbox[2] + pad)
    y1 = min(rgba.height, bbox[3] + pad)
    return rgba.crop((x0, y0, x1, y1)), background, [x0, y0, x1, y1]


def _remove_small_components(mask: np.ndarray, *, min_area: int) -> np.ndarray:
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    keep = np.zeros_like(mask, dtype=bool)
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))

    for yy in range(height):
        for xx in range(width):
            if not mask[yy, xx] or seen[yy, xx]:
                continue
            queue: deque[tuple[int, int]] = deque([(xx, yy)])
            seen[yy, xx] = True
            points: list[tuple[int, int]] = []
            while queue:
                x, y = queue.popleft()
                points.append((x, y))
                for dx, dy in directions:
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < width and 0 <= ny < height and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((nx, ny))
            if len(points) >= min_area:
                for x, y in points:
                    keep[y, x] = True

    return keep


def _border_connected_background(seed_subject: np.ndarray) -> np.ndarray:
    height, width = seed_subject.shape
    background = ~seed_subject
    seen = np.zeros_like(background, dtype=bool)
    queue: deque[tuple[int, int]] = deque()

    for x in range(width):
        for y in (0, height - 1):
            if background[y, x] and not seen[y, x]:
                seen[y, x] = True
                queue.append((x, y))
    for y in range(height):
        for x in (0, width - 1):
            if background[y, x] and not seen[y, x]:
                seen[y, x] = True
                queue.append((x, y))

    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    while queue:
        x, y = queue.popleft()
        for dx, dy in directions:
            nx = x + dx
            ny = y + dy
            if 0 <= nx < width and 0 <= ny < height and background[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                queue.append((nx, ny))

    return seen


def _alpha_metrics(rgba: Image.Image) -> dict[str, Any]:
    arr = np.asarray(rgba)
    alpha = arr[..., 3]
    return {
        "mode": "RGBA",
        "corner_alpha": [int(alpha[0, 0]), int(alpha[0, -1]), int(alpha[-1, 0]), int(alpha[-1, -1])],
        "corner_alpha_max": int(max(alpha[0, 0], alpha[0, -1], alpha[-1, 0], alpha[-1, -1])),
        "transparent_pixels": int((alpha == 0).sum()),
        "opaque_pixels_alpha_gt_96": int((alpha > 96).sum()),
        "semi_transparent_pixels": int(((alpha > 0) & (alpha <= 96)).sum()),
        "transparent_ratio": round(float((alpha == 0).sum() / alpha.size), 4),
    }


def _color_audit(rgba: Image.Image) -> dict[str, float]:
    arr = np.asarray(rgba)
    alpha = arr[..., 3]
    opaque = alpha > 96
    if not opaque.any():
        return {
            "green_ratio": 0.0,
            "red_ratio_hsv": 0.0,
            "dark_text_like_ratio": 0.0,
            "gold_ratio": 0.0,
            "cream_ratio": 0.0,
        }

    rgb = arr[opaque, :3]
    hue, saturation, value = _rgb_to_hsv(rgb)
    count = int(opaque.sum())
    green = (((hue >= 55) & (hue <= 165)) & (saturation > 0.22) & (value > 0.25)).sum()
    red = ((((hue <= 15) | (hue >= 345)) & (saturation > 0.38) & (value > 0.32))).sum()
    dark = (((value < 0.34) & (saturation > 0.18))).sum()
    gold = (((hue >= 28) & (hue <= 58)) & (saturation > 0.28) & (value > 0.35)).sum()
    cream = (((hue >= 25) & (hue <= 65)) & (saturation < 0.35) & (value > 0.72)).sum()
    return {
        "green_ratio": round(float(green / count), 4),
        "red_ratio_hsv": round(float(red / count), 4),
        "dark_text_like_ratio": round(float(dark / count), 4),
        "gold_ratio": round(float(gold / count), 4),
        "cream_ratio": round(float(cream / count), 4),
    }


def _rgb_to_hsv(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    arr = rgb.astype(np.float32) / 255.0
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]
    max_value = np.max(arr, axis=-1)
    min_value = np.min(arr, axis=-1)
    diff = max_value - min_value
    hue = np.zeros_like(max_value)
    nonzero = diff > 1e-6

    mask = (max_value == r) & nonzero
    hue[mask] = ((g[mask] - b[mask]) / diff[mask]) % 6
    mask = (max_value == g) & nonzero
    hue[mask] = ((b[mask] - r[mask]) / diff[mask]) + 2
    mask = (max_value == b) & nonzero
    hue[mask] = ((r[mask] - g[mask]) / diff[mask]) + 4
    hue *= 60
    saturation = np.where(max_value <= 1e-6, 0, diff / max_value)
    return hue, saturation, max_value


_OPS: dict[str, Callable[[float, float], bool]] = {
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
    "==": operator.eq,
    "!=": operator.ne,
}


def _evaluate_checks(contract: dict[str, Any], metrics: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    results: dict[str, Any] = {}
    failed: list[str] = []

    for check in contract.get("validation_checks", []) or []:
        check_id = str(check["id"])
        asset_id = str(check["asset_id"])
        metric_name = str(check["metric"])
        op_name = str(check.get("op") or "<=")
        expected = float(check["value"])
        actual = _metric_value(metrics, asset_id, metric_name)
        passed = bool(_OPS[op_name](actual, expected))
        results[check_id] = {
            "asset_id": asset_id,
            "metric": metric_name,
            "op": op_name,
            "value": expected,
            "actual": actual,
            "pass": passed,
        }
        if not passed:
            failed.append(check_id)

    manual: dict[str, Any] = {}
    for check in contract.get("manual_checks", []) or []:
        check_id = str(check["id"])
        status = str(check.get("status") or "pending")
        manual[check_id] = {
            "status": status,
            "description": str(check.get("description") or ""),
        }
        if status not in {"pass", "passed"}:
            failed.append(check_id)
    if manual:
        results["manual_visual_check"] = manual

    return results, failed


def _metric_value(metrics: dict[str, Any], asset_id: str, metric_name: str) -> float:
    asset_metrics = metrics["asset_cells"][asset_id]
    if metric_name in asset_metrics["color_audit_on_opaque_pixels"]:
        return float(asset_metrics["color_audit_on_opaque_pixels"][metric_name])
    if metric_name in asset_metrics["alpha_validation"]:
        return float(asset_metrics["alpha_validation"][metric_name])
    raise KeyError(f"unknown metric for {asset_id}: {metric_name}")


def _build_sprite_manifest(contract: dict[str, Any], assets: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "version": str(contract.get("version") or "0.1"),
        "source": "spec_driven_layer_contract",
        "contract_id": str(contract.get("contract_id") or "layer_contract"),
        "assets": [
            {
                "id": asset["id"],
                "role": asset["role"],
                "strategy": "source_preserving_asset_cell_extract_for_validation",
                "output": asset["output"],
                "source_cell": asset["source_cell"],
                "transparent": asset["transparent"],
                "forbid_text": asset["forbid_text"],
                "scale_mode": asset["scale_mode"],
                "nine_slice_candidate": asset["nine_slice_candidate"],
                "metadata": asset["metadata"],
            }
            for asset in assets
        ],
        "text_nodes": list(contract.get("text_nodes") or []),
        "known_issues": [
            "production-board-layer-ownership-drift",
            "asset-cell-tight-padding",
            "closed-panel-alpha-hole-fill",
        ],
    }


def _build_layer_ir(contract: dict[str, Any], board_size: tuple[int, int], assets: list[dict[str, Any]]) -> dict[str, Any]:
    layers: list[dict[str, Any]] = []
    for asset in assets:
        layers.append(
            {
                "id": asset["id"],
                "role": asset["role"],
                "bbox": asset["bbox"],
                "asset_strategy": "segmentation_extract",
                "output": asset["output"],
                "transparent": asset["transparent"],
                "remove_text": asset["forbid_text"],
                "remove_occluding_children": bool(asset["metadata"].get("children_excluded")),
                "nine_slice_candidate": asset["nine_slice_candidate"],
                "metadata": {
                    "source_cell": asset["source_cell"],
                    "scale_mode": asset["scale_mode"],
                    **{key: value for key, value in asset["metadata"].items() if value is not None},
                },
            }
        )

    for node in contract.get("text_nodes", []) or []:
        layers.append(
            {
                "id": str(node["id"]),
                "role": str(node.get("role") or "dynamic_text"),
                "bbox": list(node.get("bbox") or [0, 0, 1, 1]),
                "asset_strategy": "text_node",
                "transparent": False,
                "text": str(node["text"]),
                "remove_text": False,
                "remove_occluding_children": False,
                "nine_slice_candidate": False,
                "metadata": dict(node.get("metadata") or {}),
            }
        )

    return {
        "version": str(contract.get("version") or "0.1"),
        "canvas": {"width": board_size[0], "height": board_size[1]},
        "source_image": "production_board.png",
        "layers": layers,
    }


def _build_layout_ir(contract: dict[str, Any], board_size: tuple[int, int], assets: list[dict[str, Any]]) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    for asset in assets:
        nodes.append(
            {
                "id": asset["id"],
                "type": "SpriteCandidate",
                "role": asset["role"],
                "rect": asset["bbox"],
                "anchor": "top_left",
                "asset": asset["output"],
                "source_cell": asset["source_cell"],
                "scale_mode": asset["scale_mode"],
                "needs_engine_bbox_confirmation": True,
            }
        )
    for node in contract.get("text_nodes", []) or []:
        nodes.append(
            {
                "id": str(node["id"]),
                "type": "Text",
                "role": str(node.get("role") or "dynamic_text"),
                "text": str(node["text"]),
                "rect": list(node.get("bbox") or [0, 0, 1, 1]),
                "needs_engine_bbox_confirmation": not bool(node.get("bbox")),
            }
        )

    layout = {
        "version": str(contract.get("version") or "0.1"),
        "screen": {
            "name": str(contract.get("contract_id") or "layer_contract"),
            "canvas": {"width": board_size[0], "height": board_size[1]},
            "source_image": "production_board.png",
            "nodes": nodes,
        },
    }
    if contract.get("rough_reconstruction"):
        layout["screen"]["rough_reconstruction"] = contract["rough_reconstruction"]
    return layout


def _checker(size: tuple[int, int], cell: int = 16) -> Image.Image:
    width, height = size
    image = Image.new("RGB", size, "#f7f7f7")
    draw = ImageDraw.Draw(image)
    for y in range(0, height, cell):
        for x in range(0, width, cell):
            if (x // cell + y // cell) % 2:
                draw.rectangle((x, y, x + cell - 1, y + cell - 1), fill="#dfdfdf")
    return image


def _export_sprite_overview(output_dir: Path, assets: list[dict[str, Any]]) -> None:
    small_font, _font, title_font = _fonts()
    tile_width = 340
    tile_height = 220
    cols = 2
    rows = math.ceil(len(assets) / cols)
    overview = Image.new("RGB", (tile_width * cols, tile_height * rows + 58), "#f4f1ea")
    draw = ImageDraw.Draw(overview)
    draw.text((14, 14), f"{output_dir.name} source sprites", fill="#222", font=title_font)

    for index, asset in enumerate(assets):
        col = index % cols
        row = index // cols
        x = col * tile_width
        y = 58 + row * tile_height
        bg = _checker((tile_width, tile_height), 18)
        rgba = Image.open(output_dir / asset["output"]).convert("RGBA")
        max_width = tile_width - 44
        max_height = tile_height - 58
        scale = min(max_width / rgba.width, max_height / rgba.height, 1.0)
        show = rgba.resize((max(1, int(rgba.width * scale)), max(1, int(rgba.height * scale))), Image.Resampling.LANCZOS)
        bg.paste(show, ((tile_width - show.width) // 2, 40 + (max_height - show.height) // 2), show)
        overview.paste(bg, (x, y))
        draw.text((x + 12, y + 10), asset["id"], fill="#222", font=small_font)

    overview.save(output_dir / "sprite_overview.png")


def _export_focused_comparison(output_dir: Path, assets: list[dict[str, Any]]) -> None:
    small_font, _font, title_font = _fonts()
    cell_width = 300
    cell_height = 190
    rows = math.ceil(len(assets) / 2)
    image = Image.new("RGB", (cell_width * 4, cell_height * rows + 64), "#f4f1ea")
    draw = ImageDraw.Draw(image)
    draw.text((14, 16), "layer contract audit: asset cell -> transparent candidate", fill="#222", font=title_font)

    for index, asset in enumerate(assets):
        row = index // 2
        pair = index % 2
        x0 = pair * cell_width * 2
        y0 = 64 + row * cell_height
        source = Image.open(output_dir / asset["source_cell"]).convert("RGB")
        rgba = Image.open(output_dir / asset["output"]).convert("RGBA")

        draw.rectangle((x0, y0, x0 + cell_width - 1, y0 + cell_height - 1), fill="#fffdf8", outline="#d6c7aa")
        draw.text((x0 + 10, y0 + 8), f"{asset['id']} cell", fill="#222", font=small_font)
        source.thumbnail((cell_width - 28, cell_height - 50), Image.Resampling.LANCZOS)
        image.paste(source, (x0 + (cell_width - source.width) // 2, y0 + 36))

        x1 = x0 + cell_width
        bg = _checker((cell_width, cell_height), 16)
        show = rgba.copy()
        show.thumbnail((cell_width - 28, cell_height - 50), Image.Resampling.LANCZOS)
        bg.paste(show, ((cell_width - show.width) // 2, 36 + (cell_height - 50 - show.height) // 2), show)
        image.paste(bg, (x1, y0))
        draw.rectangle((x1, y0, x1 + cell_width - 1, y0 + cell_height - 1), outline="#d6c7aa")
        draw.text((x1 + 10, y0 + 8), f"{asset['id']} PNG", fill="#222", font=small_font)

    image.save(output_dir / "focused_split_comparison.png")


def _export_rough_reconstruction(output_dir: Path, contract: dict[str, Any]) -> None:
    rough = contract.get("rough_reconstruction")
    if not rough:
        return

    small_font, _font, title_font = _fonts()
    canvas_width, canvas_height = (int(value) for value in rough.get("canvas", [360, 540]))
    canvas = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
    fit_dir = output_dir / "assets_fit_raw"

    for item in rough.get("layers", []) or []:
        layer_id = str(item["id"])
        asset_id = str(item["asset_id"])
        x, y, width, height = _bbox(item["rect"])
        instance = Image.new("RGBA", (canvas_width, canvas_height), (0, 0, 0, 0))
        sprite = Image.open(output_dir / "assets_png" / f"{asset_id}.png").convert("RGBA")
        sprite = sprite.resize((width, height), Image.Resampling.LANCZOS)
        instance.paste(sprite, (x, y), sprite)
        instance.save(fit_dir / f"{layer_id}.png")
        canvas.alpha_composite(instance)

    draw = ImageDraw.Draw(canvas)
    for node in rough.get("text_nodes", []) or []:
        font_size = int(node.get("font_size") or 32)
        font = _font_for_size(font_size)
        _draw_centered_text(
            draw,
            _bbox(node["rect"]),
            str(node["text"]),
            font,
            str(node.get("fill") or "#3f2b12"),
            str(node.get("stroke_fill") or "#000000"),
            int(node.get("stroke_width") or 0),
        )

    canvas.save(output_dir / "rough_reconstruction.png")
    _export_rough_comparison(output_dir, contract, canvas)


def _font_for_size(size: int) -> ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _draw_centered_text(
    draw: ImageDraw.ImageDraw,
    rect: tuple[int, int, int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    stroke_fill: str,
    stroke_width: int,
) -> None:
    x, y, width, height = rect
    text_box = draw.textbbox((0, 0), text, font=font, stroke_width=stroke_width)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    draw.text(
        (x + (width - text_width) / 2, y + (height - text_height) / 2 - 2),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def _export_rough_comparison(output_dir: Path, contract: dict[str, Any], reconstruction: Image.Image) -> None:
    rough = contract.get("rough_reconstruction") or {}
    comparison = rough.get("comparison") or {}
    columns: list[tuple[str, Image.Image]] = []

    source_crop = comparison.get("source_crop")
    if source_crop:
        source_path = output_dir / "diagnostics" / f"{source_crop['id']}.png"
        if source_path.exists():
            columns.append((str(source_crop.get("label") or source_crop["id"]), Image.open(source_path).convert("RGBA")))

    columns.append((str(comparison.get("reconstruction_label") or "rough reconstruction"), reconstruction))

    composite_asset_id = comparison.get("composite_asset_id")
    if composite_asset_id:
        composite_path = output_dir / "assets_png" / f"{composite_asset_id}.png"
        if composite_path.exists():
            columns.append((str(comparison.get("composite_label") or composite_asset_id), Image.open(composite_path).convert("RGBA")))

    if not columns:
        return

    _small_font, _font, title_font = _fonts()
    column_width = 380
    panel_height = 520
    image = Image.new("RGB", (column_width * len(columns), panel_height + 80), "#f4f1ea")
    draw = ImageDraw.Draw(image)
    for index, (label, item) in enumerate(columns):
        x = index * column_width + 20
        draw.text((x, 18), label, fill="#222", font=title_font)
        bg = _checker((column_width - 40, panel_height), 18).convert("RGBA")
        show = item.copy()
        show.thumbnail((column_width - 44, panel_height - 20), Image.Resampling.LANCZOS)
        bg.paste(show, ((bg.width - show.width) // 2, (bg.height - show.height) // 2), show)
        image.paste(bg.convert("RGB"), (x, 58))

    image.save(output_dir / "rough_reconstruction_comparison.png")


def _build_report(
    contract: dict[str, Any],
    metrics: dict[str, Any],
    validation_errors: list[str],
    failed_checks: list[str],
) -> str:
    contract_id = str(contract.get("contract_id") or "layer_contract")
    asset_cells = metrics["asset_cells"]
    primary_asset_id = str(contract.get("primary_asset_id") or next(iter(asset_cells)))
    primary = asset_cells[primary_asset_id]
    checks = metrics.get("contract_checks", {})
    verdict = "pass" if not validation_errors and not failed_checks else "fail"

    lines = [
        f"# {contract_id} Contract Validation",
        "",
        "## Result",
        "",
        f"`{contract_id}` validation result: **{verdict}**.",
        "",
        "## Evidence",
        "",
        f"- Board size: `{metrics['board_size'][0]}x{metrics['board_size'][1]}`.",
        f"- Asset cells: `{len(asset_cells)}`.",
        f"- Primary asset: `{primary_asset_id}`.",
        f"- Primary source cell: `{primary['source_cell_size'][0]}x{primary['source_cell_size'][1]}`.",
        f"- Primary transparent candidate: `{primary['asset_png_size'][0]}x{primary['asset_png_size'][1]}`.",
        f"- Primary corner alpha: `{primary['alpha_validation']['corner_alpha']}`.",
        f"- Validation errors: `{len(validation_errors)}`.",
        f"- Failed checks: `{len(failed_checks)}`.",
        "",
        "## Contract Checks",
        "",
        "```json",
        json.dumps(checks, indent=2, ensure_ascii=False),
        "```",
        "",
        "## Interpretation",
        "",
        str(contract.get("interpretation") or "This validates layer ownership and artifact generation from a production board contract. It does not prove final production readiness."),
        "",
        "## Files",
        "",
        "- `layer_contract.json`: copied input contract.",
        "- `production_board.png`: copied source board.",
        "- `bbox_overlay.png`: board with asset-cell boxes.",
        "- `asset_cells/*.png`: source cell crops for audit.",
        "- `assets_png/*.png`: transparent candidates extracted from source cells.",
        "- `assets_fit_raw/*.png`: rough layout instances when rough reconstruction is configured.",
        "- `sprite_overview.png`: transparent candidate overview.",
        "- `focused_split_comparison.png`: cell-to-transparent-candidate comparison.",
        "- `rough_reconstruction.png`: rough reconstruction when configured.",
        "- `rough_reconstruction_comparison.png`: source / reconstruction / reference comparison when configured.",
        "- `probe_metrics.json`: machine-readable metrics.",
        "- `sprite_manifest.json`, `layer_ir.json`, `layout_ir.json`: validation metadata.",
        "",
        "## Verdict",
        "",
        "```text",
        str(contract.get("verdict") or f"{contract_id}: {verdict} for configured contract checks"),
        "```",
    ]
    return "\n".join(lines) + "\n"
