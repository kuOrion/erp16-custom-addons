# CSV / Data
Status: [ACTIVE]
Back to [[00_overview]]

## security/ir.model.access.csv
No seed business data — only access rights records:
- `access_sh_product_variant_spec_line` — full CRUD on `sh.product.variant.spec.line` for `base.group_user`.
- `access_sh_product_variant_extra_line` — full CRUD on `sh.product.variant.extra.line` for `base.group_user`.

Note: no access rows exist for `sh.product.variant.extra.line`'s counterpart restrictions beyond `base.group_user` — any internal user can read/write these spec lines directly via ORM even though most model-level create() overrides in this module gate on `base.group_system`. See [[09_known_issues]].

No other CSV/data files ship with this module — all attribute/value/company config records are created live by users/admins, not seeded.
