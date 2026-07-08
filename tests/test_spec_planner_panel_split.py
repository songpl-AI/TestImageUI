from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from src.spec.planner import export_spec_plan


REPO_ROOT = Path(__file__).resolve().parents[1]
SHOP_BRIEF_PATH = REPO_ROOT / "examples" / "input" / "spec_driven_shop_request.json"
REQUIRED_PANEL_ASSETS = {
    "panel_base",
    "panel_top_title_plate",
    "panel_corner_flowers",
    "panel_bottom_leaves",
    "panel_inner_texture",
}


class SpecPlannerPanelSplitTest(unittest.TestCase):
    def test_shop_planner_splits_main_panel_by_default(self) -> None:
        with tempfile.TemporaryDirectory(prefix="spec_planner_panel_split_") as tmp:
            result = export_spec_plan(SHOP_BRIEF_PATH, Path(tmp))

            plan = json.loads(result.ui_spec_path.read_text(encoding="utf-8"))
            layer_ir = json.loads(result.layer_ir_path.read_text(encoding="utf-8"))
            manifest = json.loads(result.sprite_manifest_path.read_text(encoding="utf-8"))
            sprite_plan = result.sprite_plan_path.read_text(encoding="utf-8")
            production_board_prompt = result.production_board_prompt_path.read_text(encoding="utf-8")

            image_layers = [layer for layer in plan["layers"] if layer["type"] == "image"]
            text_layers = [layer for layer in plan["layers"] if layer["type"] == "text"]
            image_layer_ids = {layer["id"] for layer in image_layers}
            image_asset_ids = {layer["asset_id"] for layer in image_layers}
            manifest_assets = {asset["id"]: asset for asset in manifest["assets"]}
            layer_ir_items = {layer["id"]: layer for layer in layer_ir["layers"]}

            self.assertEqual(result.validation_errors, [])
            self.assertNotIn("main_panel_bg", image_layer_ids)
            self.assertNotIn("main_panel_bg", image_asset_ids)
            self.assertNotIn("main_panel_bg", manifest_assets)
            self.assertFalse(any("main_panel_bg must not be emitted" in warning for warning in result.validation_warnings))

            self.assertTrue(REQUIRED_PANEL_ASSETS <= image_asset_ids)
            self.assertTrue(REQUIRED_PANEL_ASSETS <= set(manifest_assets))
            self.assertTrue(REQUIRED_PANEL_ASSETS <= set(layer_ir_items))

            panel_base = manifest_assets["panel_base"]
            self.assertEqual(panel_base["role"], "panel_base_clean_candidate")
            self.assertEqual(panel_base["scale_mode"], "nine_slice")
            self.assertTrue(panel_base["nine_slice_candidate"])
            self.assertTrue(panel_base["forbid_text"])
            self.assertIn("no title plate", panel_base["prompt_subject"])
            self.assertIn("no flowers", panel_base["prompt_subject"])
            self.assertIn("no leaves", panel_base["prompt_subject"])

            inner_texture = manifest_assets["panel_inner_texture"]
            self.assertEqual(inner_texture["role"], "panel_inner_texture_tile")
            self.assertEqual(inner_texture["scale_mode"], "stretch")
            self.assertFalse(inner_texture["nine_slice_candidate"])
            self.assertTrue(inner_texture["forbid_text"])

            title_plate = manifest_assets["panel_top_title_plate"]
            self.assertEqual(title_plate["scale_mode"], "contain")
            self.assertTrue(title_plate["forbid_text"])

            self.assertGreater(len(text_layers), 0)
            for layer in text_layers:
                with self.subTest(text_layer=layer["id"]):
                    self.assertEqual(layer["asset_strategy"], "text_node")
                    self.assertNotIn(layer["id"], manifest_assets)
                    self.assertNotIn(layer["id"], image_asset_ids)

            self.assertIn("panel_base` + `panel_top_title_plate` + `panel_corner_flowers`", sprite_plan)
            self.assertIn("main_panel_bg_composite", sprite_plan)
            self.assertIn("reference_only", sprite_plan)
            self.assertNotIn("当前按 whole_panel + child layers", sprite_plan)
            self.assertIn("do not generate `main_panel_bg` as a combined engine sprite", production_board_prompt)


if __name__ == "__main__":
    unittest.main()
