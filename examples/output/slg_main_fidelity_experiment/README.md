# SLG Fidelity Experiment

This is a minimal upper-bound experiment, not a final sprite output.

It compares two component-level candidates:

- `top_resource_strip`: the four top resource slots as one visual composite region.
- `build_nav_button`: one bottom navigation button as a compact composite region.

The `proxy_crops_not_final_sprites/` files are direct source crops. They are deliberately labeled as proxies because rectangular crops are not reusable final sprites. Their purpose is to answer a narrow question: if a component-level replacement removes most visible drift, then a real component-level regeneration pass is worth doing; if it does not, more splitting or more AI generation is unlikely to solve the problem cheaply.

Review images:

- `focused_component_comparison.png`: source/current/proxy side by side for the two components.
- `full_hybrid_proxy_comparison.png`: source, current full reconstruction, and current reconstruction with only these two proxy regions pasted back.
- `experiment_manifest.json`: bboxes and simple RGB delta metrics.
