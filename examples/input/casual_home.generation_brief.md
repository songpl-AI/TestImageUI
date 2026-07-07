# Casual Home Generation Brief

- UI 类型：休闲游戏主界面 / Home Screen
- 画布：竖屏 `720x1280` 标准版，保留 raw 生成图
- 游戏品类：cozy casual match-3 / light decoration game
- 主题：sunny candy garden village
- 用途：作为后续 Sprite Plan、Layer IR、独立 sprite 生成和 UI 重建的源效果图

## 必须出现的组件

- 背景场景
- 顶部玩家头像 / 等级 badge
- 顶部金币和宝石资源条
- 设置按钮
- 中央关卡入口 / map node card
- 大号 `PLAY` 主按钮
- 侧边 `EVENT` 入口
- 侧边 `QUEST` 入口
- 礼物 icon
- 底部四个导航 tab

## 精确文字

- `LEVEL 24`
- `PLAY`
- `SHOP`
- `QUEST`
- `EVENT`
- `1200`
- `85`

## 工程化约束

- UI 元素要视觉可分离，方便后续做 Sprite Plan。
- 按钮、卡片、badge、资源条、icon、底部导航 tab 要有清晰边界。
- 动态文字短且清晰，后续可作为 Text Node。
- 背景服务 UI，不要穿插核心 UI 边界。
