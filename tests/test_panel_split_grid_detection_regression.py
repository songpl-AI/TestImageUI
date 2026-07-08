from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw

from src.spec.layer_contract import export_layer_contract_validation


REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL_FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "panel_split_no_label"
PRODUCT_CARD_FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "product_card_grid_detection"
CURRENCY_BAR_FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "currency_bar_grid_detection"
RUNS = ("run_01", "run_02", "run_03")


def _check_fixtures() -> None:
    missing: list[Path] = []
    for run in RUNS:
        run_dir = PANEL_FIXTURE_ROOT / run
        for name in ("production_board.png", "layer_contract_fixed_bbox.json", "layer_contract_auto_detect.json"):
            path = run_dir / name
            if not path.exists():
                missing.append(path)
    if missing:
        joined = "\n".join(str(path.relative_to(REPO_ROOT)) for path in missing)
        raise unittest.SkipTest(f"panel split no-label regression fixtures are missing:\n{joined}")


def _failed_checks(metrics: dict) -> list[str]:
    checks = metrics.get("contract_checks") or {}
    return [
        key
        for key, value in checks.items()
        if isinstance(value, dict) and "pass" in value and not bool(value["pass"])
    ]


class PanelSplitGridDetectionRegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _check_fixtures()

    def test_grid_cell_auto_detection_replaces_asset_specific_hint(self) -> None:
        with tempfile.TemporaryDirectory(prefix="panel_split_grid_regression_") as tmp:
            output_root = Path(tmp)

            for run in RUNS:
                with self.subTest(run=run):
                    run_dir = PANEL_FIXTURE_ROOT / run
                    fixed_result = export_layer_contract_validation(
                        run_dir / "layer_contract_fixed_bbox.json",
                        output_root / run / "fixed_bbox",
                    )
                    auto_result = export_layer_contract_validation(
                        run_dir / "layer_contract_auto_detect.json",
                        output_root / run / "auto_detect",
                    )

                    fixed_metrics = json.loads(fixed_result.probe_metrics_path.read_text(encoding="utf-8"))
                    auto_metrics = json.loads(auto_result.probe_metrics_path.read_text(encoding="utf-8"))
                    auto_input_contract = json.loads((run_dir / "layer_contract_auto_detect.json").read_text(encoding="utf-8"))

                    self.assertGreater(len(fixed_result.failed_checks), 0)
                    self.assertEqual(_failed_checks(fixed_metrics), fixed_result.failed_checks)
                    self.assertEqual(auto_result.validation_errors, [])
                    self.assertEqual(auto_result.failed_checks, [])
                    self.assertEqual(_failed_checks(auto_metrics), [])

                    for cell in auto_input_contract["asset_cells"]:
                        self.assertNotIn("bbox_detection_hint", cell)

                    detection = auto_metrics["asset_sheet_detection"]
                    self.assertEqual(detection["mode"], "grid_cell_foreground_safe_bbox")
                    self.assertIn("grid_cell_detection", detection)
                    self.assertIn("grid_cell_search", detection["cells"]["panel_inner_texture"])

                    for asset_id, asset_metrics in auto_metrics["asset_cells"].items():
                        with self.subTest(run=run, asset_id=asset_id):
                            self.assertEqual(asset_metrics["artifact_audit"]["label_artifact_score"], 0)

                    panel_base = auto_metrics["asset_cells"]["panel_base"]
                    inner_texture = auto_metrics["asset_cells"]["panel_inner_texture"]
                    self.assertLessEqual(panel_base["color_audit_on_opaque_pixels"]["green_ratio"], 0.02)
                    self.assertEqual(panel_base["alpha_validation"]["corner_alpha_max"], 0)
                    self.assertLessEqual(inner_texture["color_audit_on_opaque_pixels"]["green_ratio"], 0.02)
                    self.assertEqual(inner_texture["alpha_validation"]["corner_alpha_max"], 0)


class ProductCardGridDetectionRegressionTest(unittest.TestCase):
    def test_compact_price_tag_does_not_expand_to_full_cell_height(self) -> None:
        run_dir = PRODUCT_CARD_FIXTURE_ROOT / "run_02"
        board_path = run_dir / "production_board.png"
        contract_path = run_dir / "layer_contract_auto_detect.json"
        missing = [path for path in (board_path, contract_path) if not path.exists()]
        if missing:
            joined = "\n".join(str(path.relative_to(REPO_ROOT)) for path in missing)
            raise unittest.SkipTest(f"product card grid detection fixtures are missing:\n{joined}")

        with tempfile.TemporaryDirectory(prefix="product_card_grid_regression_") as tmp:
            output_root = Path(tmp)
            grid_contract = json.loads(contract_path.read_text(encoding="utf-8"))
            grid_contract["board_image"] = str(board_path)
            grid_contract.setdefault("asset_sheet_detection", {})["enabled"] = True
            grid_contract["asset_sheet_detection"]["mode"] = "grid_cell_foreground_safe_bbox"
            grid_contract_path = output_root / "layer_contract_grid_detect.json"
            grid_contract_path.write_text(json.dumps(grid_contract, indent=2) + "\n", encoding="utf-8")

            result = export_layer_contract_validation(grid_contract_path, output_root / "validation_grid_detect")
            metrics = json.loads(result.probe_metrics_path.read_text(encoding="utf-8"))

            self.assertEqual(result.validation_errors, [])
            self.assertEqual(result.failed_checks, [])
            self.assertEqual(_failed_checks(metrics), [])

            detection = metrics["asset_sheet_detection"]
            self.assertEqual(detection["mode"], "grid_cell_foreground_safe_bbox")
            price_detection = detection["cells"]["price_tag_bg"]
            original_height = price_detection["original_bbox"][3]
            detected_y = price_detection["detected_bbox"][1]
            detected_height = price_detection["detected_bbox"][3]
            original_y = price_detection["original_bbox"][1]

            self.assertGreater(detected_y, original_y + 50)
            self.assertLess(detected_height, original_height * 0.65)

            guards = price_detection["edge_padding_guards"]
            self.assertTrue(guards["vertical_strip_dropped"])
            self.assertFalse(guards["vertical_extent_preserved"])

            price_metrics = metrics["asset_cells"]["price_tag_bg"]
            self.assertLess(price_metrics["asset_png_size"][1], original_height * 0.65)
            self.assertGreaterEqual(price_metrics["color_audit_on_opaque_pixels"]["gold_ratio"], 0.35)


class CurrencyBarGridDetectionRegressionTest(unittest.TestCase):
    def test_currency_bar_contract_keeps_bg_tight_and_text_free(self) -> None:
        board_path = CURRENCY_BAR_FIXTURE_ROOT / "production_board.png"
        contract_path = CURRENCY_BAR_FIXTURE_ROOT / "layer_contract_grid_detect.json"
        missing = [path for path in (board_path, contract_path) if not path.exists()]
        if missing:
            joined = "\n".join(str(path.relative_to(REPO_ROOT)) for path in missing)
            raise unittest.SkipTest(f"currency bar grid detection fixtures are missing:\n{joined}")

        with tempfile.TemporaryDirectory(prefix="currency_bar_grid_regression_") as tmp:
            output_root = Path(tmp)
            result = export_layer_contract_validation(contract_path, output_root / "validation_grid_detect")
            metrics = json.loads(result.probe_metrics_path.read_text(encoding="utf-8"))

            self.assertEqual(result.validation_errors, [])
            self.assertEqual(result.failed_checks, [])
            self.assertEqual(_failed_checks(metrics), [])

            detection = metrics["asset_sheet_detection"]
            self.assertEqual(detection["mode"], "grid_cell_foreground_safe_bbox")
            currency_detection = detection["cells"]["currency_bar_bg"]
            original_width = currency_detection["original_bbox"][2]
            original_height = currency_detection["original_bbox"][3]
            detected_width = currency_detection["detected_bbox"][2]
            detected_height = currency_detection["detected_bbox"][3]

            self.assertLess(detected_width, original_width)
            self.assertLess(detected_height, original_height * 0.85)
            self.assertFalse(currency_detection["edge_padding_guards"]["vertical_extent_preserved"])
            self.assertFalse(currency_detection["edge_padding_guards"]["horizontal_extent_preserved"])

            currency_metrics = metrics["asset_cells"]["currency_bar_bg"]
            self.assertEqual(currency_metrics["alpha_validation"]["corner_alpha_max"], 0)
            self.assertGreaterEqual(currency_metrics["color_audit_on_opaque_pixels"]["green_ratio"], 0.35)
            self.assertGreaterEqual(currency_metrics["color_audit_on_opaque_pixels"]["gold_ratio"], 0.08)
            self.assertLessEqual(currency_metrics["color_audit_on_opaque_pixels"]["dark_text_like_ratio"], 0.05)
            self.assertEqual(currency_metrics["artifact_audit"]["label_artifact_score"], 0)

            coin_metrics = metrics["asset_cells"]["coin_icon"]
            self.assertEqual(coin_metrics["alpha_validation"]["corner_alpha_max"], 0)
            self.assertGreaterEqual(coin_metrics["color_audit_on_opaque_pixels"]["gold_ratio"], 0.35)


class DecorationGroupBboxDetectionRegressionTest(unittest.TestCase):
    def test_disconnected_decoration_components_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="decoration_group_bbox_regression_") as tmp:
            output_root = Path(tmp)
            board_path = output_root / "board.png"
            contract_path = output_root / "contract.json"

            board = Image.new("RGB", (312, 219), (245, 242, 239))
            draw = ImageDraw.Draw(board)
            draw.rectangle((0, 70, 1, 218), fill=(88, 150, 30))

            for cx in (86, 276):
                draw.ellipse((cx - 38, 48, cx + 38, 108), fill=(238, 239, 210), outline=(72, 137, 34), width=4)
                draw.ellipse((cx - 22, 34, cx + 20, 88), fill=(95, 167, 40))
                draw.ellipse((cx - 30, 75, cx + 28, 132), fill=(103, 177, 47))
                draw.ellipse((cx - 14, 66, cx + 14, 94), fill=(234, 178, 38))

            board.save(board_path)
            contract = {
                "version": "0.1",
                "contract_id": "decoration_group_bbox_regression",
                "primary_asset_id": "panel_corner_flowers",
                "board_image": "board.png",
                "canvas": {"width": 312, "height": 219},
                "asset_cells": [
                    {
                        "id": "panel_corner_flowers",
                        "role": "panel_corner_flowers",
                        "bbox": [0, 0, 312, 219],
                        "transparent": True,
                        "forbid_text": True,
                        "scale_mode": "contain",
                    }
                ],
                "validation_checks": [],
                "asset_sheet_detection": {
                    "enabled": True,
                    "mode": "foreground_safe_bbox",
                    "padding": 8,
                    "threshold": 55,
                    "min_component_area": 120,
                    "drop_border_artifacts": True,
                },
            }
            contract_path.write_text(json.dumps(contract, indent=2) + "\n", encoding="utf-8")

            result = export_layer_contract_validation(contract_path, output_root / "validation")
            metrics = json.loads(result.probe_metrics_path.read_text(encoding="utf-8"))
            detection = metrics["asset_sheet_detection"]["cells"]["panel_corner_flowers"]
            detected_bbox = detection["detected_bbox"]
            detected_right = detected_bbox[0] + detected_bbox[2]

            self.assertEqual(result.validation_errors, [])
            self.assertEqual(result.failed_checks, [])
            self.assertTrue(detection["preserve_disconnected_components"])
            self.assertGreaterEqual(detection["kept_component_count"], 2)
            self.assertLessEqual(detected_bbox[0], 45)
            self.assertGreaterEqual(detected_right, 304)


if __name__ == "__main__":
    unittest.main()
