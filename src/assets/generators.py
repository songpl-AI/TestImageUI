from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from src.core.types import LayerItem


class DirectCropGenerator:
    def generate(self, source_image: Image.Image, layer: LayerItem, output_dir: Path) -> Path | None:
        if layer.asset_strategy == "ignore":
            return None

        output_dir.mkdir(parents=True, exist_ok=True)
        crop = source_image.crop((layer.bbox.x, layer.bbox.y, layer.bbox.right, layer.bbox.bottom))
        output = output_dir / f"{layer.id}.png"
        crop.save(output)
        return output


class MockRegenerateGenerator:
    def generate(self, source_image: Image.Image, layer: LayerItem, output_dir: Path) -> Path | None:
        if layer.asset_strategy in {"ignore", "text_node"}:
            return None

        output_dir.mkdir(parents=True, exist_ok=True)
        output = output_dir / f"{layer.id}.png"

        if layer.asset_strategy in {"direct_crop", "segmentation_extract"}:
            crop = source_image.crop((layer.bbox.x, layer.bbox.y, layer.bbox.right, layer.bbox.bottom))
            crop.save(output)
            return output

        image = self._placeholder_for(layer)
        image.save(output)
        return output

    def _placeholder_for(self, layer: LayerItem) -> Image.Image:
        width, height = layer.bbox.width, layer.bbox.height
        role = layer.role.lower()
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        if "screen_background" in role:
            self._draw_background(draw, width, height)
        elif "panel" in role:
            self._draw_panel(draw, width, height)
        elif "button" in role:
            self._draw_button(draw, width, height)
        elif "reward_card" in role or "card" in role:
            self._draw_card(draw, width, height)
        elif "bar" in role:
            self._draw_bar(draw, width, height)
        elif "glow" in role:
            image = self._draw_glow(width, height)
        elif "art_text" in role:
            self._draw_art_text(draw, width, height, layer.text)
        elif "title" in role:
            self._draw_title(draw, width, height, layer.text)
        else:
            self._draw_generic(draw, width, height)

        return image

    def _draw_background(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        draw.rectangle((0, 0, width, height), fill=(38, 104, 191, 255))
        for x, y, radius in [(70, 95, 38), (340, 25, 26), (585, 105, 27), (610, 970, 58)]:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(104, 161, 222, 140), width=3)

    def _draw_panel(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=34, fill=(255, 227, 130, 255), outline=(139, 80, 27, 255), width=8)
        inset = 26
        draw.rounded_rectangle((inset, 82, width - inset, height - 36), radius=24, fill=(255, 246, 194, 255), outline=(206, 145, 52, 255), width=3)

    def _draw_button(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        draw.rounded_rectangle((0, 8, width - 1, height - 1), radius=32, fill=(13, 113, 43, 255))
        draw.rounded_rectangle((8, 0, width - 9, height - 10), radius=28, fill=(48, 205, 88, 255), outline=(16, 124, 49, 255), width=5)
        draw.rounded_rectangle((22, 12, width - 22, 42), radius=18, fill=(139, 255, 146, 190))

    def _draw_card(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        draw.rounded_rectangle((0, 8, width - 1, height - 1), radius=28, fill=(75, 35, 151, 255))
        draw.rounded_rectangle((10, 0, width - 11, height - 14), radius=24, fill=(176, 133, 239, 255), outline=(93, 43, 176, 255), width=6)
        draw.rounded_rectangle((26, 18, width - 26, height - 30), radius=18, fill=(189, 150, 242, 220))

    def _draw_bar(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=28, fill=(75, 139, 229, 255), outline=(255, 238, 85, 255), width=4)

    def _draw_title(self, draw: ImageDraw.ImageDraw, width: int, height: int, text: str | None) -> None:
        draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=34, fill=(239, 65, 100, 255), outline=(255, 246, 178, 255), width=6)
        draw.rounded_rectangle((16, 14, width - 16, 47), radius=17, fill=(139, 116, 177, 210))

    def _draw_art_text(self, draw: ImageDraw.ImageDraw, width: int, height: int, text: str | None) -> None:
        label = text or ""
        font = self._load_font(max(24, min(44, height - 18)), bold=True)
        bbox = draw.textbbox((0, 0), label, font=font, stroke_width=2)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = max(0, (width - text_width) // 2)
        y = max(0, (height - text_height) // 2) - 2
        draw.text((x, y), label, fill=(255, 240, 120, 255), font=font, stroke_width=2, stroke_fill=(123, 54, 62, 255))

    def _draw_glow(self, width: int, height: int) -> Image.Image:
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        cx, cy = width // 2, height // 2
        max_radius = max(1, min(width, height) // 2)
        for radius in range(max_radius, 0, -8):
            alpha = int(70 * (1 - radius / max_radius))
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=(255, 237, 120, alpha))
        return image.filter(ImageFilter.GaussianBlur(8))

    def _draw_generic(self, draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
        draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=12, fill=(220, 220, 220, 180), outline=(120, 120, 120, 220), width=2)

    def _load_font(self, size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        candidates = [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Helvetica.ttf",
            "/Library/Fonts/Arial.ttf",
        ]
        for candidate in candidates:
            try:
                return ImageFont.truetype(candidate, size=size)
            except OSError:
                continue
        return ImageFont.load_default()
