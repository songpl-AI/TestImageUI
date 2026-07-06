# Codex Regenerate Tasks

Generate each target asset from its reference crop and prompt, then place the PNG at `target_asset`.
After all target assets exist, run the pipeline in `rebuild` mode.

## Tasks
### currency_bar_bg
- Role: `currency_bar_background`
- Strategy: `regenerate`
- Size: `205x58`
- Reference: `examples/output/mermaid_pass/regen_tasks/currency_bar_bg/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/currency_bar_bg/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/currency_bar_bg.png`

### currency_pearl_icon
- Role: `currency_icon`
- Strategy: `segmentation_extract`
- Size: `56x45`
- Reference: `examples/output/mermaid_pass/regen_tasks/currency_pearl_icon/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/currency_pearl_icon/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/currency_pearl_icon.png`

### main_shell_panel
- Role: `panel_background`
- Strategy: `regenerate_or_inpaint`
- Size: `664x835`
- Reference: `examples/output/mermaid_pass/regen_tasks/main_shell_panel/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/main_shell_panel/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/main_shell_panel.png`

### title_board
- Role: `title_board`
- Strategy: `regenerate`
- Size: `486x295`
- Reference: `examples/output/mermaid_pass/regen_tasks/title_board/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/title_board/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/title_board.png`

### title_logo
- Role: `title_art_text`
- Strategy: `regenerate`
- Size: `400x160`
- Reference: `examples/output/mermaid_pass/regen_tasks/title_logo/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/title_logo/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/title_logo.png`

### subtitle_ribbon
- Role: `ribbon_background`
- Strategy: `regenerate`
- Size: `360x82`
- Reference: `examples/output/mermaid_pass/regen_tasks/subtitle_ribbon/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/subtitle_ribbon/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/subtitle_ribbon.png`

### reward_card_bg
- Role: `reward_card_background`
- Strategy: `regenerate`
- Size: `430x345`
- Reference: `examples/output/mermaid_pass/regen_tasks/reward_card_bg/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/reward_card_bg/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/reward_card_bg.png`

### reward_pearl_icon
- Role: `reward_icon`
- Strategy: `segmentation_extract`
- Size: `240x250`
- Reference: `examples/output/mermaid_pass/regen_tasks/reward_pearl_icon/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/reward_pearl_icon/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/reward_pearl_icon.png`

### level_badge_bg
- Role: `label_badge_background`
- Strategy: `regenerate`
- Size: `265x56`
- Reference: `examples/output/mermaid_pass/regen_tasks/level_badge_bg/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/level_badge_bg/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/level_badge_bg.png`

### progress_bar_bg
- Role: `progress_bar_background`
- Strategy: `regenerate`
- Size: `415x60`
- Reference: `examples/output/mermaid_pass/regen_tasks/progress_bar_bg/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/progress_bar_bg/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/progress_bar_bg.png`

### progress_shell_icon
- Role: `progress_icon`
- Strategy: `segmentation_extract`
- Size: `74x74`
- Reference: `examples/output/mermaid_pass/regen_tasks/progress_shell_icon/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/progress_shell_icon/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/progress_shell_icon.png`

### claim_button_bg
- Role: `button_background`
- Strategy: `regenerate`
- Size: `415x130`
- Reference: `examples/output/mermaid_pass/regen_tasks/claim_button_bg/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/claim_button_bg/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/claim_button_bg.png`

### bottom_shell_decoration
- Role: `decoration_shell`
- Strategy: `segmentation_extract`
- Size: `185x80`
- Reference: `examples/output/mermaid_pass/regen_tasks/bottom_shell_decoration/reference_crop.png`
- Prompt: `examples/output/mermaid_pass/regen_tasks/bottom_shell_decoration/prompt.txt`
- Target: `examples/output/mermaid_pass/assets_regenerated/bottom_shell_decoration.png`


## Passthrough Assets
- `screen_background` (screen_background, direct_crop): `examples/output/mermaid_pass/assets_regenerated/screen_background.png`
- `currency_plus_button` (small_button, direct_crop): `examples/output/mermaid_pass/assets_regenerated/currency_plus_button.png`
- `close_button` (close_button, direct_crop): `examples/output/mermaid_pass/assets_regenerated/close_button.png`
