# Currency Bar Probe Sprite Plan - V2

Source:

- Full effect crop: `crops/source_heart_currency_bar_crop.png`
- Source bbox in `split/full_effect.png`: `[189, 26, 193, 67]`
- Asset sheet: `../split/asset_sheet.png`

This probe validates whether the V2 prompt fixed the V1 currency bar variant mismatch:

```text
top_currency_bar_bg + heart_icon + plus_button + Text Node("5")
```

## Auto Confirmed

| id | type | output | handling | reason |
|---|---|---|---|---|
| top_currency_bar_bg | currency_bar_bg | `assets_png/top_currency_bar_bg.png` | standalone sprite from asset sheet cell | The V2 cell is now a dark-brown resource-slot base, matching the full-effect bar family. |
| heart_icon | currency_icon | `assets_png/heart_icon.png` | standalone sprite from asset sheet cell | Reusable currency icon; number is not baked into the icon. |
| plus_button | button_icon | `assets_png/plus_button.png` | standalone sprite from asset sheet cell | Reusable HUD action button. |
| heart_count_text | dynamic_text | no PNG | Text Node | The `5` is dynamic state text. |

## Needs Manual Review

| id | recommended option | why |
|---|---|---|
| top_currency_bar_bg scale mode | `nine_slice` | Contain/stretch are only probes; production needs stable stretch center and fixed end caps. |
| Text Node style | engine font tuning | The source number uses a thick rounded style with stroke and shadow. |
| exact icon scale/insets | Layer IR tuning | The asset variant is correct, but the source icon and plus button have slightly different insets. |

## Probe Decision

Proceed as a reconstruction validation. This is no longer a prompt-contract failure like V1; it is now mainly a layout/fit metadata problem.
