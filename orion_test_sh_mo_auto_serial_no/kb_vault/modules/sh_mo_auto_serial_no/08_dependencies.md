# Dependencies
Status: [ACTIVE]
Back to [[00_overview]]

From `__manifest__.py`:

- **stock** — `stock.lot`, `stock.move`, `stock.move.line`, `stock.picking`, `stock.picking.type`,
  `stock.quant`, `stock.location` are all inherited/used directly; this is the module's heaviest
  integration surface. `stock.view_production_lot_form` is also now inherited (v16.0.6).
- **mrp** — `mrp.production` is the primary model extended; `procurement_group_id.mrp_production_ids`
  (the split-MO grouping) and `button_mark_done()` are both standard MRP concepts this module drives,
  including the [ADDED: v16.0.6] pool-draining pass which also calls `button_mark_done()` directly.
- **product** — `product.template.tracking`/`sh_auto_assign_serial_no` gating.
- **sale_mrp** — needed for the sale-order ↔ MO linkage that `sale.order.action_view_mrp_production()`
  overrides.
- **sale_management** — pulled in alongside `sale_mrp` for the sale order app dependency chain.

Implicit dependency (used but not declared): `stock.assign.serial` — the standard "Assign Serial
Numbers" wizard model, whose table `action_assign_serial_number()` inserts into directly via raw SQL,
and whose `generate_serial_numbers_production()`/`apply()` methods it calls. This model ships with
`stock` (specifically via `mrp`'s extension of the stock wizard for production context) so the
dependency chain covers it, but the module never references it as an explicit ORM dependency beyond the
raw SQL table name — schema changes to that table in a future Odoo core update would silently break the
`INSERT` statement. See [[09_known_issues]]. As of v16.0.6 this raw-SQL path is only exercised for the
*remaining* quantity after the released pool is drained — a batch fully covered by released serials
never touches it at all.

## Monkey-patches / overrides of base behavior
- `stock.move._action_assign()` — full reimplementation, not calling `super()`. Diverges from standard
  Odoo reservation by inserting MO-lot/transfer-lot preferential-reservation logic ("SHSMART CODE"
  blocks). See [[03_models#StockMove]].
- `stock.location.should_bypass_reservation()` — widens the standard bypass-reservation condition set.
- `stock.picking.action_assign()` — calls `super()` then manually re-does reservation for
  outgoing/internal pickings with a source hint set.
- `stock.picking_type._get_action()` — modifies action context (`default_immediate_transfer`,
  `default_company_id`) beyond the standard implementation.
- `mrp.production.action_assign_serial_number()` — [CHANGED: v16.0.6] additive change, not a
  monkey-patch of core Odoo, but worth noting here: it now conditionally skips calling into
  `stock.assign.serial` entirely if the released pool fully covers the requested quantity.
