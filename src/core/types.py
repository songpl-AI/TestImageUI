from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


AssetStrategy = Literal[
    "direct_crop",
    "segmentation_extract",
    "regenerate",
    "regenerate_or_inpaint",
    "inpaint_background",
    "text_node",
    "vector_shape",
    "ignore",
]

VALID_ASSET_STRATEGIES: set[str] = {
    "direct_crop",
    "segmentation_extract",
    "regenerate",
    "regenerate_or_inpaint",
    "inpaint_background",
    "text_node",
    "vector_shape",
    "ignore",
}


@dataclass(frozen=True)
class BBox:
    x: int
    y: int
    width: int
    height: int

    @classmethod
    def from_json(cls, value: list[int]) -> "BBox":
        if not isinstance(value, list) or len(value) != 4:
            raise ValueError("bbox must be [x, y, width, height]")
        x, y, width, height = value
        return cls(int(x), int(y), int(width), int(height))

    def as_list(self) -> list[int]:
        return [self.x, self.y, self.width, self.height]

    @property
    def right(self) -> int:
        return self.x + self.width

    @property
    def bottom(self) -> int:
        return self.y + self.height


@dataclass
class LayerItem:
    id: str
    role: str
    bbox: BBox
    asset_strategy: AssetStrategy
    output: str | None = None
    transparent: bool = True
    text: str | None = None
    remove_text: bool = False
    remove_occluding_children: bool = False
    nine_slice_candidate: bool = False
    children_hint: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_json(cls, value: dict[str, Any]) -> "LayerItem":
        strategy = value.get("asset_strategy")
        if strategy not in VALID_ASSET_STRATEGIES:
            raise ValueError(f"invalid asset_strategy for layer {value.get('id')}: {strategy}")

        return cls(
            id=str(value["id"]),
            role=str(value["role"]),
            bbox=BBox.from_json(value["bbox"]),
            asset_strategy=strategy,
            output=value.get("output"),
            transparent=bool(value.get("transparent", True)),
            text=value.get("text"),
            remove_text=bool(value.get("remove_text", False)),
            remove_occluding_children=bool(value.get("remove_occluding_children", False)),
            nine_slice_candidate=bool(value.get("nine_slice_candidate", False)),
            children_hint=list(value.get("children_hint", [])),
            metadata=dict(value.get("metadata", {})),
        )


@dataclass
class LayerIR:
    version: str
    canvas_width: int
    canvas_height: int
    source_image: str
    layers: list[LayerItem]

