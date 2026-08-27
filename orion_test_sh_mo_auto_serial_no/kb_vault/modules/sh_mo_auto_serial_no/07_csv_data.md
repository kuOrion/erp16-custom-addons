# CSV / Data
Status: [ACTIVE]
Back to [[00_overview]]

## security/ir.model.access.csv
Two access-rights records:
- `access_sh_finished_product` — full CRUD on `sh.finished.product` for `base.group_user` (any
  internal user). No group-based restriction on this model despite it holding production/lot data —
  see [[09_known_issues]].
- `access_sh_serial_reassign_log` — [CHANGED: v16.0.6, fifth UAT round] read-ONLY
  (`perm_read=1, perm_write=0, perm_create=0, perm_unlink=0`) for `base.group_system`. Originally
  granted write+create to admins; tightened per explicit client request that history must not be
  manually editable by anyone, including admins, so it stays a trustworthy audit trail. The module's
  own two write sites (`MrpProduction._sh_log_serial_event()` and the `stock.assign.serial`
  override's `_assign_serial_numbers()`) now call `.sudo()` on the create, since a plain ACL-bound
  `create()` would otherwise be blocked by this same restriction — see [[03_models#ShSerialReassignLog]].

## data/ir_cron.xml
Two daily scheduled actions, both firing at 02:00 with `numbercall=-1` (repeat indefinitely) and
`doall=False` (missed runs are not backfilled):
- `ir_cron_auto_update_main_mo_sequence` — targets `mrp.production`, runs
  `model._auto_update_mo_sequence()` [[03_models#MrpProduction]]. See [[02_data_flow#Flow 4]].
- `ir_cron_sh_update_internal_transfer_name` — targets `stock.picking` (referenced via
  `stock.model_stock_picking`), runs `model.sh_update_internal_transfer_name()`
  [[03_models#StockPicking]]. See [[02_data_flow#Flow 4]].

No other seed/master data ships with this module.
