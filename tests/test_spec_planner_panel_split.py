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
PANEL_FOCUS_IDS = [
    "panel_base",
    "panel_top_title_plate",
    "panel_corner_flowers",
    "panel_bottom_leaves",
    "panel_inner_texture",
    "full_panel_composite_reference",
]


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

    def test_shop_planner_exports_panel_focus_prompt_and_contract(self) -> None:
        with tempfile.TemporaryDirectory(prefix="spec_planner_panel_focus_") as tmp:
            result = export_spec_plan(SHOP_BRIEF_PATH, Path(tmp))

            prompt = result.production_board_panel_focus_prompt_path.read_text(encoding="utf-8")
            contract = json.loads(result.panel_focus_layer_contract_path.read_text(encoding="utf-8"))

            self.assertTrue(result.production_board_panel_focus_prompt_path.exists())
            self.assertTrue(result.panel_focus_layer_contract_path.exists())

            self.assertIn("1536x1024", prompt)
            self.assertIn("2-column by 3-row grid", prompt)
            self.assertIn("fit fully inside its own cell with a clear neutral margin", prompt)
            self.assertIn("panel_base cell especially needs empty neutral padding", prompt)
            self.assertIn("no visible cell labels, no numbers, no index markers", prompt)
            self.assertIn("Cell order is implicit by grid position only", prompt)
            self.assertIn("panel_base: only the large cream rounded panel body", prompt)
            self.assertIn("It must NOT include top title plate, flowers, leaves", prompt)
            for asset_id in PANEL_FOCUS_IDS:
                self.assertIn(asset_id, prompt)

            self.assertNotIn("main_panel_bg", prompt)
            for non_panel_asset_id in ("background_scene", "product_card_bg", "currency_bar_bg", "price_tag_bg"):
                self.assertNotIn(non_panel_asset_id, prompt)

            self.assertEqual(contract["primary_asset_id"], "panel_base")
            self.assertEqual(contract["board_image"], "production_board.png")
            self.assertEqual(contract["canvas"], {"width": 1536, "height": 1024})
            self.assertEqual(contract["split_x"], 738)
            self.assertEqual(
                contract["asset_sheet_detection"],
                {
                    "enabled": True,
                    "mode": "grid_cell_foreground_safe_bbox",
                    "padding": 22,
                    "threshold": 55,
                    "min_component_area": 120,
                    "drop_border_artifacts": True,
                },
            )

            cells = {cell["id"]: cell for cell in contract["asset_cells"]}
            self.assertEqual([cell["id"] for cell in contract["asset_cells"]], PANEL_FOCUS_IDS)
            self.assertNotIn("main_panel_bg", cells)

            panel_base = cells["panel_base"]
            self.assertEqual(panel_base["role"], "panel_base_clean_candidate")
            self.assertEqual(panel_base["bbox"], [759, 28, 405, 365])
            self.assertEqual(panel_base["scale_mode"], "nine_slice")
            self.assertTrue(panel_base["nine_slice_candidate"])
            self.assertEqual(
                panel_base["children_excluded"],
                [
                    "panel_top_title_plate",
                    "panel_corner_flowers",
                    "panel_bottom_leaves",
                    "title_text",
                    "cards",
                    "buttons",
                ],
            )

            self.assertTrue(cells["panel_corner_flowers"]["preserve_disconnected_components"])
            self.assertTrue(cells["panel_bottom_leaves"]["preserve_disconnected_components"])
            self.assertEqual(cells["full_panel_composite_reference"]["scale_mode"], "reference_only")
            self.assertTrue(cells["full_panel_composite_reference"]["validation_only"])

            check_ids = {check["id"] for check in contract["validation_checks"]}
            self.assertIn("panel_base_has_no_label_artifact", check_ids)
            self.assertIn("inner_texture_has_clean_corners", check_ids)
            self.assertIn("composite_reference_has_no_label_artifact", check_ids)
            self.assertIn("not final engine-ready sprites", contract["interpretation"])


if __name__ == "__main__":
    unittest.main()
