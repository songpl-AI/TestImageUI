from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.core.types import BBox, LayerIR, LayerItem
from src.exporters.layout_ir import build_layout_ir, save_layout_ir
from src.ir.layer_ir import layer_ir_to_json, validate_layer_ir


PANEL_SPLIT_ASSET_IDS = {
    "panel_base",
    "panel_top_title_plate",
    "panel_corner_flowers",
    "panel_bottom_leaves",
    "panel_inner_texture",
}


@dataclass(frozen=True)
class SpecPlanResult:
    output_dir: Path
    ui_spec_path: Path
    layer_ir_path: Path
    layout_ir_path: Path
    sprite_manifest_path: Path
    full_effect_prompt_path: Path
    production_board_prompt_path: Path
    sprite_plan_path: Path
    validation_report_path: Path
    asset_prompt_count: int
    validation_errors: list[str]
    validation_warnings: list[str]


def export_spec_plan(brief_path: Path, output_dir: Path) -> SpecPlanResult:
    brief = _load_json(brief_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    plan = _build_template_plan(brief, brief_path=brief_path)
    layer_ir = _build_layer_ir(plan)
    validation_errors = validate_layer_ir(layer_ir, (plan["canvas"]["width"], plan["canvas"]["height"]))
    validation_warnings = _validate_plan_contract(plan)

    ui_spec_path = output_dir / "ui_spec.json"
    layer_ir_path = output_dir / "layer_ir.json"
    layout_ir_path = output_dir / "layout_ir.json"
    sprite_manifest_path = output_dir / "sprite_manifest.json"
    full_effect_prompt_path = output_dir / "full_effect_prompt.txt"
    production_board_prompt_path = output_dir / "production_board_prompt.txt"
    sprite_plan_path = output_dir / "sprite_plan.md"
    validation_report_path = output_dir / "spec_validation_report.md"
    asset_prompts_dir = output_dir / "asset_prompts"
    asset_prompts_dir.mkdir(parents=True, exist_ok=True)

    _write_json(ui_spec_path, plan)
    _write_json(layer_ir_path, layer_ir_to_json(layer_ir))
    save_layout_ir(build_layout_ir(layer_ir, asset_base="assets_fit_raw"), layout_ir_path)

    sprite_manifest = _build_sprite_manifest(plan)
    _write_json(sprite_manifest_path, sprite_manifest)

    asset_prompt_count = 0
    for asset in sprite_manifest["assets"]:
        prompt_path = asset_prompts_dir / f"{asset['id']}.txt"
        prompt_path.write_text(_build_asset_prompt(plan, asset) + "\n", encoding="utf-8")
        asset["prompt"] = str(prompt_path.relative_to(output_dir))
        asset_prompt_count += 1
    _write_json(sprite_manifest_path, sprite_manifest)

    full_effect_prompt_path.write_text(_build_full_effect_prompt(plan) + "\n", encoding="utf-8")
    production_board_prompt_path.write_text(_build_production_board_prompt(plan, sprite_manifest) + "\n", encoding="utf-8")
    sprite_plan_path.write_text(_build_sprite_plan_markdown(plan, sprite_manifest) + "\n", encoding="utf-8")
    validation_report_path.write_text(
        _build_validation_report(plan, validation_errors, validation_warnings, sprite_manifest) + "\n",
        encoding="utf-8",
    )

    return SpecPlanResult(
        output_dir=output_dir,
        ui_spec_path=ui_spec_path,
        layer_ir_path=layer_ir_path,
        layout_ir_path=layout_ir_path,
        sprite_manifest_path=sprite_manifest_path,
        full_effect_prompt_path=full_effect_prompt_path,
        production_board_prompt_path=production_board_prompt_path,
        sprite_plan_path=sprite_plan_path,
        validation_report_path=validation_report_path,
        asset_prompt_count=asset_prompt_count,
        validation_errors=validation_errors,
        validation_warnings=validation_warnings,
    )


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError("brief must be a JSON object")
    return value


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _build_template_plan(brief: dict[str, Any], *, brief_path: Path) -> dict[str, Any]:
    canvas = brief.get("canvas") or {}
    width = int(canvas.get("width", 720))
    height = int(canvas.get("height", 1280))
    screen_name = str(brief.get("screen_name") or "spec_driven_shop_bundle")
    ui_type = str(brief.get("ui_type") or "shop_bundle")
    if ui_type != "shop_bundle":
        raise ValueError("spec planning MVP currently supports ui_type='shop_bundle'")

    text = dict(brief.get("text") or {})
    style = {
        "theme": str(brief.get("theme") or "pastoral match-3 spring shop"),
        "game_genre": str(brief.get("game_genre") or "casual match-3 mobile game"),
        "visual_style": str(
            brief.get("visual_style")
            or "polished 2D game UI, soft bevels, clean outlines, warm highlights, readable shapes"
        ),
        "palette": list(brief.get("palette") or ["mint green", "cream", "gold", "berry red"]),
        "material": str(brief.get("material") or "painted enamel, soft gold trim, subtle fabric texture"),
    }

    layers = _shop_bundle_layers(width, height, text)
    return {
        "version": "0.1",
        "screen_name": screen_name,
        "ui_type": ui_type,
        "source": {
            "brief_path": str(brief_path),
            "natural_language": str(
                brief.get("natural_language")
                or "Generate a shop bundle UI with a reusable asset plan and editable text nodes."
            ),
        },
        "canvas": {
            "width": width,
            "height": height,
        },
        "style": style,
        "contract": {
            "source_of_truth": "ui_spec_json",
            "full_effect": "visual target only; it must not define final positions or sizes",
            "assets_png": "reusable clean source sprites; natural dimensions are not layout dimensions",
            "assets_fit_raw": "one fitted instance per layer bbox for reconstruction",
            "text_policy": "dynamic text remains Text Node; only fixed title art may be sprite text",
            "image_generation_risk": "full effect and asset sheet may drift; validate with reconstruction",
        },
        "layers": layers,
    }


def _shop_bundle_layers(width: int, height: int, text: dict[str, Any]) -> list[dict[str, Any]]:
    title = str(text.get("title", "SPRING SHOP"))
    hot_deal = str(text.get("deal_label", "HOT DEAL"))
    buy = str(text.get("buy_button", "BUY"))
    currency = str(text.get("currency_amount", "3200"))
    prices = list(text.get("prices") or ["$3", "$6", "$9"])
    counts = list(text.get("item_counts") or ["x50", "x3", "x1"])
    discounts = list(text.get("discounts") or ["20%", "40%", "60%"])

    panel_x = round(width * 0.083)
    panel_y = round(height * 0.145)
    panel_w = round(width * 0.834)
    panel_h = round(height * 0.72)
    panel_top_plate_bbox = [round(width * 0.25), round(height * 0.085), round(width * 0.5), round(height * 0.12)]
    panel_inner_bbox = [
        panel_x + round(panel_w * 0.08),
        panel_y + round(panel_h * 0.2),
        round(panel_w * 0.84),
        round(panel_h * 0.53),
    ]
    panel_corner_flowers_bbox = [
        panel_x + round(panel_w * 0.04),
        panel_y - round(panel_h * 0.055),
        round(panel_w * 0.92),
        round(panel_h * 0.18),
    ]
    panel_bottom_leaves_bbox = [
        panel_x + round(panel_w * 0.08),
        panel_y + round(panel_h * 0.755),
        round(panel_w * 0.84),
        round(panel_h * 0.16),
    ]
    card_w = round(panel_w * 0.255)
    card_h = round(panel_h * 0.47)
    card_gap = round(panel_w * 0.04)
    card_y = panel_y + round(panel_h * 0.28)
    card_x1 = panel_x + round(panel_w * 0.08)
    card_positions = [card_x1 + i * (card_w + card_gap) for i in range(3)]

    layers: list[dict[str, Any]] = [
        _image_layer(
            "background_scene",
            "background_scene",
            [0, 0, width, height],
            0,
            asset_id="background_scene",
            transparent=False,
            prompt_subject="low contrast spring garden background behind a mobile game shop UI",
            scale_mode="cover",
        ),
        _image_layer(
            "panel_base",
            "panel_base_clean_candidate",
            [panel_x, panel_y, panel_w, panel_h],
            10,
            asset_id="panel_base",
            prompt_subject=(
                "clean large rounded shop panel base with cream center and gold trim; "
                "no title plate, no flowers, no leaves, no ribbon, no cards, no buttons, no text, no icons"
            ),
            scale_mode="nine_slice",
            nine_slice=True,
        ),
        _image_layer(
            "panel_inner_texture",
            "panel_inner_texture_tile",
            panel_inner_bbox,
            11,
            asset_id="panel_inner_texture",
            prompt_subject=(
                "plain reusable inner panel material tile, soft cream fabric or parchment texture only; "
                "no border, no trim, no title plate, no flowers, no leaves, no text"
            ),
            scale_mode="stretch",
        ),
        _image_layer(
            "panel_corner_flowers",
            "panel_corner_flowers",
            panel_corner_flowers_bbox,
            18,
            asset_id="panel_corner_flowers",
            prompt_subject=(
                "separate transparent flower and leaf corner decorations for the top corners of the shop panel; "
                "no panel base, no title text, no cards, no buttons"
            ),
            scale_mode="contain",
        ),
        _image_layer(
            "panel_bottom_leaves",
            "panel_bottom_leaves",
            panel_bottom_leaves_bbox,
            18,
            asset_id="panel_bottom_leaves",
            prompt_subject=(
                "separate transparent leaf and flower decoration cluster for the bottom of the shop panel; "
                "no panel base, no buttons, no text"
            ),
            scale_mode="contain",
        ),
        _image_layer(
            "panel_top_title_plate",
            "panel_top_title_plate",
            panel_top_plate_bbox,
            20,
            asset_id="panel_top_title_plate",
            prompt_subject="ornate green and gold top title plate for the shop panel, without text",
            scale_mode="contain",
        ),
        _image_layer(
            "title_logo",
            "fixed_art_text",
            [round(width * 0.275), round(height * 0.115), round(width * 0.45), round(height * 0.06)],
            21,
            asset_id="title_logo",
            prompt_subject=f'fixed art title text "{title}" in polished game UI lettering',
            scale_mode="contain",
            text=title,
            remove_text=False,
        ),
        _image_layer(
            "close_button",
            "close_button",
            [round(width * 0.84), round(height * 0.13), round(width * 0.08), round(width * 0.08)],
            30,
            asset_id="close_button",
            prompt_subject="round close button with gold rim and red center, no background",
            scale_mode="contain",
        ),
        _image_layer(
            "currency_bar_bg",
            "currency_bar_background",
            [round(width * 0.62), round(height * 0.055), round(width * 0.28), round(height * 0.055)],
            25,
            asset_id="currency_bar_bg",
            prompt_subject="compact capsule currency bar background, no icon, no number",
            scale_mode="nine_slice",
            nine_slice=True,
        ),
        _image_layer(
            "coin_icon",
            "currency_icon",
            [round(width * 0.635), round(height * 0.061), round(width * 0.045), round(width * 0.045)],
            26,
            asset_id="coin_icon",
            prompt_subject="small gold coin icon with clean transparent edge",
            scale_mode="contain",
        ),
        _text_layer(
            "currency_amount_text",
            "dynamic_text_currency_amount",
            [round(width * 0.69), round(height * 0.061), round(width * 0.15), round(height * 0.04)],
            27,
            currency,
        ),
    ]

    for index, card_x in enumerate(card_positions, start=1):
        card_id = f"product_card_{index}"
        layers.extend(
            [
                _image_layer(
                    f"{card_id}_bg",
                    "product_card_background",
                    [card_x, card_y, card_w, card_h],
                    40 + index * 10,
                    asset_id="product_card_bg",
                    prompt_subject="reusable product card background with rounded cream center and green-gold frame, no text, no icon",
                    scale_mode="nine_slice",
                    nine_slice=True,
                ),
                _image_layer(
                    f"{card_id}_item_icon",
                    "reward_item_icon",
                    [card_x + round(card_w * 0.2), card_y + round(card_h * 0.14), round(card_w * 0.6), round(card_w * 0.6)],
                    41 + index * 10,
                    asset_id=f"reward_icon_{index}",
                    prompt_subject=f"standalone shop reward icon variant {index}, matching spring match-3 UI style",
                    scale_mode="contain",
                ),
                _image_layer(
                    f"{card_id}_discount_badge_bg",
                    "discount_badge_background",
                    [card_x + round(card_w * 0.5), card_y - round(card_h * 0.035), round(card_w * 0.48), round(card_h * 0.13)],
                    42 + index * 10,
                    asset_id="discount_badge_bg",
                    prompt_subject="small red discount ribbon badge background, no text",
                    scale_mode="stretch",
                ),
                _text_layer(
                    f"{card_id}_discount_text",
                    "dynamic_text_discount",
                    [card_x + round(card_w * 0.54), card_y - round(card_h * 0.015), round(card_w * 0.38), round(card_h * 0.08)],
                    43 + index * 10,
                    discounts[index - 1],
                ),
                _text_layer(
                    f"{card_id}_count_text",
                    "dynamic_text_item_count",
                    [card_x + round(card_w * 0.28), card_y + round(card_h * 0.53), round(card_w * 0.44), round(card_h * 0.08)],
                    44 + index * 10,
                    counts[index - 1],
                ),
                _image_layer(
                    f"{card_id}_price_tag_bg",
                    "price_tag_background",
                    [card_x + round(card_w * 0.16), card_y + round(card_h * 0.72), round(card_w * 0.68), round(card_h * 0.15)],
                    45 + index * 10,
                    asset_id="price_tag_bg",
                    prompt_subject="small rounded price tag background, no text",
                    scale_mode="nine_slice",
                    nine_slice=True,
                ),
                _text_layer(
                    f"{card_id}_price_text",
                    "dynamic_text_price",
                    [card_x + round(card_w * 0.27), card_y + round(card_h * 0.745), round(card_w * 0.46), round(card_h * 0.09)],
                    46 + index * 10,
                    prices[index - 1],
                ),
            ]
        )

    layers.extend(
        [
            _image_layer(
                "hot_deal_ribbon_bg",
                "subtitle_ribbon_background",
                [panel_x + round(panel_w * 0.24), panel_y + round(panel_h * 0.175), round(panel_w * 0.52), round(panel_h * 0.07)],
                35,
                asset_id="hot_deal_ribbon_bg",
                prompt_subject="wide red and gold subtitle ribbon background, no text",
                scale_mode="stretch",
            ),
            _text_layer(
                "hot_deal_text",
                "dynamic_text_subtitle",
                [panel_x + round(panel_w * 0.32), panel_y + round(panel_h * 0.19), round(panel_w * 0.36), round(panel_h * 0.04)],
                36,
                hot_deal,
            ),
            _image_layer(
                "buy_button_bg",
                "button_background",
                [round(width * 0.31), panel_y + round(panel_h * 0.81), round(width * 0.38), round(height * 0.085)],
                90,
                asset_id="buy_button_bg",
                prompt_subject="large green primary buy button background with gold trim, no text",
                scale_mode="nine_slice",
                nine_slice=True,
            ),
            _text_layer(
                "buy_button_text",
                "dynamic_text_button_label",
                [round(width * 0.39), panel_y + round(panel_h * 0.83), round(width * 0.22), round(height * 0.045)],
                91,
                buy,
            ),
        ]
    )
    return sorted(layers, key=lambda item: item["z"])


def _image_layer(
    layer_id: str,
    role: str,
    bbox: list[int],
    z: int,
    *,
    asset_id: str,
    prompt_subject: str,
    scale_mode: str,
    transparent: bool = True,
    nine_slice: bool = False,
    text: str | None = None,
    remove_text: bool = True,
) -> dict[str, Any]:
    return {
        "id": layer_id,
        "type": "image",
        "role": role,
        "bbox": bbox,
        "z": z,
        "asset_id": asset_id,
        "asset_strategy": "regenerate",
        "transparent": transparent,
        "remove_text": remove_text,
        "remove_occluding_children": True,
        "nine_slice_candidate": nine_slice,
        "scale_mode": scale_mode,
        "prompt_subject": prompt_subject,
        "text": text,
    }


def _text_layer(layer_id: str, role: str, bbox: list[int], z: int, text: str) -> dict[str, Any]:
    return {
        "id": layer_id,
        "type": "text",
        "role": role,
        "bbox": bbox,
        "z": z,
        "asset_strategy": "text_node",
        "transparent": True,
        "remove_text": False,
        "remove_occluding_children": False,
        "nine_slice_candidate": False,
        "scale_mode": "text",
        "text": text,
    }


def _build_layer_ir(plan: dict[str, Any]) -> LayerIR:
    layers: list[LayerItem] = []
    for item in plan["layers"]:
        metadata = {
            "z": item["z"],
            "scale_mode": item["scale_mode"],
        }
        if item.get("asset_id"):
            metadata["asset_id"] = item["asset_id"]
            metadata["source_asset_png"] = f"assets_png/{item['asset_id']}.png"
        if item.get("prompt_subject"):
            metadata["prompt_subject"] = item["prompt_subject"]

        layers.append(
            LayerItem(
                id=str(item["id"]),
                role=str(item["role"]),
                bbox=BBox.from_json(item["bbox"]),
                asset_strategy=item["asset_strategy"],
                transparent=bool(item.get("transparent", True)),
                text=item.get("text"),
                remove_text=bool(item.get("remove_text", False)),
                remove_occluding_children=bool(item.get("remove_occluding_children", False)),
                nine_slice_candidate=bool(item.get("nine_slice_candidate", False)),
                metadata=metadata,
            )
        )

    canvas = plan["canvas"]
    return LayerIR(
        version=str(plan["version"]),
        canvas_width=int(canvas["width"]),
        canvas_height=int(canvas["height"]),
        source_image=f"{plan['screen_name']}_full_effect.png",
        layers=layers,
    )


def _build_sprite_manifest(plan: dict[str, Any]) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for layer in plan["layers"]:
        if layer["type"] == "image":
            grouped[layer["asset_id"]].append(layer)

    assets: list[dict[str, Any]] = []
    for asset_id, layers in sorted(grouped.items()):
        first = layers[0]
        role = first["role"]
        strategy = "fixed_art_text" if "art_text" in role else "standalone_sprite"
        assets.append(
            {
                "id": asset_id,
                "role": role,
                "strategy": strategy,
                "output": f"assets_png/{asset_id}.png",
                "transparent": first.get("transparent", True),
                "forbid_text": strategy != "fixed_art_text",
                "scale_mode": first["scale_mode"],
                "nine_slice_candidate": bool(first.get("nine_slice_candidate", False)),
                "prompt_subject": first["prompt_subject"],
                "layers": [
                    {
                        "layer_id": layer["id"],
                        "bbox": layer["bbox"],
                        "fit_output": f"assets_fit_raw/{layer['id']}.png",
                        "z": layer["z"],
                    }
                    for layer in layers
                ],
            }
        )
    return {
        "version": plan["version"],
        "screen_name": plan["screen_name"],
        "source": "spec_driven_generation",
        "assets": assets,
    }


def _validate_plan_contract(plan: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    layer_ids = [layer["id"] for layer in plan["layers"]]
    if len(layer_ids) != len(set(layer_ids)):
        warnings.append("duplicate layer id detected in ui_spec.json")

    image_layers = [layer for layer in plan["layers"] if layer["type"] == "image"]
    text_layers = [layer for layer in plan["layers"] if layer["type"] == "text"]
    if len(image_layers) < 8:
        warnings.append("effect image has fewer than 8 image layers; sprite plan may be too small to validate")
    if not text_layers:
        warnings.append("no Text Node layers found; text policy is not exercised")

    for layer in image_layers:
        role = layer["role"].lower()
        if any(token in role for token in ("button", "panel", "bar", "card", "tag")):
            if layer.get("scale_mode") not in {"nine_slice", "stretch", "contain", "cover"}:
                warnings.append(f"{layer['id']}: missing explicit scale_mode")
        if "background" in role and layer.get("remove_text") is False:
            warnings.append(f"{layer['id']}: background layer should forbid baked dynamic text")
        if layer.get("asset_id") == "main_panel_bg" and layer.get("asset_strategy") != "reference_only":
            warnings.append(
                f"{layer['id']}: main_panel_bg must not be emitted as an engine-ready sprite; "
                "split it into panel_base, panel_top_title_plate, panel_corner_flowers, panel_bottom_leaves, and panel_inner_texture"
            )

    for layer in text_layers:
        if not layer.get("text"):
            warnings.append(f"{layer['id']}: text layer is missing text")

    asset_ids = {str(layer.get("asset_id")) for layer in image_layers if layer.get("asset_id")}
    missing_panel_assets = sorted(PANEL_SPLIT_ASSET_IDS - asset_ids)
    if missing_panel_assets:
        warnings.append(f"main panel split assets missing: {', '.join(missing_panel_assets)}")

    warnings.append("offline validation only: no real full_effect or sprite PNG was generated")
    warnings.append("variant mismatch remains possible between full_effect and independent asset prompts")
    return warnings


def _build_full_effect_prompt(plan: dict[str, Any]) -> str:
    canvas = plan["canvas"]
    text_values = [layer["text"] for layer in plan["layers"] if layer["type"] == "text" and layer.get("text")]
    layer_lines = [
        f"- {layer['id']}: {layer['role']}, bbox={layer['bbox']}, z={layer['z']}, scale={layer['scale_mode']}"
        for layer in plan["layers"]
    ]
    return "\n".join(
        [
            "Use case: ui-mockup",
            "Asset type: source effect image for a game UI split pipeline",
            f"Primary request: {plan['source']['natural_language']}",
            f"Canvas: {canvas['width']}x{canvas['height']}, no device frame.",
            f"Theme: {plan['style']['theme']}.",
            f"Game genre: {plan['style']['game_genre']}.",
            f"Style: {plan['style']['visual_style']}; material: {plan['style']['material']}.",
            f"Palette: {', '.join(plan['style']['palette'])}.",
            "Composition contract: follow the UI Spec JSON as the source of truth for approximate layout, hierarchy, and required elements.",
            "Engineering constraints: UI elements must be visually separable for later standalone sprite generation; panels, cards, buttons, icons, bars, and badges need clean boundaries.",
            "Text policy: render only the listed short texts; keep them readable and easy to replace as Text Nodes.",
            f"Text (verbatim): {', '.join(json.dumps(value, ensure_ascii=False) for value in text_values)}.",
            "Avoid: device frame, watermark, brand logos, garbled text, excessive tiny labels, fused UI/background edges, strong perspective, cropped key elements.",
            "",
            "Layer contract:",
            *layer_lines,
        ]
    )


def _build_production_board_prompt(plan: dict[str, Any], sprite_manifest: dict[str, Any]) -> str:
    canvas = plan["canvas"]
    asset_lines = [
        f"- {asset['id']}: same visual variant as full_effect layer(s) "
        f"{', '.join(layer['layer_id'] for layer in asset['layers'])}; "
        f"base art only; scale_mode={asset['scale_mode']}; forbid_text={asset['forbid_text']}"
        for asset in sprite_manifest["assets"]
    ]
    return "\n".join(
        [
            "Create one production board image that contains both the full UI and its reusable asset sheet.",
            f"Left side: full_effect at {canvas['width']}x{canvas['height']} using the UI Spec layout.",
            "Right side: asset_sheet with one clean isolated cell per asset id.",
            "Asset-sheet contract: every asset cell must be the exact same visual variant as the matching full_effect layer, preserving silhouette, material, color, border, corner radius, lighting, and decoration ownership.",
            "Panel ownership contract: do not generate `main_panel_bg` as a combined engine sprite; split it into `panel_base`, `panel_top_title_plate`, `panel_corner_flowers`, `panel_bottom_leaves`, and `panel_inner_texture` cells.",
            "`panel_base` must exclude title plates, corner flowers, bottom leaves, inner texture overlays, cards, buttons, icons, numbers, and text.",
            "Only remove child layers such as dynamic text, item counts, prices, icons, or numbers when the manifest says forbid_text=true.",
            "Do not rely on rendered text labels inside the asset sheet; the manifest maps asset ids to cells externally.",
            "Use transparent-looking checker or flat neutral cell backgrounds only if needed for visibility; do not bake cell backgrounds into sprites.",
            "Avoid: variant mismatch, relayout of repeated slots, merged assets, tiny unreadable labels, extra decorative assets not listed.",
            "",
            "Assets:",
            *asset_lines,
        ]
    )


def _build_asset_prompt(plan: dict[str, Any], asset: dict[str, Any]) -> str:
    constraints = [
        f"Generate a clean standalone game UI sprite for asset `{asset['id']}`.",
        f"Subject: {asset['prompt_subject']}.",
        f"Match the shared style: {plan['style']['visual_style']}; {plan['style']['material']}.",
        f"Palette anchor: {', '.join(plan['style']['palette'])}.",
        "The sprite must match the same visual variant used in the full_effect UI Spec.",
        "Center the subject with modest padding; the generated natural size is not the engineering layout size.",
        f"Scale mode after generation: {asset['scale_mode']}.",
    ]
    if asset["transparent"]:
        constraints.append("Output with transparent background, or on a perfectly uniform chroma-key background for later alpha extraction.")
    if asset["forbid_text"]:
        constraints.append("Do not include any text, letters, numbers, labels, icons from child layers, or neighboring UI elements.")
    if asset["nine_slice_candidate"]:
        constraints.append("Keep corners and edges suitable for nine-slice scaling; avoid baked text or centered child content.")
    constraints.append("This is an engineering sprite, not a rectangular crop from the full image.")
    return "\n".join(f"- {line}" for line in constraints)


def _build_sprite_plan_markdown(plan: dict[str, Any], sprite_manifest: dict[str, Any]) -> str:
    image_assets = sprite_manifest["assets"]
    text_nodes = [layer for layer in plan["layers"] if layer["type"] == "text"]
    lines = [
        "# Sprite Plan",
        "",
        f"Source: spec-driven plan for `{plan['screen_name']}`.",
        "",
        "## 自动确认",
        "",
        "| id | 类型 | 输出 | 处理方式 | 原因 |",
        "|---|---|---|---|---|",
    ]
    for asset in image_assets:
        reason = "独立 UI 素材，由 JSON bbox 和 scale_mode 回贴"
        if asset["forbid_text"]:
            reason += "，禁止烘焙动态文字"
        lines.append(f"| {asset['id']} | {asset['role']} | {asset['output']} | {asset['strategy']} | {reason} |")
    for layer in text_nodes:
        lines.append(f"| {layer['id']} | {layer['role']} | 不生成 PNG | text_node | 动态文字保持可编辑：{layer['text']} |")

    lines.extend(
        [
            "",
            "## 需要人工确认",
            "",
            "| id | 类型 | 推荐选项 | 需要确认的原因 |",
            "|---|---|---|---|",
            "| title_logo | fixed_art_text / text_node | 当前按 fixed_art_text | 标题是否需要本地化会影响是否图片化 |",
            "| main_panel_bg_composite | visual_reference_only | 如需保留仅作 reference_only | whole `main_panel_bg` 已验证会烘焙标题牌和花叶，不能作为工程 sprite |",
            "| discount_badge_bg | baked ribbon / split decoration | 当前按 reusable badge bg | 折扣样式是否所有商品共用需要确认 |",
            "| production_board | full_effect + asset_sheet | 推荐用于真实生图小实验 | 可降低但不能消除整图和单图 variant mismatch |",
            "",
            "## 尺寸与位置规则",
            "",
            "- `ui_spec.json` / `layer_ir.json` 是尺寸、位置、层级的来源。",
            "- 主面板默认拆为 `panel_base` + `panel_top_title_plate` + `panel_corner_flowers` + `panel_bottom_leaves` + `panel_inner_texture`。",
            "- `assets_png` 是可复用源素材，不能把自然尺寸当工程尺寸。",
            "- `assets_fit_raw` 是每个 layer 的 bbox 实例，重建时引用它。",
            "- 真实生成后必须输出 reconstruction / comparison 再判断是否推广。",
        ]
    )
    return "\n".join(lines)


def _build_validation_report(
    plan: dict[str, Any],
    errors: list[str],
    warnings: list[str],
    sprite_manifest: dict[str, Any],
) -> str:
    image_layer_count = sum(1 for layer in plan["layers"] if layer["type"] == "image")
    text_layer_count = sum(1 for layer in plan["layers"] if layer["type"] == "text")
    reuse_assets = [
        asset for asset in sprite_manifest["assets"] if len(asset["layers"]) > 1
    ]
    lines = [
        "# Spec Validation Report",
        "",
        "## Summary",
        "",
        f"- Screen: `{plan['screen_name']}`",
        f"- Canvas: {plan['canvas']['width']}x{plan['canvas']['height']}",
        f"- Layers: {len(plan['layers'])}",
        f"- Image layers: {image_layer_count}",
        f"- Text nodes: {text_layer_count}",
        f"- Reusable assets: {len(sprite_manifest['assets'])}",
        f"- Assets reused by multiple layers: {len(reuse_assets)}",
        f"- Validation errors: {len(errors)}",
        f"- Validation warnings: {len(warnings)}",
        "",
        "## Contract Check",
        "",
        "- JSON is the layout source of truth.",
        "- Dynamic text is represented as Text Node layers.",
        "- Sprite source assets and fitted layout instances are separated.",
        "- Stretchable backgrounds carry `scale_mode` metadata.",
        "- Main panel backgrounds are split into base, title plate, decorations, and inner texture instead of a single `main_panel_bg` sprite.",
        "- Prompts explicitly forbid rectangular crop semantics.",
        "",
        "## Errors",
    ]
    if errors:
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append("- None")

    lines.extend(["", "## Warnings"])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("- None")

    lines.extend(["", "## Reuse Map"])
    if reuse_assets:
        for asset in reuse_assets:
            layers = ", ".join(layer["layer_id"] for layer in asset["layers"])
            lines.append(f"- `{asset['id']}` -> {layers}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Validation Result",
            "",
            "This validates the spec contract and artifact graph only. The next test should generate one production board or 1-2 representative assets, then compare the reconstruction against the full effect.",
        ]
    )
    return "\n".join(lines)
