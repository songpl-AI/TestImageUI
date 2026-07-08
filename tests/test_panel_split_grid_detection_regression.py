from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.spec.layer_contract import export_layer_contract_validation


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "panel_split_no_label"
RUNS = ("run_01", "run_02", "run_03")


def _check_fixtures() -> None:
    missing: list[Path] = []
    for run in RUNS:
        run_dir = FIXTURE_ROOT / run
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
                    run_dir = FIXTURE_ROOT / run
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


if __name__ == "__main__":
    unittest.main()
