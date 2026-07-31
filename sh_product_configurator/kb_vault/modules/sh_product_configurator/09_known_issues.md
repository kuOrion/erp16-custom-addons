# Known Issues
Status: [ACTIVE]
Back to [[00_overview]]

## Issue: `N`/`R`-prefix bypasses product name uniqueness entirely
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Updated: 2026-07-14 — extended from `N`-only to `N`/`R` per user request, see [[changelog/v16.0.12]]
Description: `product.template._should_skip_duplicate_name_validation()` exempts any name starting with `N` or `R` (case-insensitive) from the duplicate-name check, both on `create()` and `write()`/rename, and drives the "skip variant/BOM duplication" path in `copy()`. Originally added (16.0.10/16.0.11) for `N` only; extended to also match `R` with identical behavior. It is intentional business logic, but it means two entirely unrelated products both named e.g. "N-Widget" or "R-Widget" can coexist, and a rename to any `N...`/`R...` name always succeeds even if it collides with an existing exempted-prefix product.
Workaround: none — by design. Flag to the user if asked to "fix" duplicate names, since this may be expected behavior tied to ticket work, not a bug.
See changelog: [[changelog/v16.0.11]], [[changelog/v16.0.12]]

## Issue: `_show_advanced_configurator` / `configure()` re-render pattern is fragile
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `controllers/main.py#configure()` calls `super().configure(...)` purely to reuse its side effects/validation, discards the returned HTML, and manually re-derives the same context to re-render with `attribute_parent_map` added. The code's own comment calls this "a bit hacky." Any future change to the base `sale_product_configurator` controller's internal context-building logic (fields added/removed) will silently desync from this override since the re-derivation is duplicated, not delegated.
Workaround: none currently; re-derivation logic must be manually kept in sync with `sale_product_configurator`'s controller on every Odoo/module upgrade.

## Issue: unused `website_sale` import may hard-fail install if not present
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `controllers/main.py` has `from odoo.addons.website_sale.controllers import main` at module level but never references `main` afterward. `website_sale` is not listed in `__manifest__.py` `depends`. If `website_sale` isn't installed in a given database, this import raises `ImportError` at module load, breaking `sh_product_configurator` entirely.
Workaround: ensure `website_sale` is installed wherever this module is installed, or remove the dead import.

## Issue: broad "any field changed" trigger for `_sync_child_attributes`
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `product.template.attribute.value.write()` calls `_sync_child_attributes()` whenever `'child_attribute_line_ids' in vals or any(field in vals for field in self._fields)` — since `self._fields` includes essentially every field on the model, this condition is true for nearly any write, not just ones affecting the hierarchy. Not currently causing correctness bugs (the sync method itself is idempotent/cheap for templates with no children), but it's a performance smell worth simplifying if this model sees heavy write volume.
Workaround: none needed today; note for future refactor.

## Issue: `generate_int_ref()` has no batching for large catalogs
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `res.config.settings.generate_int_ref()` does `self.env['product.product'].search([])` (all variants, no domain/limit) then loops calling `_custom_default_code()` per product with no `cr.commit()` between batches. On a large product catalog this risks long transactions/timeouts. Company coding-standards doc (`CLAUDE.md`) explicitly calls for batch processing + explicit commits for bulk operations — this method does not follow that pattern.
Workaround: none currently; recommend batching if this becomes a real timeout in practice.

## Issue: no access rule differentiates read vs write on spec/extra-line models
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `ir.model.access.csv` grants full CRUD on `sh.product.variant.spec.line` and `sh.product.variant.extra.line` to `base.group_user` (any internal user), even though most create-path guards elsewhere in the module restrict to `base.group_system`. A regular user can freely edit `sh_extra_spec_line_ids` from the variant form (this may be intended — it's the "manual/free-text" table) but can also directly manipulate `sh.product.variant.spec.line` (the auto-computed table) via ORM/API calls bypassing the UI, since there's no model-level guard there.
Workaround: none; likely acceptable since the compute overwrites spec lines on next recompute trigger, but flag if data integrity on that table becomes a concern.
