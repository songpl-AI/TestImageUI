from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from PIL import Image

from src.assets.pipeline import generate_direct_assets, generate_regenerated_assets
from src.assets.regen_tasks import export_regenerate_tasks
from src.exporters.layout_ir import build_layout_ir, save_layout_ir
from src.ir.layer_ir import load_layer_ir, validate_layer_ir
from src.reconstruction.renderer import build_comparison, reconstruct
from src.report.markdown_report import build_report


def main() -> int:
    parser = argparse.ArgumentParser(description="AI UI split pipeline MVP")
    parser.add_argument("--input", required=True, type=Path, help="source UI effect image")
    parser.add_argument("--layer-ir", required=True, type=Path, help="Layer IR JSON")
    parser.add_argument("--output", required=True, type=Path, help="output directory")
    parser.add_argument(
        "--mode",
        default="full",
        choices=["validate", "direct", "regenerate", "prepare-regenerate", "rebuild", "full"],
        help="pipeline mode",
    )
    args = parser.parse_args()

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
