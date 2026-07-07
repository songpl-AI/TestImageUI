# Currency Bar Probe Sprite Plan

Source:

- Full effect crop: `crops/source_heart_currency_bar_crop.png`
- Source bbox in `split/full_effect.png`: `[186, 22, 216, 78]`
- Asset sheet: `../play_button_probe/split/asset_sheet.png`

This probe validates whether the synchronized `full_effect + asset_sheet` result can reconstruct one top HUD currency bar as:

```text
top_currency_bar_bg + heart_icon + plus_button + Text Node("5")
```

## Auto Confirmed

| id | type | output | handling | reason |
|---|---|---|---|---|
| top_currency_bar_bg | currency_bar_bg | `assets_png/top_currency_bar_bg.png` | standalone sprite from asset sheet cell | Currency bar backgrounds should not contain numbers, icons, or buttons. |
| heart_icon | currency_icon | `assets_png/heart_icon.png` | standalone sprite from asset sheet cell | The heart is a reusable currency icon. |
| plus_button | button_icon | `assets_png/plus_button.png` | standalone sprite from asset sheet cell | The plus button is a reusable HUD action button. |
| heart_count_text | dynamic_text | no PNG | Text Node | The `5` is stateful/dynamic and should remain editable. |

## Needs Manual Review

| id | recommended option | why |
|---|---|---|
| top_currency_bar_bg identity | require exact dark-brown full-effect variant in future generation | The generated asset sheet cell is a cream rounded panel, while the full-effect heart bar is a dark brown capsule. |
| top_currency_bar_bg scale mode | `nine_slice` if the correct dark bar exists | `contain` and `stretch` cannot fix an asset identity mismatch. `nine_slice` only helps once the right base art exists. |
| heart number style | Text Node with style tuning | The source number has a specific white fill, warm stroke, and shadow. Text rendering needs engine-side tuning. |

## Probe Decision

Proceed with the local reconstruction anyway, because the mismatch itself is the data this validation is meant to expose.
