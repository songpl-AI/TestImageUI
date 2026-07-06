from __future__ import annotations

from pathlib import Path

from PIL import Image

from src.assets.generators import DirectCropGenerator, MockRegenerateGenerator
from src.core.types import LayerIR


def generate_direct_assets(source_image: Image.Image, layer_ir: LayerIR, output_dir: Path) -> dict[str, str]:
    generator = DirectCropGenerator()
    outputs: dict[str, str] = {}
    for layer in layer_ir.layers:
        path = generator.generate(source_image, layer, output_dir)
        if path:
            outputs[layer.id] = str(path)
    return outputs


def generate_regenerated_assets(source_image: Image.Image, layer_ir: LayerIR, output_dir: Path) -> dict[str, str]:
    generator = MockRegenerateGenerator()
    outputs: dict[str, str] = {}
    for layer in layer_ir.layers:
        path = generator.generate(source_image, layer, output_dir)
        if path:
            outputs[layer.id] = str(path)
    return outputs
