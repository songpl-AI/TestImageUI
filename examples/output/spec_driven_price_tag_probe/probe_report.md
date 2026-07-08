# Price Tag Background Probe

## Result

The probe passes the minimum engineering check for `price_tag_bg` as a transparent source sprite and focused reconstruction.

- `price_tag_bg` is RGBA with transparent corners and no baked price.
- Dynamic price remains a Text Node from spec: `$3`.
- `stretch` is recommended for this tag instance because the generated cell is much wider than the target bbox.

## Caveats

- The generated full-effect board shows different prices (`$1.99`, `$3.99`, `$4.99`) from the spec (`$3`, `$6`, `$9`), so visual delta is diagnostic only.
- One corner is semi-transparent (`alpha=46`) due to anti-aliasing from the extracted cell edge. This is acceptable for the probe, but production should use a cleaner matte.
- A production pass should replace the approximate Text Node font/stroke with calibrated font metadata.

## Metrics

```json
{
  "target_bbox": [
    104,
    65
  ],
  "source_cell_size": [
    256,
    83
  ],
  "full_crop_size": [
    152,
    62
  ],
  "sprite_natural_size": [
    233,
    67
  ],
  "foreground_bbox_in_source_cell": [
    0,
    0,
    233,
    67
  ],
  "background_estimate_rgb": [
    251,
    247,
    240
  ],
  "text_bbox_relative_to_price_tag": [
    17,
    11,
    70,
    39
  ],
  "text_value_from_spec": "$3",
  "alpha_validation": {
    "mode": "RGBA",
    "corner_alpha": [
      46,
      0,
      0,
      0
    ],
    "transparent_pixels": 1312,
    "opaque_pixels": 13690,
    "semi_transparent_pixels": 609,
    "transparent_ratio": 0.084
  },
  "mean_abs_delta_vs_full_scaled": {
    "contain_text": 65.62,
    "stretch_text": 44.89
  }
}
```
