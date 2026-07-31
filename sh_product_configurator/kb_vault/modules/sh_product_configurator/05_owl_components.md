# Frontend JS Components
Status: [ACTIVE]
Back to [[00_overview]]

Note: this module mixes an OWL-era `patch()` component with two legacy `odoo.define()` modules (pre-OWL widget/mixin style). None are true OWL components with templates of their own — they patch existing Odoo JS objects.

## sale_product_field.js (OWL patch)
Status: [ACTIVE]
Purpose: Patches `SaleOrderLineProductField` (from `@sale/js/sale_product_field`) and `OptionalProductsModal` (from `@sale_product_configurator/js/product_configurator_modal`) so the configurator flow also works when the record being edited is a `product.product` directly (not just a sale order line).
Patches:
- `OptionalProductsModal.prototype._toggleDisable` — always keeps the primary confirm button enabled/clickable if the item is already `.in_cart`, overriding the standard "disable if combination impossible" behavior.
- `SaleOrderLineProductField.prototype._openProductConfigurator(mode)` — if `this.env.model.root.resModel == 'product.product'`: stores `sh_active_model` in `localStorage`, RPCs [[06_controllers#/sale_product_configurator/configure]] with the current PTAV/no-variant/custom-attribute selections, resolves/creates the product via `selectOrCreateProduct` (from `sale.VariantMixin`), builds `this.rootProduct`, opens a fresh `OptionalProductsModal`. On `confirm`, calls `shGetAndCreateSelectedProducts()` (see below) then RPCs [[06_controllers#/unlink/product_variant]] to clean up the temp product. On `closed` without confirm (and not `mode == 'edit'`), resets the record's product fields. Falls back to `this._super(mode)` for non-`product.product` models.
RPC: calls [[06_controllers#/sale_product_configurator/configure]], [[06_controllers#/unlink/product_variant]]
State: uses `localStorage` (`sh_active_model`, `sh_productId`) to pass flow state across the RPC/modal boundary since the modal is a separate legacy widget system.

## product_configurator_modal.js (legacy `.include()`)
Status: [ACTIVE]
Purpose: Extends `OptionalProductsModal` (via `odoo.define('website_sale_product_configurator.OptionalProductsModal', ...)`) to fetch the "advanced" configurator markup when editing a `product.product`, and to manage nested attribute group visibility.
Key methods:
- `willStart()` — if `localStorage.getItem('sh_active_model') == 'product.product'`, fetches `/sale_product_configurator/show_advanced_configurator` [[06_controllers#_show_advanced_configurator]] instead of the default content, then clears the `sh_active_model` flag. Otherwise defers to `parentInit`.
- `shGetAndCreateSelectedProducts(sh_product_id)` — iterates `.js_product.in_cart` DOM rows, extracts quantity/custom/no-variant attribute data, calls `updateProduct()` (from `variant_mixin.js`) per row to persist the combination, and returns the assembled product list.
- `_onModalReady()` — parses the `#attribute_parent_map` hidden input (JSON), and wires: initial hide of every child `.variant_attribute` group whose id appears in the map, initial reveal of children whose parent already has a value selected (recursive via `showChildren`), and a `change` listener on `input[name^="ptal-"]`/`select[name^="ptal-"]` that hides all descendants of the changed attribute then re-shows only the branch matching the newly selected value (`hideChildren`/`showChildren`, both recursive).
RPC: calls `/sale_product_configurator/show_advanced_configurator` [[06_controllers#_show_advanced_configurator]]
See also: [[04_views_xml#templates.xml]] for the `#attribute_parent_map` hidden input this reads.

## variant_mixin.js (legacy `odoo.define`)
Status: [ACTIVE]
Purpose: Extends the standard `sale.VariantMixin` with a custom update path that targets an *existing* variant by id instead of always creating a new one.
Key methods:
- `VariantMixin.updateProduct($container, shProductId, productId, productTemplateId, useAjax)` — POSTs to `/update_product_variant` [[06_controllers#/update_product_variant]] with the container's currently-selected PTAV ids (via `VariantMixin.getSelectedVariantValues`) plus `sh_product_id`/`product_template_id`. Chooses ajax vs `_rpc` vs `this.rpc` depending on caller context (legacy widget vs OWL-compatible caller).
- `VariantMixin.shSelectOrCreateProduct(...)` — thin wrapper hitting the standard `/sale/create_product_variant` route (kept for parity/possible reuse; primary flow uses `updateProduct` instead).
RPC: calls [[06_controllers#/update_product_variant]]

## list_renderer_patch.js (OWL patch)
Status: [ACTIVE]
Purpose: Patches `ListRenderer.prototype.isSortable` so the `attribute_id` column on a `product.template.attribute.line` list is never sortable — sort order there must follow the hierarchy/sequence logic in [[03_models#ProductTemplateAttributeLine]], not alphabetic attribute name.
See also: [[04_views_xml#product_template_views.xml]] (same intent enforced XML-side via `sortable="0"`, this JS patch covers any list not using that specific inherited view).
