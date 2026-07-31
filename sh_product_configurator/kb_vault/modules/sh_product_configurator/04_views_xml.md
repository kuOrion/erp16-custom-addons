# Views (XML)
Status: [ACTIVE]
Back to [[00_overview]]

## sale_order_views.xml
- `view_order_form_inherit_sh_product_configurator` (inherits `sale.view_order_form`, priority 100) — restricts the `product_template_id` tree column to `base.group_system` only.
- `view_order_form_inherit_sale_product_configurator` (inherits `sale_product_configurator.sale_order_view_form`, priority 100) — makes the `product_id` tree column visible by default (`optional="show"`).
Related model: [[03_models#ProductProduct]]

## product_template_views.xml
- `product_template_only_form_view_inherit_sh_product_configurator` (inherits `product.product_template_only_form_view`) — on the Attributes tab tree: locks `attribute_id` and `value_ids` selection (`domain=[('id','=',-1)]`, i.e. effectively disables picking existing shared attributes/values — everything must be created fresh per template) and disables column sorting on `attribute_id`; adds a drag `sequence` handle column before `attribute_id`.
Related model: [[03_models#ProductTemplateAttributeLine]], see also [[05_owl_components#list_renderer_patch.js]] for the JS-side sort disabling of this same column.

## product_views.xml
- `product_normal_form_view_inherit` (inherits `product.product_normal_form_view`) —
  - Before the `options` div: adds `product_template_id` (custom widget `sol_product_many2one`, domain excludes self-template, invisible unless the record is saved and `show_product_template_field`).
  - After `pricing` div: adds invisible technical fields `product_custom_attribute_value_ids`, `product_no_variant_attribute_value_ids`, `product_template_attribute_value_ids` (kept on the view so they're loaded/available to JS/RPC even though not shown).
  - New notebook page **"Specification"**: two-column layout — left (`col-5`) read-only `sh_spec_line_ids` tree (Attribute/Description), right (`col-6`) editable `sh_extra_spec_line_ids` tree (Name/Value).
Related model: [[03_models#ProductProduct]], [[03_models#ShProductSpecification]]

## prodcut_attributes_views.xml
- `form_inherit_product_attribute` (inherits `product.product_attribute_view_form`) — after `create_variant`: adds a group showing `sh_parent_attribute`/`sh_parent_value` (both readonly — set programmatically, not hand-edited), `sh_product_tmpl_id`, invisible `sh_is_custom_attribute`; on the values tree, adds `description` as an optional column.
Related model: [[03_models#ProductAttribute]]

## product_template_attribute_value_views.xml
- `product_template_attribute_value_view_form_inherit_sh_product_configurator` (inherits `product.product_template_attribute_value_view_form`) — exposes `product_tmpl_id` invisibly; adds `description` before `exclude_for`; adds a **"Sub-Attributes"** section with a `child_attribute_line_ids` one2many editable tree — this is the actual UI for building the parent→child hierarchy from a specific PTAV. The nested `attribute_id`/`value_ids` fields are also domain-locked (`[('id','=',-1)]`) to force fresh creation, and a "Configure" button opens `action_open_attribute_values` (standard Odoo action, restricted to `product.group_product_variant`).
- `product_template_attribute_value_view_tree_inherit_sh_product_configurator` (inherits `product.product_template_attribute_value_view_tree`) — adds `description` as optional column after `name`.
Related model: [[03_models#ProductTemplateAttributeValue]]

## res_config_setting_ref_view.xml
- `sh_inherit_view_form_config_setting` (inherits `base_setup.res_config_settings_view_form`) — after the `companies` div, adds a "Product Internal Reference Generator Feature" section: toggle `sh_product_int_ref_gen`, conditional (only visible when toggle is on) fields `sh_pdt_seq_sep`, a "GENERATE INTERNAL REFERENCE FOR ALL PRODUCT" button (`generate_int_ref`), `sh_pdt_attr_digit`, `sh_pdt_new_seq_sep`.
Related model: [[03_models#ResConfigSettings]]

## templates.xml
- `configure_optional_products_inherit` (inherits `sale_product_configurator.configure_optional_products`) — injects a hidden `<input id="attribute_parent_map">` carrying the JSON parent/child map before the products table; conditionally hides the Quantity and Price columns/rows (`td-qty`/`td-price`/`.o_total_row`) when `sh_active_model == 'product.product'` (a plain variant edit doesn't need quantity/price UI).
Related controller: [[06_controllers#/sale_product_configurator/configure]]

## variant_templates.xml
- `sh_product_configurator.render_nested_attributes` — recursive QWeb template rendering one `product.template.attribute.line` (`select`/`radio`/`pills`/`color` display types, mirroring standard Odoo markup) and then recursing into any `child_lines` whose attribute's `sh_parent_attribute` matches the current line's attribute — this is what produces the nested `<ul><li>` hierarchy in the storefront/configurator variant picker.
- `sh_product_configurator_nested_attributes` (inherits `sale.variants`) — replaces the standard flat attribute list (`//ul[1]`) with a call into `render_nested_attributes`, starting from only the top-level lines (`not l.attribute_id.sh_parent_attribute`).
Related model: [[03_models#ProductTemplateAttributeLine]], [[03_models#ProductAttribute]]
