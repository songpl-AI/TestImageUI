# Sprite Plan - SLG Main

- 源图：`examples/input/slg_main_raw.png`
- 源图尺寸：`1672x941`
- 标准化工作图：`examples/input/slg_main.png`
- 工作图尺寸：`1280x720`
- 输出目录：`examples/output/slg_main_single_sprites/`
- 用途：横屏 SLG 主界面 UI 效果图拆解前置计划
- 当前阶段：推荐方案已确认，已进入 manifest / IR / bbox overlay 阶段
- 生成时间：`2026-07-07`

## 总体判断

这张图适合进入 `ui-sprite-regenerator` 流程。它有明确的横屏 SLG 主界面结构：主城背景、顶部资源 HUD、左侧玩家信息、左侧任务面板、右侧活动入口、底部导航按钮和右下主行动按钮。

需要注意两点：

1. 背景主城细节丰富，建议第一轮作为整张场景背景处理，不拆单个建筑 sprite。建筑热点可以在后续 Layout IR 中作为 invisible hit area 或独立交互节点记录。
2. 图中有较多文字和数字，尤其任务面板的小字。工程上应尽量保留为 Text Node，不把文字烘进底图 sprite。

## 自动确认

| id | 类型 | 建议输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| bg_kingdom_city | background | `bg_kingdom_city.png` | background_sprite | 主城作为整张背景场景使用，避免拆建筑导致上下文碎片化 |
| player_avatar_frame | profile_frame | `player_avatar_frame.png` | standalone_sprite | 左上头像框、金边圆框可复用 |
| player_avatar_icon | avatar_icon | `player_avatar_icon.png` | standalone_sprite | 头盔头像是独立 icon，可替换 |
| player_power_panel_bg | info_panel_bg | `player_power_panel_bg.png` | standalone_sprite | POWER 面板底图应去文字和数字 |
| player_level_badge_bg | badge_bg | `player_level_badge_bg.png` | standalone_sprite | 等级徽章底图与等级数字分离 |
| player_level_text | dynamic_text | 不生成 PNG | text_node | `35` 是动态等级数字 |
| player_power_label | label_text | 不生成 PNG | text_node | `POWER` 应可本地化 |
| player_power_value | dynamic_text | 不生成 PNG | text_node | `1,250,000` 是动态战力数字 |
| vip_badge_bg | badge_bg | `vip_badge_bg.png` | standalone_sprite | VIP 牌底图可复用，文字单独处理 |
| vip_text | dynamic_text | 不生成 PNG | text_node | `VIP 8` 是动态身份等级 |
| title_plate_bg | title_plate | `title_plate_bg.png` | standalone_sprite | 顶部标题牌底图需和 `KINGDOM` 分离 |
| top_banner_decoration | decoration | `top_banner_decoration.png` | standalone_sprite | 标题牌两侧翅膀和垂旗可作为固定装饰 |
| title_text | label_text / fixed_art_text | 不生成 PNG，待确认 | text_node_by_default | `KINGDOM` 可能需要本地化，默认先作为 Text Node |
| resource_bar_bg | resource_bar_bg | `resource_bar_bg.png` | reusable_sprite | WOOD / FOOD / GOLD / GEMS 四条资源条可复用同一底图 |
| resource_plus_button | small_button | `resource_plus_button.png` | reusable_sprite | 四个绿色加号按钮可复用 |
| wood_icon | resource_icon | `wood_icon.png` | standalone_sprite | 木材图标独立复用 |
| food_icon | resource_icon | `food_icon.png` | standalone_sprite | 粮食图标独立复用 |
| gold_icon | resource_icon | `gold_icon.png` | standalone_sprite | 金币图标独立复用 |
| gems_icon | resource_icon | `gems_icon.png` | standalone_sprite | 宝石图标独立复用 |
| resource_labels | label_text | 不生成 PNG | text_node | `WOOD` / `FOOD` / `GOLD` / `GEMS` 应可本地化 |
| resource_values | dynamic_text | 不生成 PNG | text_node | `2.5M` / `3.2M` / `4.7M` / `1,250` 是动态数据 |
| quest_panel_bg | quest_panel_bg | `quest_panel_bg.png` | standalone_sprite | 左侧任务面板底图不应包含任务文字 |
| quest_header_bg | header_bg | `quest_header_bg.png` | standalone_sprite | `QUEST` 标题栏底图与文字分离 |
| quest_collapse_button | small_button | `quest_collapse_button.png` | standalone_sprite | 右上折叠按钮独立使用 |
| quest_row_icon_bg | small_icon_badge | `quest_row_icon_bg.png` | reusable_sprite | 任务行左侧圆形图标底可复用 |
| quest_row_icons | quest_icons | `quest_icon_upgrade.png` 等 | standalone_sprite | 任务类型图标独立生成 |
| quest_texts | dynamic_text | 不生成 PNG | text_node | 任务标题和进度数字都应保留为 Text Node |
| side_event_button_bg | side_button_bg | `side_event_button_bg.png` | reusable_sprite | 右侧活动入口底板可复用 |
| side_notification_badge_bg | notification_badge_bg | `side_notification_badge_bg.png` | reusable_sprite | 红色数字角标可复用 |
| event_chest_icon | event_icon | `event_chest_icon.png` | standalone_sprite | EVENT 宝箱 icon 独立 |
| bonus_gift_icon | event_icon | `bonus_gift_icon.png` | standalone_sprite | BONUS 礼盒 icon 独立 |
| alliance_shield_icon | event_icon | `alliance_shield_icon.png` | standalone_sprite | ALLIANCE 盾牌 icon 独立 |
| arena_swords_icon | event_icon | `arena_swords_icon.png` | standalone_sprite | ARENA 双剑 icon 独立 |
| side_button_labels | label_text | 不生成 PNG | text_node | `EVENT` / `BONUS` / `ALLIANCE` / `ARENA` 应可本地化 |
| side_badge_numbers | dynamic_text | 不生成 PNG | text_node | `3` / `5` / `7` / `1` 是动态红点数字 |
| bottom_nav_button_bg | nav_button_bg | `bottom_nav_button_bg.png` | reusable_sprite | BUILD / ARMY / HERO / QUEST / MAP 可复用按钮底 |
| bottom_nav_icons | nav_icons | `build_icon.png` 等 | standalone_sprite | 底部每个功能 icon 独立 |
| bottom_nav_labels | label_text | 不生成 PNG | text_node | 底部按钮文字应可本地化 |
| chat_button_bg | small_nav_button_bg | `chat_button_bg.png` | standalone_sprite | CHAT 按钮底图与气泡 icon、文字分离 |
| mail_button_bg | small_nav_button_bg | `mail_button_bg.png` | standalone_sprite | MAIL 按钮底图与信封 icon、文字分离 |
| chat_icon | nav_icon | `chat_icon.png` | standalone_sprite | 聊天气泡 icon 独立 |
| mail_icon | nav_icon | `mail_icon.png` | standalone_sprite | 邮件信封 icon 独立 |
| go_button_bg | primary_button_bg | `go_button_bg.png` | standalone_sprite | 右下主行动按钮底图应去文字和城堡 icon |
| go_button_castle_icon | button_icon | `go_button_castle_icon.png` | standalone_sprite | GO 按钮内城堡 icon 独立 |
| go_button_text | label_text | 不生成 PNG | text_node | `GO` 是按钮文案 |

## 需要人工确认

| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| bg_kingdom_city_hotspots | city_building_hotspots | 推荐第一轮不拆建筑，只记录 invisible hit areas | 主城建筑多且互相遮挡，拆成 sprite 会破坏整体透视和光照 |
| title_text | fixed_art_text / text_node | 推荐 Text Node，若作为品牌主标题可改 fixed_art_text | `KINGDOM` 可能需要本地化，也可能作为固定标题艺术字 |
| top_banner_decoration | merged_title_plate / split_decoration | 推荐拆成标题牌底图 + 两侧装饰 + 垂旗 | 装饰是否复用不确定，拆开更灵活但节点更多 |
| resource_bar_bg | one_reusable_bg / four_unique_bgs | 推荐一个通用资源条底图复用 | 四条资源条形状接近，但左侧 icon 区和宽度略不同 |
| quest_panel | clean_panel_plus_text / screenshot_like_panel | 推荐 clean panel + row icons + Text Nodes | 任务列表文字多，直接做整图不可编辑 |
| side_event_buttons | one_bg_reused / four_unique_button_bgs | 推荐共用一个右侧入口底板 | 入口按钮形状一致，icon 和 label 分离即可 |
| bottom_nav_buttons | one_bg_reused / five_unique_button_bgs | 推荐一个通用底部按钮底图复用 | 统一按钮能减少资产数量，选中态暂未出现 |
| go_button | whole_button / bg_icon_text_split | 推荐拆成按钮底图 + 城堡 icon + GO Text | 大按钮可能需要动画、换 icon 或换文案 |
| notification_badges | badge_bg_plus_text / baked_numbers | 推荐 badge bg + Text Node | 红点数字动态变化，不能烘成 PNG |
| city_scene_quality | keep_generated_scene / regenerate_clean_bg | 推荐保留 raw 图作为风格参考，再生成干净背景 | 当前背景很漂亮但被 UI 覆盖区域不可逆，若要无 UI 背景需重生成 |

## 建议第一轮生成的 sprite 清单

如果人工确认按推荐方案执行，第一轮建议生成这些独立素材：

```text
bg_kingdom_city.png
player_avatar_frame.png
player_avatar_icon.png
player_power_panel_bg.png
player_level_badge_bg.png
vip_badge_bg.png
title_plate_bg.png
top_banner_decoration.png
resource_bar_bg.png
resource_plus_button.png
wood_icon.png
food_icon.png
gold_icon.png
gems_icon.png
quest_panel_bg.png
quest_header_bg.png
quest_collapse_button.png
quest_row_icon_bg.png
quest_icon_upgrade.png
quest_icon_train.png
quest_icon_gather.png
quest_icon_defeat.png
side_event_button_bg.png
side_notification_badge_bg.png
event_chest_icon.png
bonus_gift_icon.png
alliance_shield_icon.png
arena_swords_icon.png
bottom_nav_button_bg.png
build_icon.png
army_icon.png
hero_icon.png
quest_nav_icon.png
map_icon.png
chat_button_bg.png
mail_button_bg.png
chat_icon.png
mail_icon.png
go_button_bg.png
go_button_castle_icon.png
```

## Text Node 清单

```text
player_level_text = "35"
vip_text = "VIP 8"
player_power_label = "POWER"
player_power_value = "1,250,000"
title_text = "KINGDOM"
wood_label = "WOOD"
wood_value = "2.5M"
food_label = "FOOD"
food_value = "3.2M"
gold_label = "GOLD"
gold_value = "4.7M"
gems_label = "GEMS"
gems_value = "1,250"
quest_header_text = "QUEST"
quest_1_title = "Upgrade Castle"
quest_1_progress = "(24/25)"
quest_2_title = "Train 1,000 Soldiers"
quest_2_progress = "(680/1000)"
quest_3_title = "Gather 500K Wood"
quest_3_progress = "(320K/500K)"
quest_4_title = "Defeat 10 Bandits"
quest_4_progress = "(6/10)"
side_event_label = "EVENT"
side_bonus_label = "BONUS"
side_alliance_label = "ALLIANCE"
side_arena_label = "ARENA"
side_event_badge = "3"
side_bonus_badge = "5"
side_alliance_badge = "7"
side_arena_badge = "1"
chat_label = "CHAT"
mail_label = "MAIL"
build_label = "BUILD"
army_label = "ARMY"
hero_label = "HERO"
quest_nav_label = "QUEST"
map_label = "MAP"
go_button_text = "GO"
```

## 本轮不生成的内容

- 不把原图 bbox crop 当作最终 sprite。
- 不直接生成 `assets_png/`。
- 不处理真实透明 PNG 去底。

## 人工确认记录

- 用户确认：`按照推荐的来吧`
- 执行结果：已按推荐方案生成 `sprite_manifest.json`、`layer_ir.json`、`layout_ir.json` 和 `bbox_overlay.png`。

## 下一步

请确认“需要人工确认”表中的拆法。如果按推荐方案执行，下一步会进入：

1. 输出 `sprite_manifest.json`。
2. 基于 `examples/input/slg_main.png` 建立 `layer_ir.json` / `layout_ir.json`。
3. 生成 `bbox_overlay.png` 供人工检查。
4. 再进入独立 sprite 生成阶段。
