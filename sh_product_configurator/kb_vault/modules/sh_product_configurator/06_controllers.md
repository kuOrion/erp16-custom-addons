# Controllers
Status: [ACTIVE]
Back to [[00_overview]]

## /unlink/product_variant [POST, type=json]
Status: [ACTIVE]
File: `controllers/product_configurator.py`
Auth: user
Purpose: Deletes a transient/temporary `product.product` created as a side effect of the configurator flow, but only if it was never a real manually-saved variant (`not sh_is_created_manually` OR `not sh_is_record_saved`) — real saved variants are never touched by this route.
Called by: [[05_owl_components#sale_product_field.js]] (on modal confirm and on modal close)
Returns: `True`/`False`/unlink result (JSON boolean-ish)
Note: uses `sudo()` to browse/unlink — the safety check is the `sh_is_created_manually`/`sh_is_record_saved` guard, not access rights.

## /update_product_variant [POST, type=json]
Status: [ACTIVE]
File: `controllers/product_configurator.py`
Auth: user
Purpose: Replaces (not merges) a variant's `product_template_attribute_value_ids` with the ids the user selected in the configurator UI, using `(6, 0, ids)` for an atomic all-or-nothing update.
Params: `sh_product_id`, `product_template_id`, `product_template_attribute_value_ids` (JSON string of ids)
Called by: [[05_owl_components#variant_mixin.js]] `VariantMixin.updateProduct`
Returns: `True`
Note: uses `sudo()` to browse/write.

## /sale_product_configurator/configure [POST, type=json] — override
Status: [ACTIVE]
File: `controllers/main.py`, class `WebsiteSaleProductConfiguratorController(ProductConfiguratorController)`
Auth: user
Purpose: Calls the parent `sale_product_configurator` controller's `configure()` to get the base rendering context, then re-derives the same context (product template, pricelist, selected combination) and re-renders `sale_product_configurator.configure` with an added `attribute_parent_map` (JSON dict of `{child_attribute_id: {parent_attribute_id, parent_value_id}}`, built by scanning `product_template.attribute_line_ids` for `sh_parent_attribute`/`sh_parent_value`).
Called by: [[05_owl_components#sale_product_field.js]]
Returns: rendered HTML (QWeb `sale_product_configurator.configure`, see [[04_views_xml#templates.xml]])
Known limitation: comment in the code notes calling `super().configure()` first and then re-rendering is "a bit hacky" since the base method returns HTML, not a dict — see [[09_known_issues]].

## _show_advanced_configurator (helper, invoked via inherited route)
Status: [ACTIVE]
File: `controllers/main.py`
Auth: inherited from the base `show_advanced_configurator` route it overrides (same class)
Purpose: Same `attribute_parent_map` derivation as `configure()` above, applied when rendering `sale_product_configurator.optional_products_modal` for the "advanced configurator" (multi-product / edit-existing-variant) modal path.
Called by: [[05_owl_components#product_configurator_modal.js]] `willStart()`
Returns: rendered HTML (QWeb `sale_product_configurator.optional_products_modal`)
