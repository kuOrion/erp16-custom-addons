# Data Flow
Status: [ACTIVE]
Back to [[00_overview]]

## Flow 1 — Admin creates a hierarchical attribute on a product template
User adds an attribute line on the Product Template form (Attributes tab) →
`product.template.attribute.line.create()` [[03_models#ProductTemplateAttributeLine]] checks `base.group_system`,
auto-fills `product_tmpl_id` from `parent_attribute_value_id` if given, forces `sequence=999` for new lines
(bottom of list) unless `sh_keep_sequence` context is set, and if the attribute itself is brand-new
(`(0, 0, {...})` tuple) stamps `sh_parent_value` / `sh_parent_attribute` / `sh_is_custom_attribute` /
`sh_product_tmpl_id` onto the attribute vals before creation →
after `super().create()`, links `record.attribute_id.sh_product_tmpl_id` if unset →
calls `_sh_insert_hierarchically()` to place the new line immediately after its parent's last descendant,
shifting other lines' `sequence` as needed (not a full resequence — see [[03_models#ProductTemplateAttributeLine]]).
A uniqueness constraint (`_check_duplicate_attribute_name_per_template`) blocks two lines on the same
template sharing an attribute name (case-insensitive check, then exact match).

## Flow 2 — Configuring/editing a variant from the Sale Order line
User clicks "Configure" on a sale order line (or edits a `product.product` directly) →
`sale_product_field.js#_openProductConfigurator` detects `resModel == 'product.product'`, stores
`sh_active_model` in `localStorage`, calls controller [[06_controllers#/sale_product_configurator/configure]]
which renders `sale_product_configurator.configure` with `attribute_parent_map` injected →
modal opens (`OptionalProductsModal`, patched in [[05_owl_components#product_configurator_modal.js]]),
`willStart()` detects `sh_active_model` and instead fetches
`/sale_product_configurator/show_advanced_configurator` → `_show_advanced_configurator()`
[[06_controllers#_show_advanced_configurator]] renders `sale_product_configurator.optional_products_modal`
with the same `attribute_parent_map` →
`_onModalReady()` wires change listeners on `.variant_attribute` radio/select inputs to recursively
show/hide child attribute groups per `attribute_parent_map` →
on Confirm, `shGetAndCreateSelectedProducts()` collects selected PTAV ids per product row and calls
`VariantMixin.updateProduct` [[05_owl_components#variant_mixin.js]] → JSON-RPC
[[06_controllers#/update_product_variant]] which writes `product_template_attribute_value_ids` via
`(6, 0, ids)` onto the target `product.product` (sudo) →
on modal close, `/unlink/product_variant` [[06_controllers#/unlink/product_variant]] removes the
transient variant if it was never marked `sh_is_record_saved`/`sh_is_created_manually`.

## Flow 3 — Manual variant creation and internal reference
User opens Product Variant form, sets `product_template_id` (custom widget field), and saves →
`product.product.write()`/`create()` [[03_models#ProductProduct]]: if `product_template_id` is set,
`vals['product_tmpl_id']` is synced from it and `sh_is_created_manually=True` is stamped →
duplicate-combination guard searches existing active variants with the same `combination_indices`
on the target template; if `write()` finds one it force-unlinks side-effect temp variants and raises
`UserError` (with an explicit `cr.commit()` first so the cleanup isn't rolled back by the raise) →
once the attribute combination (`product_template_attribute_value_ids`) is set and
`self.env.company.sh_product_int_ref_gen` is enabled, `_custom_default_code()` /
inline default_code logic builds `default_code` from attribute value names, truncated to
`sh_pdt_attr_digit` chars each, joined by `sh_pdt_new_seq_sep`, skipping any attribute whose
parent-value condition (`sh_parent_attribute`/`sh_parent_value`) is already satisfied by the
selected parent value (redundancy avoidance) → `product.default_code` is set uppercased.

## Flow 4 — Specification tab auto-population
Any write to `product_template_attribute_value_ids`, `attribute_line_ids`, or `active` on a
`product.product`, or a `read()` that includes `sh_spec_line_ids`, triggers
`_compute_sh_spec_lines()` [[03_models#ShProductSpecification]] which clears
(`(5, 0, 0)`) and rebuilds `sh.product.variant.spec.line` rows — one per PTAV, showing
attribute name + `product_attribute_value_id.description`. This is shown read-only next to a
free-editable `sh_extra_spec_line_ids` table on the variant form's "Specification" tab
([[04_views_xml#product_views.xml]]).

## Flow 5 — Duplicating a product template
User duplicates a template →
`product.template.copy()` [[03_models#ProductTemplate]]: strips `attribute_line_ids` from the copy
vals, sets `sh_skip_variant_creation=True` context (so `_create_variant_ids` no-ops entirely) →
`super().copy()` creates the bare new template →
manually recreates each attribute line: copies the shared `product.attribute` record
(re-stamping `sh_product_tmpl_id` to the new template), maps old attribute values to new ones
by name, creates a new `product.template.attribute.line` with `sh_skip_resequence`/`sh_keep_sequence`
context to preserve original ordering →
restores parent/child hierarchy on the new lines by matching old `parent_attribute_value_id` to
the newly created PTAV with the same attribute+value name →
copies BOMs at template level only (`product_id=False`) via `_copy_duplicate_boms()` — never
per-variant, since the duplicate intentionally has **zero** variants →
copies variant "extra data" (`sh_extra_spec_line_ids`, `product_template_id` link) via
`_copy_variant_extra_data()`, which is a no-op here since there are no variants yet on the copy.
