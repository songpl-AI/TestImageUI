# Prompt 模板

## 通用模板

```text
Use case: ui-mockup
Asset type: source effect image for a game UI split pipeline
Primary request: Generate a <UI 类型> for a <游戏品类/题材> mobile game.
Canvas: vertical 720x1280 / 1080x1920, no device frame.
Theme: <主题、题材、氛围>.
Core components: <组件清单>.
Style: crisp 2D game UI, polished, clean edges, consistent materials, suitable for later sprite planning.
Composition: centered main UI, clear hierarchy, enough spacing between components.
Text (verbatim): "<精确文字 1>", "<精确文字 2>", "<精确文字 3>".
Engineering constraints: UI elements should be visually separable for later standalone sprite generation; dynamic text should be short and legible; buttons/cards/panels/icons/progress bars should have clear boundaries.
Avoid: device frame, watermark, brand logos, excessive tiny text, garbled text, photorealism unless requested, UI elements fused into the background, strong perspective, cropped key elements.
```

## 活动弹窗

```text
Use case: ui-mockup
Asset type: source effect image for a game UI split pipeline
Primary request: Generate a vertical mobile game event popup.
Canvas: 720x1280, no device frame.
Theme: <主题>.
Core components: themed background, main popup panel, title plate, reward card, reward icon, progress/badge area, primary action button, close button, currency badge.
Style: high quality 2D casual game UI, clean edges, polished trims, consistent lighting.
Composition: centered popup, clear separation between panel, title, reward card, button, icons, and text.
Text (verbatim): "<标题>", "<副标题>", "<按钮>", "<数字>".
Engineering constraints: all UI parts should be visually separable for later Sprite Plan; button and card backgrounds should not be visually fused with text; dynamic text should be legible and easy to replace.
Avoid: too many small labels, garbled text, heavy occlusion, background decorations crossing UI borders, cropped close button, watermark.
```

## 商城礼包页

```text
Use case: ui-mockup
Asset type: game shop UI effect image
Primary request: Generate a mobile game shop bundle screen.
Canvas: vertical 720x1280, no device frame.
Theme: <题材>.
Core components: shop panel, bundle cards, item icons, price tag, discount ribbon, buy button, currency bar, close/back button.
Text (verbatim): "SHOP", "HOT DEAL", "$6", "BUY".
Engineering constraints: product cards, buttons, badges, currency bar, icons, and text should be separable for later sprite generation.
Avoid: dense product grid, unreadable small prices, text baked into complex backgrounds, watermark.
```

## 战令 / 通行证

```text
Use case: ui-mockup
Asset type: battle pass UI effect image
Primary request: Generate a mobile game battle pass reward screen.
Canvas: vertical 720x1280 or horizontal 1280x720, no device frame.
Theme: <赛季主题>.
Core components: season title, level badge, progress bar, reward track, free/premium distinction, claim button, currency counter.
Text (verbatim): "BATTLE PASS", "LEVEL 12", "CLAIM", "3200".
Engineering constraints: reward cards, progress bar, badges, title art, buttons, and icons should have clear boundaries for later sprite extraction.
Avoid: too many reward items, tiny unreadable labels, merged reward track background, watermark.
```

## 任务面板

```text
Use case: ui-mockup
Asset type: quest panel UI effect image
Primary request: Generate a mobile game quest panel.
Canvas: vertical 720x1280, no device frame.
Theme: <主题>.
Core components: main panel, tabs, quest item rows, progress bars, reward icons, claim buttons.
Text (verbatim): "QUESTS", "DAILY", "CLAIM", "3/5".
Engineering constraints: list item backgrounds, tabs, progress bars, buttons, and reward icons should be separable; long task descriptions should be represented as simple placeholder text or omitted.
Avoid: lots of tiny text, overcrowded rows, illegible task descriptions, merged icons and buttons.
```
