# Asset / Layer Plan - Pastoral Match-3 Home UI

## Screen

- Game type: casual match-3
- Screen type: main home screen
- Orientation: portrait
- Visual style: pastoral countryside, warm spring garden, fruit orchard, soft rounded wood UI, cream panels, fresh green leaves, berry accents
- Production board structure:
  - `full_effect`: vertical match-3 home UI mockup
  - `asset_sheet`: fixed 4x4 grid of reusable UI assets

## full_effect Layer Plan

| layer id | type | description |
|---|---|---|
| bg_pastoral_village | background | soft orchard and cottage landscape, low contrast behind UI |
| top_currency_bar | hud_group | hearts, coins, gems, plus buttons |
| player_avatar_frame | frame | round avatar frame top-left |
| event_banner_panel | panel | seasonal event banner near upper middle |
| level_map_panel | panel | winding match-3 level path with round level nodes |
| level_node_active | state_node | active level button on path |
| daily_reward_button | side_button | side activity button |
| mail_button | icon_button | side message button |
| shop_button | icon_button | side shop button |
| play_button_bg | button_bg | large bottom-center primary button |
| play_button_text | text_node | exact text "PLAY" |
| bottom_nav_button_bg | button_bg | reusable bottom tab background |
| home_icon | icon | home tab icon |
| team_icon | icon | team tab icon |
| garden_icon | icon | garden tab icon |

## asset_sheet Fixed Grid

Grid: 4 rows x 4 columns. One isolated asset per cell.

| row | col | asset id | type | constraints |
|---|---:|---|---|---|
| 1 | 1 | top_currency_bar_bg | bar_bg | no numbers, no icons |
| 1 | 2 | heart_icon | icon | clean standalone |
| 1 | 3 | coin_icon | icon | clean standalone |
| 1 | 4 | gem_icon | icon | clean standalone |
| 2 | 1 | plus_button | button_icon | clean standalone |
| 2 | 2 | player_avatar_frame | frame | empty frame, no portrait |
| 2 | 3 | event_banner_panel | panel | no text |
| 2 | 4 | level_node_active | button_state | no number |
| 3 | 1 | level_node_locked | button_state | no number |
| 3 | 2 | play_button_bg | button_bg | no PLAY text |
| 3 | 3 | bottom_nav_button_bg | button_bg | no icon or label |
| 3 | 4 | red_badge_dot | badge_dot | clean standalone |
| 4 | 1 | home_icon | icon | clean standalone |
| 4 | 2 | team_icon | icon | clean standalone |
| 4 | 3 | garden_icon | icon | clean standalone |
| 4 | 4 | shop_icon | icon | clean standalone |

## Text Nodes

| text node id | exact text | role |
|---|---|---|
| title_text | "GARDEN VALE" | fixed title candidate |
| play_button_text | "PLAY" | dynamic button label |
| level_number | "128" | dynamic level number |
| coins_amount | "12,450" | dynamic currency |
| gems_amount | "320" | dynamic currency |

## Validation Questions

- Does the full_effect look like a usable vertical match-3 home screen?
- Are the asset sheet cells visually isolated and stable?
- Do reusable backgrounds avoid baked dynamic text?
- Do asset sheet materials match the full_effect UI materials?
- Can we identify at least 12 planned assets without guessing?
