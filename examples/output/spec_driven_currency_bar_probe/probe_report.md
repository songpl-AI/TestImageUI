# Currency Bar Background Probe

## Result

The probe is a **partial pass** for `currency_bar_bg`.

- `currency_bar_bg` is RGBA and no longer contains the baked number.
- `coin_icon` is kept as a separate source sprite and fitted into its own bbox.
- Dynamic amount remains a Text Node from spec: `3200`.
- `stretch` is better than `contain` for the bar background because this is a horizontally scalable capsule.

## Caveats

- One corner of `currency_bar_bg` is still opaque because the generated leaf decoration touches the asset-cell crop edge. This is not a rectangular-background failure, but it means the source sprite has poor natural padding.
- The generated full-effect board shows a different currency amount (`1,250`) and an extra plus button not present in this spec, so visual delta is diagnostic only.
- The asset-sheet bar includes leaf decorations at the ends. That decoration ownership must be accepted or split before production.

## Metrics

```json
{
  "target_bbox": [
    202,
    70
  ],
  "source_cell_size": [
    267,
    86
  ],
  "coin_source_cell_size": [
    138,
    143
  ],
  "full_crop_size": [
    256,
    72
  ],
  "sprite_natural_size": [
    260,
    86
  ],
  "coin_sprite_natural_size": [
    131,
    135
  ],
  "foreground_bbox_in_source_cell": [
    0,
    0,
    260,
    86
  ],
  "coin_foreground_bbox_in_source_cell": [
    0,
    0,
    131,
    135
  ],
  "coin_bbox_relative_to_bar": [
    11,
    8,
    32,
    32
  ],
  "text_bbox_relative_to_bar": [
    51,
    8,
    108,
    51
  ],
  "text_value_from_spec": "3200",
  "alpha_validation": {
    "currency_bar_bg": {
      "mode": "RGBA",
      "corner_alpha": [
        0,
        0,
        255,
        0
      ],
      "transparent_ratio": 0.0875
    },
    "coin_icon": {
      "mode": "RGBA",
      "corner_alpha": [
        0,
        0,
        0,
        0
      ],
      "transparent_ratio": 0.1828
    }
  },
  "mean_abs_delta_vs_full_scaled": {
    "contain_icon_text": 58.23,
    "stretch_icon_text": 54.54
  }
}
```

