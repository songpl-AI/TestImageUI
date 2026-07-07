# Known Issues

本文件记录 `ui-sprite-regenerator` 在实际运行中踩过的坑。每次使用 skill 前先读本文件；每次遇到可复用的新问题，按模板追加。

## 使用规则

1. 运行前先扫描本文件，优先应用“预防规则”。
2. 遇到新问题时，判断它是否会导致返工、误解或结果不可用。
3. 如果会，把它追加到“记录区”，并写清楚触发条件、原因、预防规则和修正动作。
4. 不要只记录现象；必须记录下次如何避免。
5. 如果问题来自用户纠正，要尊重纠正内容，并把它转成可执行规则。

## 新增记录模板

```markdown
### KI-YYYYMMDD-短名

- 状态：active / resolved / watch
- 触发条件：
- 问题表现：
- 根因：
- 预防规则：
- 修正动作：
- 验证方式：
- 来源：
```

## 记录区

### KI-20260707-rect-crop-not-sprite

- 状态：active
- 触发条件：用户要求“每一张单图”“sprite 贴图”“工程切图”“可复用素材”。
- 问题表现：把原图按 bbox 裁出矩形块，并把这些 crop 当成最终 sprite。
- 根因：混淆了 reference crop / reconstruction crop 和 engine-ready standalone sprite。
- 预防规则：矩形 crop 只能作为参考、调试或重建校验；最终 sprite 必须是独立生成或干净提取的透明 PNG，只包含目标元素本身。
- 修正动作：先输出 Sprite Plan；确认后逐个生成 standalone sprite，并提供棋盘格总览图。
- 验证方式：查看 `sprite_overview.png`；每个 PNG 应是独立元素，不能带邻近背景、遮挡、其它 UI 或动态文字。
- 来源：Mermaid Pass 图处理时，用户明确纠正“不是要切开图片，是要每一张单图”。

### KI-20260707-plan-before-generate

- 状态：active
- 触发条件：开始处理新的 UI 效果图。
- 问题表现：直接生成素材，后续才发现某些元素应该拆/合/保留为 Text Node。
- 根因：缺少人工确认的 Sprite Plan 阶段。
- 预防规则：任何 UI 图片处理前，必须先输出 Sprite Plan，分为“自动确认”和“需要人工确认”；除非用户明确授权“按你的判断直接执行”，否则不要直接开始生图。
- 修正动作：在输出目录生成 `sprite_plan.md` 或在对话中给出等价表格，等待确认。
- 验证方式：最终回复中说明哪些项自动确认、哪些项经过人工确认。
- 来源：用户要求先分析“哪些元素要分成什么样的 sprite”，不确定的给人工确认。

### KI-20260707-raw-vs-normalized-source

- 状态：active
- 触发条件：同时存在原始生成图和标准化/缩放后的工作图。
- 问题表现：从缩放后的 `720x1280` 图提取或规划素材，而用户真正指定的是 raw 原图。
- 根因：把布局验证用标准图和素材参考用原图混为一谈。
- 预防规则：用户指定具体图片路径时，以该路径作为源图；raw 图用于素材风格参考和高质量生成，标准化图只用于 layout/reconstruction 测试。
- 修正动作：在 Sprite Plan 顶部写明 `source_image`、尺寸和用途；必要时保留 raw IR 与 normalized IR 两套。
- 验证方式：输出路径和计划中显示使用的源图路径与用户指定一致。
- 来源：Mermaid Pass raw 图处理时，用户指出应该基于 `mermaid_pass_raw.png`。

### KI-20260707-dynamic-text-not-png

- 状态：active
- 触发条件：UI 中存在数字、价格、按钮文案、进度值、倒计时、普通 label。
- 问题表现：把动态文字做成 PNG，导致后续不可编辑、不可本地化、不可复用。
- 根因：为了视觉还原，忽略了工程可编辑性。
- 预防规则：动态内容默认是 Text Node，不生成 PNG；只有固定艺术字标题或用户明确要求图片化时才生成 sprite。
- 修正动作：Sprite Plan 中把动态文字列为 `text_node`，输出列写“不生成 PNG”。
- 验证方式：背景/按钮/卡片/进度条素材不含文字；文字在计划或 Layout IR 中单独列出。
- 来源：AI UI split pipeline 设计与 Mermaid Pass 处理经验。

### KI-20260707-concurrent-output-corruption

- 状态：active
- 触发条件：多个命令同时读写同一个 output 目录，尤其是 `prepare-regenerate` 与 `rebuild` 并行执行。
- 问题表现：Pillow 读取到未写完的 PNG，报 `UnidentifiedImageError` 或生成坏图。
- 根因：同一输出目录并发读写，没有原子写入保护。
- 预防规则：同一 output 目录的 pipeline 命令必须串行执行；不要并发运行 prepare/rebuild/full。
- 修正动作：先运行 prepare，确认结束后再运行 rebuild；如出现坏图，删除对应输出目录后重跑。
- 验证方式：命令退出码为 0，`identify` 能识别关键 PNG。
- 来源：`shop_popup_codex` 流程中并发执行 prepare/rebuild 时出现坏图。

### KI-20260707-chroma-key-conflict

- 状态：watch
- 触发条件：主体颜色接近默认 key color，例如绿色、青绿色、霓虹色 UI。
- 问题表现：去底时主体部分被误删，或边缘出现色键残留。
- 根因：chroma-key 颜色与主体颜色冲突，或背景不是完全均匀纯色。
- 预防规则：默认使用 `#00ff00`；如果主体含绿色/青绿色，改用 `#ff00ff` 等不冲突颜色。prompt 必须要求背景完全均匀、无阴影、无渐变、无纹理。
- 修正动作：重新生成 chroma-key 源图，换 key color；必要时调整 `remove_chroma_key.py` 参数。
- 验证方式：最终 PNG 为 RGBA，四角透明，主体边缘没有明显色边或缺损。
- 来源：透明 sprite 生成流程。

### KI-20260707-size-position-consistency

- 状态：active
- 触发条件：人工确认 Sprite Plan 后，准备逐个重新生成 sprite。
- 问题表现：AI 生成的单图自然尺寸、主体占比、padding 或风格细节不一致，无法稳定还原到原 UI；或者只有 sprite 清单，没有位置和层级信息。
- 根因：把“生成哪些单图”和“这些单图放在哪里、多大、谁盖住谁”混为一谈，并把 AI 生成图的自然尺寸误当成工程尺寸。
- 预防规则：Sprite Plan 确认后，必须补 `sprite_manifest.json` 与 `layer_ir.json` / `layout_ir.json` 或等价结构；尺寸、位置、层级、锚点由 IR 锁定，不能靠 AI 猜。
- 修正动作：为每个 sprite / Text Node 记录 bbox 和层级；生成独立 `assets_png` 后，再 fit 到固定 bbox 透明画布生成 `assets_fit_raw`；最后按 IR 输出 `reconstruction.png` / `comparison.png`。
- 验证方式：`assets_fit_raw` 的画布尺寸等于 IR bbox；重建图中元素位置、大小、层级和 Text Node 与源图可对照。
- 来源：Casual Home 图确认后，用户提出“怎么知道单图大小和位置，重新生成是否会一致”的疑问。

### KI-20260707-reuse-asset-vs-layout-instance

- 状态：active
- 触发条件：同一个 sprite 源素材需要在 UI 中出现多次，例如星星、普通 tab 背景、重复按钮底。
- 问题表现：把一个可复用源素材当成多个独立素材重复生成，或让多个布局节点直接引用同一个已 fit 的 PNG，导致尺寸、padding 或位置不可控。
- 根因：混淆 `assets_png` 源素材和 `assets_fit_raw` 布局实例。
- 预防规则：`assets_png/<asset_id>.png` 只表示可复用的干净源素材；每个布局节点必须有独立的 `assets_fit_raw/<layer_id>.png`，即使它们来自同一个源素材。
- 修正动作：在 `layer_ir.json` 中用 layer id 表示布局实例，用 `metadata.asset_id` / `metadata.source_asset_png` 记录源素材；layout 节点引用 `assets_fit_raw/<layer_id>.png`。
- 验证方式：同一 `asset_id` 可以被多个 layer 复用，但 `assets_fit_raw` 输出数量应等于需要图片回贴的 layer 数量。
- 来源：Casual Home 图中 `star_slot` 和 `bottom_tab_bg_normal` 需要复用同一源素材但对应多个布局实例。

### KI-20260707-context-fragmentation-visual-drift

- 状态：active
- 触发条件：把一张完整 AI UI 图拆成多个独立 sprite 后，逐个生成或用程序化 mock 生成资产，再重建整屏。
- 问题表现：重建图与原图的整体材质、光照、透视、线条粗细、色彩饱和度和细节密度明显不一致；各 sprite 之间也不像来自同一套美术。
- 根因：原图是在同一个全局视觉上下文中一次性生成的，而独立 sprite 生成会丢失全局背景、相邻元素、统一光源、材质和细节密度；程序化 mock 只能验证链路，不能代表高保真美术还原。
- 预防规则：区分“pipeline/mock 验证图”和“美术一致性结果”；真实生成时必须提供全屏源图、局部 crop、统一 style guide / palette / material sheet，优先先生成一张 asset family sheet，再拆成透明 sprite，避免逐个孤立生成。
- 修正动作：对需要视觉一致性的项目，先建立 style anchor 和共用参考板；对每个 sprite prompt 引用同一全屏图与同一风格描述；生成后用 sprite overview 和 reconstruction 做一致性审核，不合格时成批重生成同一族资产。
- 验证方式：`sprite_overview.png` 中同类资产的描边、材质、高光、阴影和饱和度一致；`comparison.png` 不应出现明显的矢量化、扁平化或不同画风拼贴感。
- 来源：Casual Home mock reconstruction 中，用户指出原图与重建图差距大且存在明显不一致性。

### KI-20260707-sheet-cell-overflow-and-key-holes

- 状态：active
- 触发条件：使用 asset family sheet 一次性生成 4x4 或网格化 sprite，并按网格单元拆出透明 PNG。
- 问题表现：某些素材越过单元格边界，拆图后带入相邻 sprite 的金边碎片；头像框、地图 pin 等内部镂空区域仍保留 chroma-key 底色。
- 根因：AI 生成的 sheet 不会严格遵守单元边界；只做 border-connected 去底会保留不连通的内部 key 色洞。
- 预防规则：拆 sheet 时不能只按固定 cell crop 输出；应允许少量 cell overflow，去底后按目标中心选择主连通组件，并对非冲突色素材清理内部 key-like 像素。对宝石等主体接近 key 色的素材要豁免全局 key 删除。
- 修正动作：保存原始 cell source 作为审计材料；最终 `assets_png` 只保留目标主组件，去除相邻碎片和内部 key 色洞，再生成 `sprite_overview.png` 人工检查。
- 验证方式：棋盘格总览中每张 sprite 不应含相邻素材碎片；透明镂空区域应显示棋盘格；紫色/宝石主体不能被误删。
- 来源：SLG main UI asset family sheet 拆分时，`top_banner_decoration` 带入相邻半圆碎片，`player_avatar_frame` 和 `map_icon` 内部保留洋红色 key 色。
