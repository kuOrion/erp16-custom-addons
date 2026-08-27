# Architecture
Status: [ACTIVE]
Back to [[00_overview]]

## Layers

```
Backend (Python models only — no controllers, no JS/OWL in this module)
  mrp.production (serial assign/release action, main-MO compute, name suffixing) [[03_models#MrpProduction]]
  product.template (auto-assign toggle)                                   [[03_models#ProductTemplate]]
  res.company / res.config.settings (Type1/Type2 prefix config)           [[03_models#ResConfigSettings]]
  sale.order (MO smart-button context tweak)                              [[03_models#SaleOrder]]
  sh.finished.product (produced qty + lots per MO)                        [[03_models#ShFinishedProduct]]
  sh.serial.reassign.log (new, v16.0.6 — release/reuse history)           [[03_models#ShSerialReassignLog]]
  stock.location (should_bypass_reservation override)                     [[03_models#StockLocation]]
  stock.lot (prefix-aware next-serial lookup, released-pool query)        [[03_models#StockLot]]
  stock.move (lot range fields, custom reservation logic)                 [[03_models#StockMove]]
  stock.move.line (selection helper field, currently unused by UI)        [[03_models#StockMoveLine]]
  stock.picking / stock.picking.type (source MO/transfer, custom action_assign, name suffix) [[03_models#StockPicking]]
        |
        | view inherits only — no custom controllers, no JS assets in manifest
        v
Views (XML) — form inherits on mrp.production, product.template,
  res.config.settings, stock.move, stock.move.line, stock.picking, stock.lot;
  new tree/form/action for sh.finished.product                [[04_views_xml]]
        |
        | scheduled background jobs
        v
ir.cron — 2 daily jobs re-normalizing MO and internal-transfer display names [[07_csv_data]]
```

## How the layers connect
1. Company Settings (`res.config.settings`, related to `res.company`) hold the Type 1 / Type 2 prefix
   configuration. These are read by `mrp.production.action_assign_serial_number()` at click time.
2. `product.template.sh_auto_assign_serial_no` (default True) is a per-product opt-out flag, surfaced
   on the product form and related onto `mrp.production` as a readonly indicator
   (`sh_auto_assign_serial_no`) controlling required-ness of `sh_serial_no_type`/`sh_produce_qty` on the
   MO form.
3. `mrp.production.action_assign_serial_number()` is the central orchestration method: **first**
   drains the released-serial pool (`stock.lot.sh_get_released_serials()`, lowest number first,
   [ADDED: v16.0.6]) onto as many sibling MOs as possible, logging a `reuse` event per one; **then**,
   for any remaining quantity, resolves the next serial (via `stock.lot.sh_get_next_serial` or a
   fresh `ir.sequence`), inserts a `stock.assign.serial` wizard record via raw SQL, calls that
   wizard's standard `generate_serial_numbers_production()` + `apply()`, and marks done as many
   remaining sibling split MOs as needed; finally accumulates results onto `sh.finished.product` and
   appends a `(qty)` suffix to the MO's own name.
4. `stock.lot.sh_config_prifix_type` tags every lot with which prefix type produced it, closing the
   loop so `sh_get_next_serial` can find "the last lot of this type" directly instead of relying purely
   on the `ir.sequence` counter (which is per-code, not filterable by lot state).
5. [ADDED: v16.0.6] `mrp.production.action_release_serial_number()` detaches a lot from its MO
   (clears `lot_producing_id`, strips it from `sh.finished.product.lot_ids`), sets
   `stock.lot.sh_is_released=True`, and logs a `release` event to `sh.serial.reassign.log`. The lot
   record itself is never deleted — only the association is removed, matching the client's explicit
   "keep the serial number so we can use it for another product" requirement.
6. On the delivery/internal-transfer side, `stock.picking.sh_source_mo_id` /
   `sh_internal_picking_id` are informational hints a user sets; `stock.picking.action_assign()` (full
   override, calls `super()` first then re-runs custom reservation logic) and
   `stock.move._action_assign()` (also overridden, "SHSMART CODE" blocks) both read these hints to
   preferentially reserve `stock.quant`s carrying the referenced lots before generic reservation logic
   would apply.
7. `mrp.production._auto_update_mo_sequence()` and `stock.picking.sh_update_internal_transfer_name()`
   are invoked daily by [[07_csv_data]] cron jobs to keep the `(qty)` name suffix correct even if
   something updated quantities without going through the normal write-time hooks.

## Entry points
- MO form → "Assign Serial No" button (visible only on the main MO of a split group, hidden once total
  quantity already matches) → `action_assign_serial_number()` (now pool-aware, v16.0.6).
- MO form → "Release Serial No" button [ADDED: v16.0.6] (admin-only, visible only when a serial is
  assigned) → `action_release_serial_number()`.
- MO form → picking a `sh_serial_no_type` → `_onchange_sh_serial_no_type` optionally shows a
  company-configured confirmation warning.
- Company Settings → Manufacturing tab → "MO Assign Serial No." section → configures Type 1/Type 2.
- Delivery/Internal Transfer form → `sh_source_mo_id` or `sh_internal_picking_id` field → drives
  `action_assign()` on Reserve.
- Stock Move "Detailed Operations" popup → `start_lot_id`/`end_lot_id` + "Update" button →
  `sh_action_update_move_line()` prunes move lines outside the lot id range.
- MO form / Serial Number (Lot) form → "Serial No History" / "Release History" tabs [ADDED: v16.0.6,
  admin-only] → read-only view of `sh.serial.reassign.log`.
- Daily cron (02:00) → `_auto_update_mo_sequence()`, `sh_update_internal_transfer_name()`.
