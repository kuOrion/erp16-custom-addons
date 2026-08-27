# Models
Status: [ACTIVE]
Back to [[00_overview]]

## MrpProduction (mrp.production) — inherit
File: `models/mrp_production.py`
Status: [ACTIVE]
Purpose: Central orchestration for serial-number assignment/release across a group of split MOs, plus
the "main MO" concept and live name-suffixing.
Key Fields:
- `sh_serial_no_type` (Selection type1/type2) — which company-configured prefix scheme to use
- `sh_finished_product_ids` (One2many sh.finished.product) — accumulated produced qty/lots for this MO
- `sh_produce_qty` (Float) — how many split MOs to mark done in one "Assign Serial No" click
- `sh_auto_assign_serial_no` (related to `product_id.sh_auto_assign_serial_no`) — drives required-ness
  of `sh_serial_no_type`/`sh_produce_qty` on the form
- `sh_main_mo` (Boolean, compute, store=True) — True only for the lowest-id MO in a
  `procurement_group_id`'s split-MO set
- `sh_total_qty` (Integer) — mirrors `product_qty` via onchange, used for serial-button visibility
- `sh_is_serial_btn_invisible` (Boolean, compute) — True once `sh_total_qty` already equals the
  produced quantity recorded on `sh_finished_product_ids[0]`
- `sh_serial_history_ids` (Many2many sh.serial.reassign.log, compute) — [ADDED: v16.0.6] all
  release/reuse log rows where this MO appears as either `from_production_id` or `to_production_id`;
  computed rather than a real relation since one lot can pass through many MOs over time and there is
  no single natural inverse field.
Critical Methods:
- `_compute_sh_main_mo()` — for the group `self.procurement_group_id.mrp_production_ids`, sorts by id
  and flags only the first as main; every other sibling gets `sh_main_mo=False`. Note: this walks
  `self.procurement_group_id` (not each record's own group) inside a loop over `self` — see
  [[09_known_issues]] for a correctness caveat when computing over multiple MOs from different groups
  at once.
- `_compute_sh_serial_history_ids()` — [ADDED: v16.0.6] searches `sh.serial.reassign.log` for rows
  referencing this MO from either side.
- `_onchange_product_qty()` — mirrors `product_qty` into `sh_total_qty` (used only for visibility calc,
  not persisted business logic).
- `_onchange_sh_serial_no_type()` — surfaces a company-configured confirmation warning message when a
  type is selected, if one is configured.
- `write()` — whenever `lot_producing_id` is written and `sh_serial_no_type` is set, stamps
  `sh_config_prifix_type` on that lot from the matching company prefix. This is how a lot "remembers"
  which type generated it, feeding back into `stock.lot.sh_get_next_serial`.
  [CHANGED: seventh UAT round] Also, whenever `lot_producing_id` is written to a lot that is
  currently `sh_is_released=True`, clears the flag and logs a `reuse` event — regardless of WHICH
  code path performed the write. This closes the gap where assigning a serial via the **standard**
  Odoo Lot/Serial Number field (bypassing this module's Assign/Reassign buttons entirely) left
  `sh_is_released=True` on an actively-in-use serial, risking it being offered to a second MO by the
  pool logic later — found live via a user manually assigning a released serial through the standard
  field, confirmed by the flag still reading `True` afterward and no history row being created. A
  `search()`-based `already_logged` guard prevents a double log row on the rare path where this
  module's own code already writes a `reuse` entry for the same write (verified via ORM test: no
  double-logging occurs across `action_reassign_serial_number()`'s two branches or the batch
  `stock.assign.serial` path, since none of those write to an already-released lot AND explicitly
  log in the same call — but the guard exists in case a future call site does).
- `action_assign_serial_number()` — see [[02_data_flow#Flow 1]] and [[02_data_flow#Flow 5]] for the
  full sequence. [CHANGED: v16.0.6] released serial NAMES (lowest first) are now pre-filled into the
  `stock.assign.serial` row's `serial_numbers` text at INSERT time, and
  `generate_serial_numbers_production()` is only called to append newly generated names for the
  remaining quantity (skipped entirely if the released pool covers the whole batch); the actual lot
  reuse happens inside the module's `stock.assign.serial` override
  [[03_models#StockAssignSerialNumbers]]. Also normalizes `sh_serial_no_type` on all pending sibling
  MOs before the wizard runs, so `write()`'s prefix-tagging never stamps the wrong type.
  > Previously: always generated the full `sh_produce_qty` as brand-new serials, ignoring any
  released ones — see [[changelog/v16.0.6]]
- `action_release_serial_number()` — [ADDED: v16.0.6] admin-only. If `state == 'done'`, first calls
  `_sh_reset_done_mo_to_draft()` to reverse the MO to `draft` (see [[02_data_flow#Flow 5]] for the
  full field-by-field breakdown — required because core Odoo blocks lot changes once real stock moves
  reference it). [CHANGED: seventh UAT round] Also unlinks every `stock.move.line` still referencing
  the lot (state-reset alone leaves the rows in place, which still trips core's product-change guard
  on later cross-product reassignment) and every zero-quantity `stock.quant` referencing it (otherwise
  those empty rows silently block a later manual delete of the lot via `stock_quant_lot_id_fkey`, even
  though there is no real stock left — found live via a user attempting to bulk-delete 20 released
  lots from Inventory > Lots/Serial Numbers). Then detaches the MO's `lot_producing_id`, strips it
  from linked `sh.finished.product.lot_ids`, marks the lot `sh_is_released=True`, logs the event.
- `_sh_reset_done_mo_to_draft()` — [ADDED: v16.0.6, third UAT round] resets a `done` MO's moves, move
  lines, workorders, quantities, and pickings to their pre-completion state so `_compute_state` lands
  on `draft`. Reference: `custom/addons/sh_mrp_cancel`'s Cancel-to-Draft flow — that flow only, no
  other logic adopted. See [[02_data_flow#Flow 5]] for the exact field list.
- `_sh_unreseve_qty()` — [ADDED: v16.0.6, third UAT round] reverses quant quantities for a set of
  moves' move lines (adds back at source location, subtracts at destination), used by
  `_sh_reset_done_mo_to_draft()`. Reference: `custom/addons/sh_mrp_cancel`.
- `action_reassign_serial_number()` — [ADDED: v16.0.6, second UAT round] admin-only, one-click (no
  wizard, per client). Assigns the lowest released serial for the MO's type prefix via
  `_sh_take_released_lot()`, else creates a new lot at `_sh_next_free_serial_number()`. Blocks if the
  MO already holds a serial (must Release first) or has no Serial No Type.
- `_sh_take_released_lot(lot)` — [ADDED: v16.0.6, second UAT round; CHANGED: fourth UAT round]
  consume helper for the one-click Reassign button: repoints the SAME lot record's `product_id` when
  it differs from the MO's product (safe — a released lot has no stock moves against it, see
  [[02_data_flow#Flow 5]] cross-product reuse rule), rather than creating a duplicate lot per product.
  The automatic batch path applies the identical rule independently inside the `stock.assign.serial`
  override [[03_models#StockAssignSerialNumbers]].
- `_sh_next_free_serial_number(prefix, padding)` — [ADDED: v16.0.6, second UAT round] returns
  max-numeric-suffix + 1 across all lots whose NAME starts with the prefix (tag-independent); used to
  anchor fresh `ir.sequence` numbering and Reassign's new-lot creation so numbering never restarts or
  collides.
- `_sh_log_serial_event(lot, from_production, to_production, action)` — [ADDED: v16.0.6] shared
  helper creating one `sh.serial.reassign.log` row; used by `action_release_serial_number()`,
  `action_reassign_serial_number()`, and `_sh_take_released_lot()` (the batch path logs directly in
  the `stock.assign.serial` override).
- `action_mass_release_serial_number()` / `action_mass_reassign_serial_number()` — [ADDED: v16.0.6,
  third UAT round] multi-record list-view versions: loop over `self`, filtering to only the records
  that actually have (release) or lack (reassign) a serial, calling the existing single-record
  `ensure_one()` methods per record — so selecting a mixed batch in the MO list and running the mass
  action from **Action ▸ Release/Reassign Serial No** silently skips records that don't apply instead
  of erroring the whole selection out.
- `_auto_update_mo_sequence()` (`@api.model`, cron target) — see [[02_data_flow#Flow 4]].
See also: [[02_data_flow#Flow 1]], [[02_data_flow#Flow 4]], [[02_data_flow#Flow 5]], [[09_known_issues]]

## ProductTemplate (product.template) — inherit
File: `models/product.py`
Status: [ACTIVE]
Purpose: Per-product opt-in/out of the auto-serial-assignment requirement.
Key Fields: `sh_auto_assign_serial_no` (Boolean, default=True) — shown on the product form only when
`tracking == 'serial'`; related onto `mrp.production` to drive field requirements there.

## ResCompany / ResConfigSettings — inherit
File: `models/res_config_settings.py`
Status: [ACTIVE]
Purpose: Company-level configuration for the two independent serial-numbering "types".
Key Fields (on `res.company`, related onto `res.config.settings`):
- `sh_number_of_degit_type1` / `sh_number_of_degit_type2` (Integer) — zero-padding width for each type's
  `ir.sequence`
- `sh_prefix_type1` / `sh_prefix_type2` (Char) — the literal prefix string; also doubles as the lookup
  key on `stock.lot.sh_config_prifix_type` and the new `sh_is_released` pool query
- `sh_confirirmation_message_type1` / `sh_confirirmation_message_type2` (Char) — optional warning shown
  when that type is selected on an MO
Note: field name spelling (`sh_confirirmation_message_...`) is a typo baked into the DB schema —
preserve it exactly in any code referencing these fields.

## SaleOrder (sale.order) — inherit
File: `models/sale_order.py`
Status: [ACTIVE]
Purpose: Makes the "Manufacturing Orders" smart button on a sale order default-filter to only main MOs.
Critical Methods: `action_view_mrp_production()` — calls `super()`, injects
`search_default_sh_main_mo: True` into the returned action's context.

## ShFinishedProduct (sh.finished.product) — new model
File: `models/sh_finished_product.py`
Status: [ACTIVE]
Purpose: One record per "main" MO, accumulating total produced quantity and the list of lots/serials
produced across all its split-MO siblings as they're marked done.
Key Fields: `name` (related `production_id.name`, store=True), `product_id`, `sh_serial_no` (Char,
currently unused — no code writes to it), `sh_product_qty` (Float), `location_id` (related
`production_id.location_dest_id`), `production_id`, `company_id`, `lot_id` (single, currently unused —
no code writes to it), `lot_ids` (One2many stock.lot via `sh_finished_product_id` — the actively used
field, also targeted by [ADDED: v16.0.6] release logic's `(3, lot.id)` unlink command)
Critical Methods: `sh_show_details_action()` — opens a form-view popup (`target='new'`) for the record.
See also: [[02_data_flow#Flow 1]], [[02_data_flow#Flow 5]], [[09_known_issues]] (unused fields)

## ShSerialReassignLog (sh.serial.reassign.log) — new model
File: `models/sh_serial_reassign_log.py`
Status: [ACTIVE]
Added: v16.0.6
Purpose: Audit trail of every serial-number release and automatic-reuse event, so an admin can trace
which MO a serial passed through over time. Implements the client's explicit history requirement from
TICKET/24830 follow-up.
Key Fields:
- `lot_id` (Many2one stock.lot, required, ondelete='cascade') — the serial the event concerns.
  **Caution**: `ondelete='cascade'` means hard-deleting a `stock.lot` silently destroys its entire
  history here too — see [[09_known_issues]] for a real instance of this trade-off being made
  deliberately during a data cleanup.
- `from_production_id` (Many2one mrp.production) — set for `release` events (the MO the serial was
  taken from); blank for `reuse` events
- `to_production_id` (Many2one mrp.production) — set for `reuse` events (the MO the serial was given
  to); blank for `release` events
- `action` (Selection: `release` / `reuse`, required)
- `user_id` (Many2one res.users, default current user)
No custom methods — purely a log model.
Access: [CHANGED: v16.0.6, fifth UAT round] **read-only for everyone, including admins** —
`perm_read=1`, `perm_write=0`, `perm_create=0`, `perm_unlink=0` for `base.group_system` (not
`base.group_user` at all). Per explicit client instruction: history must not be manually editable by
anyone, so it stays trustworthy. The module's own writes (`MrpProduction._sh_log_serial_event()` and
the `stock.assign.serial` override's `_assign_serial_numbers()`) call `.sudo()` on `create()` to
bypass this same restriction — a plain unprivileged `create()` from those methods would otherwise
also be blocked by the ACL. Do not remove those `.sudo()` calls without also loosening the ACL, or
the module's own release/reassign buttons will start raising Access Errors.
See also: [[02_data_flow#Flow 5]], [[03_models#MrpProduction]]

## StockAssignSerialNumbers (stock.assign.serial) — inherit
File: `models/stock_assign_serial.py`
Status: [ACTIVE]
Added: v16.0.6 (second UAT round)
Purpose: Makes core mrp's serial-assignment wizard released-serial-aware. Two full-body overrides of
core `odoo/addons/mrp/wizard/stock_assign_serial_numbers.py` (copied + minimally modified — re-sync
these if core changes on upgrade):
- `_onchange_serial_numbers()` — the "Existing Serial Numbers" duplicate check now excludes lots with
  `sh_is_released=True` (those names are *supposed* to be in the list for reuse).
- `_assign_serial_numbers()` — instead of blindly creating a new lot per name, each name matching a
  released lot is consumed: same product → the released lot record is reused directly; different
  product → a new lot with the same name is created for the correct product and the released one is
  retired. A `reuse` event is logged per reused name against the split production that received it.
See also: [[02_data_flow#Flow 5]], [[08_dependencies]]

## StockLocation (stock.location) — inherit
File: `models/stock_location.py`
Status: [ACTIVE]
Purpose: Widens which stock moves bypass normal reservation.
Critical Methods: `should_bypass_reservation()` — overridden to also return True for `usage in
('supplier', 'internal', 'customer', 'inventory', 'production')` (standard Odoo only bypasses for a
narrower set of cases) plus the existing `scrap_location`/`transit`-without-company conditions. Widens
the set of moves that skip normal quant-based reservation and instead just create move lines directly.
Note: class name in the file is `StockMove` despite inheriting `stock.location` — see
[[09_known_issues]].

## StockLot (stock.lot) — inherit
File: `models/stock_lot.py`
Status: [ACTIVE]
Purpose: Ties a lot to the prefix-type that generated it, provides "next serial" lookup based on that
lineage, and [ADDED: v16.0.6] tracks/serves released serials for reuse.
Key Fields: `sh_finished_product_id` (Many2one sh.finished.product), `sh_config_prifix_type` (Char) —
which prefix string generated this lot; `sh_is_released` (Boolean, default False, copy=False)
[ADDED: v16.0.6] — True while this serial is detached from any MO and available for reuse;
`sh_reassign_log_ids` (One2many sh.serial.reassign.log via `lot_id`) [ADDED: v16.0.6] — full
release/reuse history for this specific serial, shown on the lot's "Release History" tab.
Critical Methods:
- `sh_get_next_serial(company, product, prefix, serial_type)` (`@api.model`) — finds the most recent
  `stock.lot` for this company with matching `sh_config_prifix_type`, and if `product.tracking !=
  'none'`, returns `generate_lot_names(last_serial.name, 2)[1]` (standard Odoo helper that increments
  a lot name and returns the *next* one in a 2-element preview list). Returns `False` if no prior lot
  exists — the caller then falls back to a fresh `ir.sequence`. Unchanged by v16.0.6; still consulted
  only after the released pool is exhausted.
- `sh_get_released_serials(company, prefix, qty)` (`@api.model`) — [ADDED: v16.0.6; CHANGED: fifth
  UAT round] returns up to `qty` lots matching `company_id` + `sh_config_prifix_type` +
  `sh_is_released=True`, ordered by `name ASC` (lowest serial number first, per the client's explicit
  ordering requirement). [CHANGED] Also requires `name =like prefix%` — same fix class as
  `sh_get_next_serial`'s name-anchor validation: a stale/mistagged lot (e.g. a lot literally named
  "BB0166" but tagged `sh_config_prifix_type='AA'` from pre-fix test data) was leaking into the AA
  released pool before this fix, confirmed via direct ORM test
  (`env['stock.lot'].sh_get_released_serials(company, 'AA', 5)` returned `BB0166` last in the list).
  Does not filter by product — matches `sh_get_next_serial`'s existing behavior, confirmed intentional
  with the client (a released serial is reusable by any product sharing that prefix).
See also: [[02_data_flow#Flow 1]], [[02_data_flow#Flow 5]]

## StockMove (stock.move) — inherit
File: `models/stock_move.py`
Status: [ACTIVE]
Purpose: Adds a lot-range bulk-select/prune helper and heavily customizes `_action_assign()` to
preferentially reserve quants tied to a picking's `sh_source_mo_id`/`sh_internal_picking_id`.
Key Fields: `start_lot_id`, `end_lot_id` (Many2one stock.lot) — range bounds for
`sh_action_update_move_line`; `mo_lot_ids` (Many2many stock.lot, compute) — candidate lots sourced from
the picking's `sh_source_mo_id.lot_ids` or `sh_internal_picking_id`'s move lines, used as the domain for
`start_lot_id`/`end_lot_id`
Critical Methods:
- `_compute_mo_lot_ids()` — derives the candidate-lot set from whichever of `sh_source_mo_id` /
  `sh_internal_picking_id` is set on the move's picking.
- `sh_action_update_move_line()` — validates both bounds are set and `start_lot_id.id <=
  end_lot_id.id`, then unlinks every move line whose `lot_id` falls outside that id range.
- `_action_assign(force_qty=False)` — **full reimplementation** of the standard Odoo reservation method
  (not calling `super()`), with two "SHSMART CODE" blocks inserted at the points where standard Odoo
  would call `_update_reserved_quantity` normally. These blocks check
  `picking.picking_type_code == 'outgoing' and picking.picking_type_code == 'internal'` (see
  [[09_known_issues]] for why this condition can never be true) and, when a `sh_source_mo_id` or
  `sh_internal_picking_id` is set, search for quants matching that MO's/transfer's lots at the move's
  location before falling through to the standard reservation call.
See also: [[02_data_flow#Flow 2]], [[02_data_flow#Flow 3]], [[09_known_issues]]

## StockMoveLine (stock.move.line) — inherit
File: `models/stock_move_line.py`
Status: [ACTIVE] (field present but not currently driving any active logic)
Purpose: Placeholder selection-checkbox field for a move-line bulk-action UI that was designed but is
currently fully commented out (both the onchange handler here and the tree-view field placement in
`views/stock_move_views.xml`).
Key Fields: `sh_select_record` (Boolean)
See also: [[09_known_issues]]

## StockPickingType (stock.picking.type) — inherit
File: `models/stock_picking.py`
Status: [ACTIVE]
Purpose: Minor action-context tweak for picking-type list actions.
Critical Methods: `_get_action()` — calls standard `_for_xml_id`, forces `default_immediate_transfer:
False` and adds `default_company_id`/`search_default_picking_type_id` into the action context; respects
the `stock.no_default_immediate_tranfer` system parameter.

## StockPicking (stock.picking) — inherit
File: `models/stock_picking.py`
Status: [ACTIVE]
Purpose: Source-MO/source-transfer lot-reservation hinting, MO/internal-transfer smart buttons, and
live quantity-suffix naming for internal transfers.
Key Fields:
- `mo_count`, `internal_transfer_count` (Integer, compute) — smart-button counters
- `sh_source_mo_id` (Many2one sh.finished.product) — user-selected "these are the lots I want to pull
  from" hint, domain-limited via `sh_source_mo_ids` to MOs whose finished lots are actually in stock at
  this picking's source location (`_compute_sh_source_mo_ids`)
- `sh_source_mo_ids` (Many2many sh.finished.product, compute) — the domain source for the field above
- `sh_internal_picking_id` (Many2one stock.picking, domain restricted to `picking_type_id.code =
  'internal'`) — alternative hint, mutually exclusive with `sh_source_mo_id` via onchange
- `sh_internal_picking_ids` (Many2many stock.picking, compute) — domain source for the field above
Critical Methods:
- `_compute_sh_source_mo_ids()` — for each move on the picking, finds `done`, `sh_main_mo=True` MOs at
  this location producing this product, whose finished-product lots still have available stock quants
  at this picking's source location; offers those as selectable "source MO" options.
- `_compute_sh_internal_picking_ids()` — similar, but sources from other `done` internal-type pickings
  of the same product/location rather than MOs.
- `_onchange_sh_source_mo_id()` / `_onchange_sh_internal_picking_id()` — enforce mutual exclusivity.
- `action_mo_records()` / `action_internal_transfer_records()` — smart-button handlers opening the
  standard MO/picking list actions filtered to the relevant ids.
- `action_assign()` — see [[02_data_flow#Flow 2]]. Full override that calls `super()` then, for
  outgoing/internal pickings with a source hint set, unreserves and manually re-reserves against the
  hinted lots' quants with two near-identical code blocks (one for `sh_source_mo_id`, one for
  `sh_internal_picking_id`) — see [[09_known_issues]] for duplication concern.
- `button_validate()` — after `super()`, for internal transfers recomputes and rewrites the `(qty)` name
  suffix from `move_ids.quantity_done`.
- `sh_update_internal_transfer_name()` (`@api.model`, cron target) — see [[02_data_flow#Flow 4]].
See also: [[02_data_flow#Flow 2]], [[02_data_flow#Flow 4]], [[09_known_issues]]
