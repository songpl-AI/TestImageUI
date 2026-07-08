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

### KI-20260707-composite-proxy-not-realgen-guarantee

- 状态：watch
- 触发条件：先用源图局部 crop proxy 验证组合控件能显著接近原图，再尝试真实生成同一组合控件 sprite 或拆分组件 sprite。
- 问题表现：crop proxy 贴回后接近原图，但真实生成的组合 sprite 仍出现画风、比例、字重、icon 占比和材质密度漂移；即使改成 `button_bg + icon + badge + Text Node`，如果生成素材本身漂移，最终回贴仍不会更像源图。
- 根因：crop proxy 是像素上限参照，真实生成仍会重新诠释按钮形状、字体、材质和 icon；组合控件或拆分组件能改善可编辑性和组装边界，但没有消除生成模型的视觉漂移。
- 预防规则：不要把 crop proxy 的效果等同于真实生成可达效果；也不要假设“拆得更工程化”就会自动更像源图。先对 1 个组件做真实生成小实验，再决定是否推广到全屏。
- 修正动作：若真实生成失败，优先判断瓶颈是拆分粒度、字体/Text Node、还是素材生成风格漂移；必要时改用更强 reference/edit/inpaint 路径，而不是继续全屏批量生成。
- 验证方式：同时输出 source/current/crop proxy/realgen 局部对比；记录真实生成版本与 source crop 的 delta，不只看 crop proxy 上限。
- 来源：SLG `build_nav_button` 实验中，crop proxy delta 为 0.00，当前独立 sprite delta 为 45.20，整按钮真实生成 delta 为 53.61，拆分真实生成 + Text Node delta 为 45.64；SLG `top_resource_strip` 实验中，当前独立 sprite delta 为 57.61，realgen frame + Text Nodes delta 为 53.92，只小幅改善。

### KI-20260707-edit-cleanup-canonicalizes-ui

- 状态：watch
- 触发条件：把源图局部 crop 作为 edit target/reference，让模型删除遮挡子元素、文字或背景，并补全干净 UI 底板。
- 问题表现：输出确实是干净独立 sprite，但比例、边框厚度、材质颗粒、磨损、高光和细节密度被模型重画成更规整、更高清的“标准 UI 模板”，回贴后仍不像源图。
- 根因：单张扁平 crop 中被 icon、文字或 badge 遮挡的像素没有真实图层信息；edit/inpaint 会按模型先验补全，而不是恢复原始设计稿。没有 mask、材质表或原生分层资产时，局部参考不能锁死源图级细节。
- 预防规则：不要把 edit/cleanup/inpaint 视为比重新生成更可靠的高保真保证；它只能作为小实验验证。若一个组件已经在 whole realgen、decomposed realgen、cleanup/inpaint 三条路径都失败，不要继续堆 prompt 复杂度。
- 修正动作：记录 metrics 和对比图；若仍不接近 source，停止在该组件上继续 prompt 微调，转向其它代表组件验证或考虑人工修图、受控分割、PSD 化、style/material sheet 等替代方案。
- 验证方式：输出 source/current/crop proxy/whole realgen/decomposed realgen/cleanup 局部对比；比较 mean RGB delta，并检查 `sprite_overview.png` 是否虽干净但风格标准化。
- 来源：SLG `build_button_bg_cleanup` 实验中，cleanup/inpaint 生成了透明按钮底板，但局部 delta 为 47.56，差于拆分真实生成 + Text Node 的 45.64。

### KI-20260707-multi-slot-composite-relayout

- 状态：watch
- 触发条件：把多个重复槽位或横向 HUD 控件作为一个大 composite sprite 生成，例如顶部资源条、任务标签组、多个货币条。
- 问题表现：生成图满足透明和无文字约束，但会重新分配槽位间距、条宽、icon 大小、icon 颜色和加号样式；局部指标可能略有改善，但仍远离 crop proxy 上限。
- 根因：模型把宽组合控件理解为“重新设计一组整齐 HUD 槽位”，而不是严格复刻源图中的不均匀间距、具体 icon identity 和小尺寸材质细节。
- 预防规则：多槽位 composite 可以作为小实验，但不要因为它比细拆略好就推广到整屏；必须检查 spacing、icon identity、颜色和 Text Node 对齐。
- 修正动作：若要继续追求高保真，优先考虑从确定性素材/人工修图/PSD 化/受控分割补图获取 icon 与 frame，而不是继续用 prompt 微调宽组合控件。
- 验证方式：输出 source/current/crop proxy/realgen frame + Text Nodes 对比，并同时记录 full-crop delta 和 UI-mask delta。
- 来源：SLG `top_resource_strip` 实验中，realgen frame + Text Nodes 的 full-crop delta 从 57.61 降到 53.92，UI-mask delta 从 60.78 降到 58.34，但 spacing 与 icon identity 明显漂移，宝石从紫色偏为银蓝色。

### KI-20260707-visual-state-extract-tradeoff

- 状态：watch
- 触发条件：用户更关心“生成图要像效果图”，并允许位置后续手调，不强求每个 sprite 都高度可复用、可编辑。
- 问题表现：AI 重新生成路线视觉漂移大；但 source-preserving mask extract 可以非常接近源图，同时会把文字、状态、icon 和局部材质烘焙在同一张视觉态 sprite 中。
- 根因：保留源图像素能避开重新生成带来的画风漂移，但单张扁平图没有真实图层，视觉态提取无法自动恢复可编辑结构。
- 预防规则：在 Sprite Plan 中明确区分 `visual_state_sprite` 和 `engineering_sprite`。前者用于视觉还原优先，允许烘焙文字/状态；后者用于长期工程复用，仍需 Text Node 和干净子资产。
- 修正动作：需要“先像效果图”时，优先尝试非矩形 semantic mask 提取，而不是继续 prompt 微调真实生成。需要正式可复用资产时，再单独补一套工程拆分。
- 验证方式：输出 sprite overview、mask overlay、source/current/proxy/visual_extract 对比，并分别记录 full-crop delta 与 alpha-mask delta。
- 来源：SLG `build_nav_button_visual_state` 实验中，current independent delta 为 45.20，visual extract 贴回当前重建底图 delta 为 4.63，alpha-mask 区域 delta 为 1.56。

### KI-20260707-layered-source-extract-occlusion-limit

- 状态：watch
- 触发条件：按图层关系拆分源图组件，并尝试对每层做 source-preserving extraction，例如按钮底板、icon、badge、Text Node。
- 问题表现：icon/badge 这类可见前景层能较好提取；但底板被 icon、文字或 badge 遮挡时，干净底板只能局部补洞，补洞质量决定最终相似度。
- 根因：单张扁平效果图没有真实隐藏图层。保留源图像素可以避免 AI 重画漂移，但无法凭空恢复被遮挡的底板像素。
- 预防规则：不要把 `source_extract` 理解成自动恢复完整 PSD 图层；对遮挡层必须显式记录 `exclude_mask`、`known_limitation` 和可选 `reference_package`。补洞只应该作用在小范围遮挡区域，不要重画整个资产。
- 修正动作：为困难 layer 输出局部截图、target mask、exclude mask 和 prompt，后续可用 crop + mask + prompt 做增强；同时保留 `visual_state_sprite` 作为视觉上限回退。
- 验证方式：同时输出 visual_state、layered + Text Node、layered + fixed text 对比；记录 full-crop delta 和 layer-mask delta，并查看 sprite_overview 中每层是否独立透明。
- 来源：SLG `build_nav_button_layered_source_extract` 实验中，current independent delta 为 45.20，layered + Text Node delta 为 28.69，layered + fixed text delta 为 22.66，visual_state delta 为 4.63。

### KI-20260707-sam-rembg-mask-not-hidden-layer

- 状态：watch
- 触发条件：引入 SAM2 / SAM / rembg / matting 工具来改善 source-preserving sprite extraction。
- 问题表现：前景 icon、badge、fixed text 的 mask 和 alpha 明显更稳定，但底板被前景层遮挡的区域仍然只能近似补洞；如果把 rembg 的整组件 alpha 直接混入底板，可能把 badge、icon 边缘或邻近像素漏进 button_bg。
- 根因：SAM/rembg 处理的是可见像素的分割和边缘，不包含被遮挡的隐藏图层信息；rembg 也不知道工程层语义，不能决定哪个像素属于底板、子元素或视觉态。
- 预防规则：SAM/rembg 只能作为 `target_mask` / `alpha_refine` 辅助，Layer IR 仍必须显式区分 `visual_state_sprite`、`button_bg`、`icon`、`badge`、`Text Node`。底板 outer alpha 应优先来自 SAM 的底板/按钮 mask，不要直接使用整组件 rembg alpha。遮挡补洞必须单独标记为 `known_limitation`。
- 修正动作：保存 SAM candidate overview、chosen masks、rembg alpha 和 reference_package；对前景层用 SAM mask + rembg refine，对底板用 SAM button mask 减 child masks，再只对遮挡洞做局部 fill / LaMa / 人工修图小实验。
- 验证方式：同时检查 `sprite_overview.png` 的独立资产洁净度、`focused_*comparison.png` 的回贴效果、full-crop delta、layer-mask delta，以及 visual-state alpha-mask delta。
- 来源：SLG `build_nav_button_sam_rembg_extract` 实验中，previous layered + Text Node delta 为 28.69，SAM/rembg layered + Text Node delta 为 21.89；previous layered + fixed text delta 为 22.66，SAM/rembg layered + fixed text delta 为 15.84；visual-state diagnostic alpha-mask delta 为 0.97，但 button_bg 遮挡区域仍需要近似补洞。

### KI-20260707-lama-inpaint-needs-shadow-layer

- 状态：watch
- 触发条件：用 LaMa / inpaint 工具补全被 icon、文字、badge 遮挡的底板 layer。
- 问题表现：LaMa 对底板遮挡洞有小幅改善，但如果 mask 只覆盖前景实体，不覆盖投影/阴影，底板 sprite 仍会残留暗影痕迹；如果扩大 mask，又可能重画金边、材质和面板纹理，造成新的漂移。
- 根因：inpaint 模型只能根据周围像素生成合理近似，不能知道阴影应该属于 icon、独立 shadow layer 还是 button_bg。单张扁平图没有真实隐藏图层，也没有光影归属标注。
- 预防规则：在 Layer IR 中把 `shadow` / `drop_shadow` 归属显式记录为 `needs_manual_shadow_review`，不要默认自动拆成独立 layer。对 icon 阴影，可以候选为跟随 icon 或独立 shadow layer，但必须用对照图和指标验证；只有确认阴影不属于底板时，才把它纳入底板 inpaint mask。不要把 LaMa 当作自动 PSD 恢复。
- 修正动作：输出至少两类 mask 对照：实体 mask 和实体+shadow mask；比较 sprite_overview 的底板洁净度、回贴 delta 和视觉漂移。若 shadow 拆层没有提升，不要继续盲目更换 inpaint 模型，应把 shadow 归属交给人工确认或依赖 PSD/人工修图。
- 验证方式：同时检查 `build_button_bg*.png` 是否残留 icon 阴影、`focused_lama*_comparison.png` 的局部效果、Text Node/fixed text 两套 delta，以及 visual-state diagnostic 仍然作为视觉上限。
- 来源：SLG `build_nav_button_lama_inpaint_extract` 实验中，SAM/rembg layered + Text Node delta 为 21.89，LaMa layered + Text Node delta 为 20.67；SAM/rembg fixed text delta 为 15.84，LaMa fixed text delta 为 14.59；提升存在但不大，且 button_bg 仍可见锤子阴影/遮挡痕迹。随后 `build_nav_button_shadow_layer_extract` 实验中，previous LaMa + fixed text 为 14.59，shadow small + fixed text 为 14.71，shadow medium + fixed text 为 15.33，说明自动 shadow 拆层会略微变差。

### KI-20260707-sync-asset-sheet-needs-scale-mode

- 状态：active
- 触发条件：使用同步生成的 `full_effect + asset_sheet` production board，并从 asset sheet 提取按钮底板、货币条、面板等可拉伸 UI 背景做回贴。
- 问题表现：asset sheet 中的无字按钮底板是干净独立素材，但用 contain/等比 fit 回贴到 full_effect 的宽按钮 bbox 时明显过短；改用 stretch fit 更接近，但会拉伸边角、叶子或装饰。
- 根因：按钮底、货币条、面板等 UI 背景在引擎里通常依赖九宫格/切片拉伸，而不是用自然尺寸等比缩放。同步生成能改善风格一致性，但不会自动给出 `scale_mode`、九宫格边界和装饰归属。
- 预防规则：Asset / Layer Plan 与 Layer IR 中必须为可拉伸背景记录 `scale_mode`，至少区分 `contain`、`stretch`、`nine_slice`；对按钮花朵、叶子、角标等装饰，明确是 baked into bg 还是 separate decoration layer。
- 修正动作：回贴验证时至少输出 contain 与 stretch 两个对照；若 stretch 明显优于 contain，则不要继续调 prompt，优先补 `nine_slice` 元数据和装饰归属人工确认项。
- 验证方式：输出 source / contain fit / stretch fit 对比图；检查 `assets_fit_raw` 的画布是否来自 IR bbox；记录 full-crop delta 与 alpha-mask delta，但以视觉和装饰归属判断为主。
- 来源：Pastoral Match-3 `play_button_probe` 中，`play_button_bg` contain fit 的 full-crop delta 为 112.09、alpha-mask delta 为 81.62；stretch fit 改善为 84.30 / 61.21，但仍缺少 full_effect 中的花朵装饰和正确九宫格边界。

### KI-20260707-sync-asset-sheet-variant-mismatch

- 状态：active
- 触发条件：使用同步生成的 `full_effect + asset_sheet` production board，并假设同名 asset id 的 asset-sheet 单元就是 full-effect 中对应 layer 的可复用底图。
- 问题表现：asset sheet 的网格结构和命名看起来正确，但某个资产的视觉 variant 与 full-effect 中实际使用的 layer 不一致；例如 asset sheet 给出浅色 cream panel，而 full-effect 顶部资源条使用深棕 capsule slot。
- 根因：prompt 只约束了“需要哪些 asset id”，没有强约束“asset_sheet 单元必须是 full_effect 同名 layer 的同款 base art，只移除动态文字和子元素”。模型会把 asset sheet 当成同风格素材清单，而不是严格的图层引用表。
- 预防规则：Asset / Layer Plan 必须写清楚每个 full_effect layer id 与 asset_sheet cell 的一一对应关系；asset_sheet 中的 base layer 必须保持相同 silhouette、材质、颜色、描边、边角和装饰归属，只能删除文字、icon、数字等 child layers。
- 修正动作：发现 variant mismatch 时，不要继续调 contain/stretch/nine_slice；先回到 prompt contract，要求重新生成正确 asset variant。只有拿到正确 base art 后，才验证 `scale_mode` 和九宫格。
- 验证方式：对至少两个不同类型组件做局部回贴对比；如果 contain/stretch 指标接近且都很差，同时肉眼看到颜色/材质/形状不一致，应判定为 asset identity mismatch。
- 来源：Pastoral Match-3 `currency_bar_probe` 中，`top_currency_bar_bg + heart_icon + plus_button + Text Node("5")` 的 contain delta 为 66.34，stretch delta 为 67.39；问题是浅色 asset-sheet bar 与深棕 full-effect bar 不同款，缩放策略无法修复。

### KI-20260707-production-board-layer-ownership-drift

- 状态：active
- 触发条件：用单张 production board 同时生成 `full_effect` 与 `asset_sheet`，并要求 asset cell 是某个 layer 的干净 base art。
- 问题表现：整体风格和同款性比逐个独立生成更好，但 asset cell 可能把其它层的装饰、标题牌、花叶、阴影或外框一起烘焙进来；full_effect 中的动态数字、价格、折扣也可能不按 spec 精确生成。
- 根因：图像模型把 production board 当作视觉设计板，而不是严格执行的图层导出器；它会按美术完整性重组装饰归属，并弱化 JSON/bbox/text 的工程约束。
- 预防规则：production board 只能作为 style/material/variant 同步验证，不可直接视为最终 Layer IR 或透明 sprite 来源。每个 asset id 必须继续声明 decoration ownership、forbid_text、scale_mode、Text Node 边界，并用局部对比确认是否干净。
- 修正动作：从 board 中切出的 cell 只能作为审计材料或 reference crop；进入工程前必须再做透明提取/单图重生成/人工修图，并通过 `sprite_overview` 与 reconstruction 验证。
- 验证方式：输出 full-effect crop vs asset-sheet cell 对比；检查 base asset 是否包含不该属于该层的 title board、花叶、child icon、数字、价格或阴影。
- 来源：`spec_driven_realgen_validation` 中，`main_panel_bg` asset cell 与 full UI 同风格，但把 title plaque 和花叶装饰烘焙进了面板底图；full UI 的 `currency_amount` 也从 spec 的 `3200` 漂移成 `1,250`。

### KI-20260707-asset-cell-tight-padding

- 状态：active
- 触发条件：从 production board / asset sheet 中裁出单个 cell，并将其转换为透明源 sprite。
- 问题表现：PNG 已经是 RGBA，文字也去掉了，但主体或装饰贴到 cell 边界，导致某些角落 alpha 不是 0，或者自然 sprite 缺少可安全缩放/居中的 padding。
- 根因：图像模型生成 asset sheet 时不会为每个 cell 预留工程化透明边距；装饰叶片、花朵、阴影或边框可能触碰 crop 边缘。
- 预防规则：不要只用 “RGBA + 去文字” 判定 sprite 合格；还要检查四角 alpha、主体 bbox 与 crop 边缘距离、sprite_overview 中是否有足够透明 padding。
- 修正动作：优先重新生成带明确 padding 的 asset cell；次选手工扩展透明画布并在 fit 阶段先 trim subject bbox；如果装饰归属不明确，拆成 background + decoration layer。
- 验证方式：记录 `corner_alpha`、transparent ratio、foreground bbox；`assets_fit_raw` 必须来自 IR bbox，而不是直接拉伸贴边自然图。
- 来源：`spec_driven_currency_bar_probe` 中，`currency_bar_bg` 已去掉中性背景并可回贴，但左下角 alpha 仍为 255，因为叶片装饰贴到了 cell 边缘。

### KI-20260707-closed-panel-alpha-hole-fill

- 状态：active
- 触发条件：从浅色中性 backing 的 asset cell 中提取浅色封闭面板、卡片底、牌匾或 parchment 背景。
- 问题表现：只按背景色差生成 alpha 时，金边/描边被保留，但面板内部因为颜色接近 backing 被误做成半透明或透明，sprite_overview 中能看到棋盘格穿透面板内部。
- 根因：颜色差分只能识别高对比边缘和纹理，不能理解“封闭边框内部也属于同一 UI 底图”。
- 预防规则：对封闭 UI 背景类素材，alpha mask 不能只靠色差；应先用高置信边缘/材质得到 subject seed，再从 crop 边界做 background flood fill，并把非边界连通的内部孔洞填为前景。
- 修正动作：用 hole-fill 后的 mask 重新输出 RGBA，并重新检查四角 alpha、内部不透棋盘格、`sprite_overview.png` 和 focused comparison。
- 验证方式：面板内部应为不透明材质；四角 alpha 应为 0；`transparent_ratio` 不应来自面板内部大面积漏空。
- 来源：`spec_driven_panel_split_validation` 中，第一版 `panel_base` 提取把浅色面板内部做成半透明；改用 border flood fill + hole fill 后四角 alpha 为 `[0,0,0,0]` 且内部不再透出棋盘格。
