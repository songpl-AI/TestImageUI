# Sprite Plan - Casual Home

- 源图：`examples/input/casual_home.png`
- 源图尺寸：`720x1280`
- raw 参考图：`examples/input/casual_home_raw.png`
- 用途：休闲游戏主界面 UI 效果图拆解前置计划
- 当前阶段：人工确认已完成，可进入独立 sprite 生成阶段
- 确认时间：`2026-07-07`

## 总体判断

这张图适合继续进入 `ui-sprite-regenerator` 流程。主要 UI 元素边界比较清楚，能分成顶部 HUD、中央关卡入口、侧边活动入口、底部导航和背景场景几大块。

需要注意：这是主界面，不是单一弹窗。相比弹窗，主界面的背景和 UI 元素耦合更强，尤其中央关卡卡片中间有“道路/场景窗口”，底部导航和背景贴得较近，因此部分元素需要人工确认拆法。

## 自动确认

| id | 类型 | 建议输出 | 处理方式 | 原因 |
|---|---|---|---|---|
| bg_candy_village | background | `bg_candy_village.png` | standalone_sprite / background | 背景场景作为整张背景图使用，不作为按钮类 sprite 拆分 |
| player_avatar_frame | profile_badge_bg | `player_avatar_frame.png` | standalone_sprite | 头像框、等级底座、进度条属于可复用 HUD 组件，建议去掉猫头像和数字 |
| player_avatar_icon | avatar_icon | `player_avatar_icon.png` | standalone_sprite | 猫头像是独立 avatar icon，可单独生成或替换 |
| player_level_text | dynamic_text | 不生成 PNG | text_node | `12` 属于动态等级数字 |
| player_progress_bar | progress_bar_bg | `player_progress_bar.png` | standalone_sprite | 头像下方紫色进度条应作为独立 HUD 资产 |
| coin_bar_bg | currency_bar_bg | `coin_bar_bg.png` | standalone_sprite | 金币资源条底图需要去掉金币 icon、数字和加号 |
| coin_icon | currency_icon | `coin_icon.png` | standalone_sprite | 金币 icon 可复用 |
| coin_amount_text | dynamic_text | 不生成 PNG | text_node | `1200` 是动态资源数字 |
| coin_plus_button | small_button | `coin_plus_button.png` | standalone_sprite | 加号按钮是明确独立按钮 |
| gem_bar_bg | currency_bar_bg | `gem_bar_bg.png` | standalone_sprite | 宝石资源条底图需要去掉宝石 icon、数字和加号 |
| gem_icon | currency_icon | `gem_icon.png` | standalone_sprite | 宝石 icon 可复用 |
| gem_amount_text | dynamic_text | 不生成 PNG | text_node | `85` 是动态资源数字 |
| gem_plus_button | small_button | `gem_plus_button.png` | standalone_sprite | 加号按钮是明确独立按钮 |
| settings_button | icon_button | `settings_button.png` | standalone_sprite | 设置按钮边界清晰，可独立生成 |
| play_button_bg | button_bg | `play_button_bg.png` | standalone_sprite | 主按钮底图必须去掉 `PLAY` 文案 |
| play_button_label | button_label | 不生成 PNG | text_node | `PLAY` 应保持可编辑，除非后续确认要艺术字图片 |
| event_gift_icon | icon | `event_gift_icon.png` | standalone_sprite | 礼物盒 icon 可独立复用 |
| event_label_text | label_text | 不生成 PNG | text_node | `EVENT` 应作为 Text Node |
| quest_clipboard_icon | icon | `quest_clipboard_icon.png` | standalone_sprite | 任务剪贴板 icon 可独立复用 |
| quest_label_text | label_text | 不生成 PNG | text_node | `QUEST` 应作为 Text Node |
| gift_chest_icon | icon | `gift_chest_icon.png` | standalone_sprite | 宝箱 icon 可独立复用 |
| gift_label_text | label_text | 不生成 PNG | text_node | `GIFT` 应作为 Text Node |

## 人工确认结果

| id | 类型 | 推荐选项 | 需要确认的原因 |
|---|---|---|---|
| central_level_card | level_card / map_gate | 已确认：拆成 `level_card_bg` + `level_ribbon_bg` + `star_slot` + `inner_scene_window` + `play_button_bg` | 中央关卡入口很大，包含外框、标题丝带、场景窗口、星星和按钮；拆开更适合工程化 |
| level_ribbon_bg | ribbon_bg | 已确认：独立 sprite，`LEVEL 24` 作为 Text Node | 关卡号动态变化，不做图片文字 |
| level_title_text | dynamic_text | 已确认：Text Node | 文字有轻微艺术效果，但关卡号应动态 |
| star_slots | rating_icons | 已确认：生成单个 `star_slot.png` | 单星更适合动态评分数量 |
| central_inner_scene | scene_window | 已确认：作为可独立放入卡片的场景窗口素材 | 与卡片外框分离，方便替换或动画 |
| left_event_button_bg | side_button_bg | 已确认：底板、icon、文字分开 | 入口按钮可复用，文字保持可编辑 |
| left_quest_button_bg | side_button_bg | 已确认：底板、icon、文字分开 | 入口按钮可复用，文字保持可编辑 |
| right_gift_button_bg | side_button_bg | 已确认：底板、icon、文字分开 | 入口按钮可复用，文字保持可编辑 |
| bottom_nav_bar_bg | nav_bar_bg | 已确认：独立生成整条紫色导航底 | 底部导航条适合整体背景 |
| bottom_tab_bg_normal | nav_tab_bg | 已确认：生成 normal tab 背景 | SHOP/QUEST/DECOR 使用普通态 |
| bottom_tab_bg_selected | nav_tab_bg_selected | 已确认：生成 selected tab 背景 | HOME 使用选中态 |
| bottom_tab_icons | nav_icons | 已确认：每个 icon 独立：`shop_icon`、`quest_icon`、`home_icon`、`decor_icon` | icon 可复用，且与 tab 背景分离 |
| bottom_tab_labels | label_text | 已确认：全部 Text Node：`SHOP`、`QUEST`、`HOME`、`DECOR` | 底部 tab 文案可能本地化 |
| foreground_candy_decor | background_part | 已确认：归入背景，不拆独立 decoration sprite | 前景糖果、花草与背景耦合强 |

## 建议第一轮生成的 sprite 清单

如果人工确认按推荐方案执行，第一轮建议生成这些独立素材：

```text
bg_candy_village.png
player_avatar_frame.png
player_avatar_icon.png
player_progress_bar.png
coin_bar_bg.png
coin_icon.png
coin_plus_button.png
gem_bar_bg.png
gem_icon.png
gem_plus_button.png
settings_button.png
level_card_bg.png
level_ribbon_bg.png
star_slot.png
play_button_bg.png
event_button_bg.png
event_gift_icon.png
quest_button_bg.png
quest_clipboard_icon.png
gift_chest_icon.png
gift_label_bg.png
bottom_nav_bar_bg.png
bottom_tab_bg_normal.png
bottom_tab_bg_selected.png
shop_icon.png
quest_icon.png
home_icon.png
decor_icon.png
```

## Text Node 清单

```text
player_level_text = "12"
coin_amount_text = "1200"
gem_amount_text = "85"
level_title_text = "LEVEL 24"
play_button_label = "PLAY"
event_label_text = "EVENT"
quest_label_text = "QUEST"
gift_label_text = "GIFT"
bottom_shop_label = "SHOP"
bottom_quest_label = "QUEST"
bottom_home_label = "HOME"
bottom_decor_label = "DECOR"
```

## 人工确认记录

1. 中央关卡入口：要整体一张，还是按推荐拆成外框、丝带、星星、按钮等？
    答：按照推荐拆吧
2. `LEVEL 24`：作为动态 Text Node，还是固定艺术字图片？
    答：动态 Text Node
3. 星星：需要单个星星 icon，还是三个星星整体图？
    答：需要单个星星 icon
4. 侧边 EVENT / QUEST / GIFT：整体按钮一张，还是底板、icon、文字分开？
    答：底板、icon、文字分开
5. 底部导航：是否按“导航条背景 + 普通 tab + 选中 tab + 独立 icon + Text”拆？
    答：是
6. 前景糖果和花草：只是背景的一部分，还是需要独立 decoration sprite？
    答：是背景的一部分

## 本轮不生成的内容

- 本文件本身不生成最终 sprite。
- 不做矩形 crop 冒充 sprite。
- 不生成 Layer IR。
- 不做 UI 重建。

下一步进入真正的独立 sprite 生成阶段，执行清单见 `sprite_manifest.json`。
