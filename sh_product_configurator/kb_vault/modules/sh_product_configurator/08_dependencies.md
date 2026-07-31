# Dependencies
Status: [ACTIVE]
Back to [[00_overview]]

From `__manifest__.py`:

- **sale** — base sale order/order line models this module extends (`sale.order` view inherits).
- **sale_management** — sale management app dependency chain (quotation templates etc.); pulled in alongside `sale`.
- **sale_product_configurator** — the module whose `OptionalProductsModal`, `ProductConfiguratorController`, `VariantMixin`, and `configure`/`optional_products_modal` QWeb templates are patched/inherited throughout this module. This is the core integration point — nearly every JS/controller/view file here inherits from something in `sale_product_configurator`.
- **mrp** — needed for `mrp.bom`, which `product.template._copy_duplicate_boms()` reads/copies on template duplication.

Implicit dependency (not declared, used via `import`): `website_sale` — `controllers/main.py` imports `from odoo.addons.website_sale.controllers import main` but that import is unused in the file body beyond the import statement itself. If `website_sale` is not installed this import will fail at load time — see [[09_known_issues]].

## Monkey-patches / overrides of base behavior
- `product.template._create_variant_ids()` — full reimplementation, not calling `super()`; diverges from standard Odoo by skipping the single-value-push-onto-existing-variant step. See [[03_models#ProductTemplate]].
- `product.template.product_template_variant_value_ids` domain widened from standard `[('attribute_line_id.value_count', '>', 1)]` to `[]`.
- `OptionalProductsModal.prototype._toggleDisable` (OWL patch) — overrides standard combination-possible/impossible button-disable behavior.
- `ListRenderer.prototype.isSortable` (OWL patch) — globally disables sorting for one specific column/model combination.
