# PLAY Button Probe Sprite Plan - V2

Source:

- Full effect crop: `crops/source_play_button_crop.png`
- Source bbox in `split/full_effect.png`: `[274, 833, 347, 104]`
- Asset sheet: `../split/asset_sheet.png`

This probe validates whether the V2 asset sheet provides the same primary button base used by the full-effect PLAY button:

```text
play_button_bg + Text Node("PLAY")
```

## Auto Confirmed

| id | type | output | handling | reason |
|---|---|---|---|---|
| play_button_bg | button_bg | `assets_png/play_button_bg.png` | standalone sprite from asset sheet cell | Button base should not contain dynamic text. |
| play_button_text | dynamic_text | no PNG | Text Node | `PLAY` should remain editable/localizable. |

## Needs Manual Review

| id | recommended option | why |
|---|---|---|
| play_button_bg scale mode | `nine_slice` | The wide button body should not rely on natural image size. |
| side flower decorations | separate decoration sprites | The full-effect button includes side flowers, but the asset sheet only provides the green button base. |
| Text Node style | engine font tuning | The source has large white rounded letters with shadow/stroke. |

## Probe Decision

Proceed as a reconstruction validation, but treat the source crop metrics carefully because the crop includes side flowers and garden background pixels.
