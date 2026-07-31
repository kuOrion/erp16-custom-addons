# Architecture
Status: [ACTIVE]
Back to [[00_overview]]

## Layers

```
Backend (Python models, server-side guards)
  product.attribute / product.attribute.value        [[03_models#ProductAttribute]]
  product.template (create/write/copy overrides)      [[03_models#ProductTemplate]]
  product.template.attribute.line (hierarchy+seq)      [[03_models#ProductTemplateAttributeLine]]
  product.template.attribute.value (sync child attrs)  [[03_models#ProductTemplateAttributeValue]]
  product.product (variant create/write, default_code) [[03_models#ProductProduct]]
  sh.product.variant.spec.line / extra.line            [[03_models#ShProductSpecification]]
  res.company / res.config.settings (int. ref config)  [[03_models#ResConfigSettings]]
        |
        | XML-RPC / ORM calls, view actions
        v
Views (XML) — form/tree inherits on product.template, product.product,
  product.attribute, product.template.attribute.value, sale.order,
  res.config.settings                                  [[04_views_xml]]
        |
        | QWeb templates rendered server-side for the sale/website configurator popup
        v
Controllers — /unlink/product_variant, /update_product_variant (JSON-RPC),
  inherited /sale_product_configurator/configure                [[06_controllers]]
        |
        | rendered HTML returned to browser
        v
Frontend JS (legacy odoo.define + OWL patch) — patches OptionalProductsModal
  and SaleOrderLineProductField to route configurator opens through
  product.product context, show/hide nested attribute groups, and call
  the custom controllers                                [[05_owl_components]]
```

## How the layers connect
1. A user opens the product configurator (from a Sale Order line, or directly editing a `product.product` variant). The frontend JS (`sale_product_field.js`) detects whether the active model is `product.product` and, if so, stores that in `localStorage` and fetches the configurator HTML via RPC to `/sale_product_configurator/configure`, an inherited controller route (`controllers/main.py`) that adds `attribute_parent_map` (JSON of child→parent attribute/value id pairs) to the render context.
2. The returned QWeb template (`views/templates.xml`, `views/variant_templates.xml`) recursively renders attribute lines (`sh_product_configurator.render_nested_attributes`), nesting children under parents using `sh_parent_attribute`.
3. `product_configurator_modal.js` (legacy `.include()` patch on `OptionalProductsModal`) reads `sh_active_model` from `localStorage` to branch into the "advanced configurator" flow and wires `_onModalReady` to hide/show `.variant_attribute` groups client-side as the user picks parent values, using the same `attribute_parent_map`.
4. On confirm, the modal calls the custom JSON controllers in `controllers/product_configurator.py`: `/update_product_variant` writes the chosen PTAV combination onto the existing `product.product` (replace-all via `(6,0,ids)`), and `/unlink/product_variant` cleans up temporary/unsaved variant records that the flow created as side effects.
5. All of this rides on top of standard Odoo variant/attribute models, which are inherited (not replaced) in `models/`. The heaviest override is `product.template._create_variant_ids`, which intentionally skips a standard Odoo step (see [[03_models#ProductTemplate]]).

## Entry points
- Sale Order line "Configure" button → `sale_product_field.js` → `/sale_product_configurator/configure` → QWeb modal → `/update_product_variant` or `/unlink/product_variant`.
- Product Template form → Attributes tab → creating an attribute line triggers `product.template.attribute.line.create()` hierarchy/sequence logic ([[03_models#ProductTemplateAttributeLine]]).
- Product Variant (`product.product`) form → "Product" field (`product_template_id`) lets a user manually bind/create a variant against a template; triggers `product.product.create()`/`write()` duplicate-guard and `default_code` generation.
- Company Settings → "Product Internal Reference Generator Feature" → `generate_int_ref()` button re-runs `_custom_default_code()` for every product.
- Duplicating a product template (Action → Duplicate) → `product.template.copy()` override.
