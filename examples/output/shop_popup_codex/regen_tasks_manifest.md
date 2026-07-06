# Codex Regenerate Tasks

Generate each target asset from its reference crop and prompt, then place the PNG at `target_asset`.
After all target assets exist, run the pipeline in `rebuild` mode.

## Tasks
### panel_main_bg
- Role: `panel_background`
- Strategy: `regenerate_or_inpaint`
- Size: `580x875`
- Reference: `examples/output/shop_popup_codex/regen_tasks/panel_main_bg/reference_crop.png`
- Prompt: `examples/output/shop_popup_codex/regen_tasks/panel_main_bg/prompt.txt`
- Target: `examples/output/shop_popup_codex/assets_regenerated/panel_main_bg.png`

### title_board
- Role: `title_board`
- Strategy: `regenerate`
- Size: `420x135`
- Reference: `examples/output/shop_popup_codex/regen_tasks/title_board/reference_crop.png`
- Prompt: `examples/output/shop_popup_codex/regen_tasks/title_board/prompt.txt`
- Target: `examples/output/shop_popup_codex/assets_regenerated/title_board.png`

### title_logo
- Role: `title_art_text`
- Strategy: `regenerate`
- Size: `420x90`
- Reference: `examples/output/shop_popup_codex/regen_tasks/title_logo/reference_crop.png`
- Prompt: `examples/output/shop_popup_codex/regen_tasks/title_logo/prompt.txt`
- Target: `examples/output/shop_popup_codex/assets_regenerated/title_logo.png`

### reward_card_bg
- Role: `reward_card_background`
- Strategy: `regenerate`
- Size: `400x345`
- Reference: `examples/output/shop_popup_codex/regen_tasks/reward_card_bg/reference_crop.png`
- Prompt: `examples/output/shop_popup_codex/regen_tasks/reward_card_bg/prompt.txt`
- Target: `examples/output/shop_popup_codex/assets_regenerated/reward_card_bg.png`

### reward_glow
- Role: `decoration_glow`
- Strategy: `regenerate`
- Size: `320x320`
- Reference: `examples/output/shop_popup_codex/regen_tasks/reward_glow/reference_crop.png`
- Prompt: `examples/output/shop_popup_codex/regen_tasks/reward_glow/prompt.txt`
- Target: `examples/output/shop_popup_codex/assets_regenerated/reward_glow.png`

### reward_chest_icon
- Role: `reward_icon`
- Strategy: `segmentation_extract`
- Size: `260x230`
- Reference: `examples/output/shop_popup_codex/regen_tasks/reward_chest_icon/reference_crop.png`
- Prompt: `examples/output/shop_popup_codex/regen_tasks/reward_chest_icon/prompt.txt`
- Target: `examples/output/shop_popup_codex/assets_regenerated/reward_chest_icon.png`

### buy_button_bg
- Role: `button_background`
- Strategy: `regenerate`
- Size: `340x125`
- Reference: `examples/output/shop_popup_codex/regen_tasks/buy_button_bg/reference_crop.png`
- Prompt: `examples/output/shop_popup_codex/regen_tasks/buy_button_bg/prompt.txt`
- Target: `examples/output/shop_popup_codex/assets_regenerated/buy_button_bg.png`

### coin_bar_bg
- Role: `currency_bar_background`
- Strategy: `regenerate`
- Size: `310x85`
- Reference: `examples/output/shop_popup_codex/regen_tasks/coin_bar_bg/reference_crop.png`
- Prompt: `examples/output/shop_popup_codex/regen_tasks/coin_bar_bg/prompt.txt`
- Target: `examples/output/shop_popup_codex/assets_regenerated/coin_bar_bg.png`

### coin_icon
- Role: `currency_icon`
- Strategy: `segmentation_extract`
- Size: `70x70`
- Reference: `examples/output/shop_popup_codex/regen_tasks/coin_icon/reference_crop.png`
- Prompt: `examples/output/shop_popup_codex/regen_tasks/coin_icon/prompt.txt`
- Target: `examples/output/shop_popup_codex/assets_regenerated/coin_icon.png`


## Passthrough Assets
- `screen_background` (screen_background, direct_crop): `examples/output/shop_popup_codex/assets_regenerated/screen_background.png`
- `close_button` (close_button, direct_crop): `examples/output/shop_popup_codex/assets_regenerated/close_button.png`
