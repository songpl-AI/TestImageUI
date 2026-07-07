# Sprite Plan

Source image: `examples/input/slg_main.png` (`1280x720`)
Reference crop: `examples/output/slg_main_fidelity_experiment/reference_crops/top_resource_strip_source_reference_crop.png`
Component bbox: `[338, 0, 914, 72]`

This is a narrow experiment for a different component type from the BUILD nav button. The source crop is only a reference / edit target. It is not a final sprite.

## 自动确认

| id | 类型 | 输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| top_resource_strip_frame | composite_hud_frame | `assets_png/top_resource_strip_frame.png` | standalone_composite_sprite | 顶部资源条布局固定，适合测试“组合控件 sprite”是否比细拆资源条更接近源图 |
| resource_labels | dynamic_text | 不生成 PNG | text_node | WOOD / FOOD / GOLD / GEMS 保持可编辑，避免烘焙文字 |
| resource_values | dynamic_text | 不生成 PNG | text_node | 2.5M / 3.2M / 4.7M / 1,250 是动态数值 |

## 需要人工确认

| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| top_resource_strip_frame | composite sprite / split bars | 本轮推荐 composite sprite | 它牺牲一部分复用性，但能验证不同类型组合控件是否也发生真实生成漂移 |

## 生成约束

- `top_resource_strip_frame` 可以包含四个固定资源 icon、四个资源条底板、四个绿色加号。
- 禁止包含任何文字、字母、数字。
- 禁止包含天空背景、地图背景、邻近 UI。
- 最终必须是透明 PNG，并 fit 回 `[338, 0, 914, 72]`。


## 实验结果

- 已生成 `assets_png/top_resource_strip_frame.png`，它是透明组合 sprite，不是源图 crop。
- 已输出 `sprite_overview.png`、`bbox_overlay.png`、`focused_top_resource_strip_comparison.png`、`full_top_resource_strip_comparison.png` 和 `experiment_manifest.json`。
- 局部平均 RGB delta：当前独立 sprite 57.61，crop proxy 0.00，realgen frame + Text Nodes 53.92。
- UI mask delta：当前独立 sprite 60.78，realgen frame + Text Nodes 58.34。
- 结论：生成产物符合无文字透明 sprite 约束，但 spacing、条宽、icon 比例和 plus button 细节明显被重新排版/重画，未接近 crop proxy 上限。
