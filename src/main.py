from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from src.spec.layer_contract import export_layer_contract_validation
from src.spec.planner import export_spec_plan


def main() -> int:
    parser = argparse.ArgumentParser(description="AI UI split pipeline MVP")
    parser.add_argument("--input", type=Path, help="source UI effect image")
    parser.add_argument("--layer-ir", type=Path, help="Layer IR JSON")
    parser.add_argument("--brief", type=Path, help="natural-language generation brief JSON")
    parser.add_argument("--contract", type=Path, help="spec-driven layer contract JSON")
    parser.add_argument("--output", required=True, type=Path, help="output directory")
    parser.add_argument(
        "--mode",
        default="full",
        choices=[
            "plan-spec",
            "validate-contract",
            "validate",
            "direct",
            "regenerate",
            "prepare-regenerate",
            "rebuild",
            "full",
        ],
        help="pipeline mode",
    )
    args = parser.parse_args()

    if args.mode == "plan-spec":
        if not args.brief:
            parser.error("--brief is required when --mode plan-spec")
        result = export_spec_plan(args.brief, args.output)
        print(f"Wrote {result.ui_spec_path}")
        print(f"Wrote {result.layer_ir_path}")
        print(f"Wrote {result.layout_ir_path}")
        print(f"Wrote {result.sprite_manifest_path}")
        print(f"Wrote {result.full_effect_prompt_path}")
        print(f"Wrote {result.production_board_prompt_path}")
        print(f"Wrote {result.production_board_panel_focus_prompt_path}")
        print(f"Wrote {result.panel_focus_layer_contract_path}")
        print(f"Wrote {result.sprite_plan_path}")
        print(f"Wrote {result.validation_report_path}")
        print(f"Asset prompts: {result.asset_prompt_count}")
        if result.validation_errors:
            print("Spec validation failed:")
            for error in result.validation_errors:
                print(f"- {error}")
            return 1
        if result.validation_warnings:
            print("Spec validation warnings:")
            for warning in result.validation_warnings:
                print(f"- {warning}")
        return 0

    if args.mode == "validate-contract":
        if not args.contract:
            parser.error("--contract is required when --mode validate-contract")
        result = export_layer_contract_validation(args.contract, args.output)
        print(f"Wrote {result.copied_board_path}")
        print(f"Wrote {result.layer_ir_path}")
        print(f"Wrote {result.layout_ir_path}")
        print(f"Wrote {result.sprite_manifest_path}")
        print(f"Wrote {result.probe_metrics_path}")
        print(f"Wrote {result.probe_report_path}")
        print(f"Assets: {result.asset_count}")
        if result.validation_errors:
            print("Layer contract IR validation failed:")
            for error in result.validation_errors:
                print(f"- {error}")
            return 1
        if result.failed_checks:
            print("Layer contract checks failed:")
            for check in result.failed_checks:
                print(f"- {check}")
            return 1
        return 0

    if not args.input:
        parser.error("--input is required unless --mode plan-spec or --mode validate-contract")
    if not args.layer_ir:
        parser.error("--layer-ir is required unless --mode plan-spec or --mode validate-contract")

    from PIL import Image

    from src.assets.pipeline import generate_direct_assets, generate_regenerated_assets
    from src.assets.regen_tasks import export_regenerate_tasks
    from src.exporters.layout_ir import build_layout_ir, save_layout_ir
    from src.ir.layer_ir import load_layer_ir, validate_layer_ir
    from src.reconstruction.renderer import build_comparison, reconstruct
    from src.report.markdown_report import build_report

    source_image = Image.open(args.input).convert("RGBA")
    layer_ir = load_layer_ir(args.layer_ir)
    errors = validate_layer_ir(layer_ir, source_image.size)
    if errors:
        print("Layer IR validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    if args.mode == "validate":
        print("Layer IR validation passed.")
        return 0

    output_dir: Path = args.output
    output_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(args.input, output_dir / "original.png")

    direct_dir = output_dir / "assets_direct"
    regenerated_dir = output_dir / "assets_regenerated"

    if args.mode in {"direct", "prepare-regenerate", "full"}:
        direct_assets = generate_direct_assets(source_image, layer_ir, direct_dir)
        direct_rebuild = reconstruct(
            layer_ir,
            direct_dir,
            output_dir / "reconstruction_direct.png",
            draw_text=False,
            strict_assets=True,
        )
        print(f"Generated direct assets: {len(direct_assets)}")
        print(f"Wrote {direct_rebuild}")

    if args.mode == "prepare-regenerate":
        tasks, passthrough_assets = export_regenerate_tasks(source_image, layer_ir, output_dir, source_image_path=args.input)
        layout_path = save_layout_ir(build_layout_ir(layer_ir), output_dir / "layout_ir.pending.json")
        report_path = build_report(layer_ir, output_dir / "report.md")
        print(f"Exported Codex regenerate tasks: {len(tasks)}")
        print(f"Prepared passthrough assets: {len(passthrough_assets)}")
        print(f"Wrote {output_dir / 'regen_tasks_manifest.md'}")
        print(f"Wrote {layout_path}")
        print(f"Wrote {report_path}")
        return 0

    if args.mode in {"regenerate", "full"}:
        regenerated_assets = generate_regenerated_assets(source_image, layer_ir, regenerated_dir)
        regenerated_rebuild = reconstruct(
            layer_ir,
            regenerated_dir,
            output_dir / "reconstruction_regenerated.png",
            draw_text=True,
            strict_assets=True,
        )
        print(f"Generated regenerated assets: {len(regenerated_assets)}")
        print(f"Wrote {regenerated_rebuild}")

    if args.mode == "rebuild":
        try:
            direct_rebuild = reconstruct(
                layer_ir,
                direct_dir,
                output_dir / "reconstruction_direct.png",
                draw_text=False,
                strict_assets=True,
            )
            regenerated_rebuild = reconstruct(
                layer_ir,
                regenerated_dir,
                output_dir / "reconstruction_regenerated.png",
                draw_text=True,
                strict_assets=True,
            )
        except ValueError as exc:
            print(str(exc))
            return 1
        print(f"Wrote {direct_rebuild}")
        print(f"Wrote {regenerated_rebuild}")

    if args.mode in {"full", "rebuild"}:
        comparison = build_comparison(
            args.input,
            output_dir / "reconstruction_direct.png",
            output_dir / "reconstruction_regenerated.png",
            output_dir / "comparison.png",
        )
        layout_path = save_layout_ir(build_layout_ir(layer_ir), output_dir / "layout_ir.json")
        report_path = build_report(layer_ir, output_dir / "report.md")
        print(f"Wrote {comparison}")
        print(f"Wrote {layout_path}")
        print(f"Wrote {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
