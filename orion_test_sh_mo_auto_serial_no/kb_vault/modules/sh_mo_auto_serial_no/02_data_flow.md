# Data Flow
Status: [ACTIVE]
Back to [[00_overview]]

## Flow 1 — Assigning a serial number and closing out split MOs
User opens the "main" MO (lowest id in its `procurement_group_id`, `sh_main_mo=True`, computed by
`_compute_sh_main_mo` [[03_models#MrpProduction]]), sets `sh_serial_no_type` (Type 1/Type 2 — triggers
an optional company-configured confirmation warning via `_onchange_sh_serial_no_type`), sets
`sh_produce_qty` (how many split MOs to close in this pass), clicks **Assign Serial No** →
`action_assign_serial_number()` [[03_models#MrpProduction]]:
1. Validates `sh_produce_qty > 0` if the product requires auto-assign.
2. Resolves the company's prefix/digit config for the chosen type, and normalizes
   `sh_serial_no_type` on all pending sibling MOs in the group so `write()`'s prefix-tagging never
   stamps a lot with the wrong type.
3. Computes the "next serial" anchor for new generation: `stock.lot.sh_get_next_serial()`
   [[03_models#StockLot]] anchors on the lot with the **highest numeric suffix by NAME** for the
   prefix (not the newest row by id — reused serials come back as new rows with old names); if no
   prefix-named lot exists at all, an `ir.sequence` is found by code (or created once) and its
   `number_next` is set from `_sh_next_free_serial_number()` so numbering always continues past
   every existing lot instead of restarting at 1.
4. [ADDED: v16.0.6] Fetches released serial NAMES (lowest first, up to `sh_produce_qty`) via
   `sh_get_released_serials()` — see [[02_data_flow#Flow 5]] Step B.
5. Determines the target MO record to attach the assignment to: prefers a sibling MO in
   `state == 'confirmed'` within the same `procurement_group_id`, else falls back to `self`.
6. Inserts a `stock.assign.serial` row directly via `self.env.cr.execute(INSERT ...)` (bypassing normal
   `create()` defaults — see [[09_known_issues]]) with `serial_numbers` pre-filled with the released
   names and `next_serial_count` set to only the remaining quantity; calls
   `generate_serial_numbers_production()` (skipped when the released pool covers everything) to append
   new names, then `apply()` — where the module's `stock.assign.serial` override
   [[03_models#StockAssignSerialNumbers]] splits the production and reuses released lots per name.
7. Marks done as many remaining sibling MOs as `sh_produce_qty` allows via `button_mark_done()`.
8. Collects `lot_producing_id` from every now-`done` sibling MO (reused and freshly-generated
   portions alike) into a list, then creates or updates the `sh.finished.product` record
   for `self` (`production_id = self.id`): increments `sh_product_qty` by `sh_produce_qty`, appends
   the collected lot ids to `lot_ids` via `(4, lot_id)` commands. See [[03_models#ShFinishedProduct]].
9. Recomputes the MO's own display name suffix: strips any existing `"(N)"` trailing pattern via
   regex and re-appends `"({count of sibling MOs in the group})"`.

## Flow 2 — Reserving stock against a specific MO's or transfer's lots
User opens a delivery or internal transfer, sets `sh_source_mo_id` (a `sh.finished.product` record —
selectable only from MOs the system found produced matching, in-stock serials at this location, via
`_compute_sh_source_mo_ids` [[03_models#StockPicking]]) or `sh_internal_picking_id`
(mutually exclusive with the above via onchange), clicks **Reserve** →
`stock.picking.action_assign()` [[03_models#StockPicking]] calls `super().action_assign()` first (does
the standard reservation), then — only for `outgoing`/`internal` picking types and only if
`sh_source_mo_id` or `sh_internal_picking_id` is set — calls `do_unreserve()` and re-does reservation
from scratch: for each move, iterates the referenced MO's/transfer's lots, searches `stock.quant` for
that exact lot at the picking's source location, and creates `stock.move.line` rows + calls
`stock.quant._update_reserved_quantity()` directly, splitting demand across quants if one lot's
available quantity doesn't cover it. Move state is then manually recomputed
(`assigned`/`partially_available`/`confirmed`) based on how much of `product_uom_qty` got covered.
A parallel, more defensive version of similar "prefer this MO's lots" logic also lives in
`stock.move._action_assign()` [[03_models#StockMove]] (the "SHSMART CODE" blocks), used during the
standard batch-reservation pass rather than the picking-level Reserve button.

## Flow 3 — Range-selecting lots on the stock move Detailed Operations popup
User opens a stock move's "Detailed Operations" popup (serial-tracked product), sets `start_lot_id`/
`end_lot_id` (both domain-restricted to `mo_lot_ids`, a compute pulling lots from the picking's
`sh_source_mo_id.lot_ids` or `sh_internal_picking_id.move_ids.move_line_ids.lot_id`, see
`_compute_mo_lot_ids` [[03_models#StockMove]]), clicks **Update** →
`sh_action_update_move_line()` [[03_models#StockMove]] deletes every move line whose `lot_id` falls
outside the `[start_lot_id.id, end_lot_id.id]` range (raises `UserError` if either bound is missing or
inverted).

## Flow 4 — Nightly name-suffix reconciliation
Cron `ir_cron_auto_update_main_mo_sequence` (daily, 02:00) calls
`mrp.production._auto_update_mo_sequence()` [[03_models#MrpProduction]]: for every `sh_main_mo=True`
MO in the current company, recomputes `"(sibling count)"` suffix and rewrites `name` if it drifted.
Cron `ir_cron_sh_update_internal_transfer_name` (daily, 02:00) calls
`stock.picking.sh_update_internal_transfer_name()` [[03_models#StockPicking]]: for every internal-type
picking, recomputes `"(total done qty)"` suffix from `move_ids.quantity_done` and rewrites `name` if it
drifted. Both crons exist because the live write-time hooks (`button_mark_done` name-suffix code in MO,
`button_validate` override in picking) can miss some paths where quantities change without going
through those exact methods.
See also: [[07_csv_data]]

## Flow 5 — [ADDED: v16.0.6] Release a wrongly-assigned serial + pool-aware reuse
Per TICKET/24830: a serial number was mistakenly allocated to the wrong manufactured model (ticket
example: serial meant for `MGH10CA00` allocated to `EZ7` instead). An admin (`base.group_system`)
needs to free that serial and have it automatically flow back into use, without losing the serial
number itself, and without deleting or resetting the MO it came from.

**Step A — Release:** Admin opens the wrongly-assigned MO and clicks **Release Serial No** (visible
only when `lot_producing_id` is set, admin-only via view `groups`; hidden together with "Assign
Serial No" — exactly one of Assign/Release/Reassign is visible at a time, driven by whether
`lot_producing_id` is set) → `action_release_serial_number()` [[03_models#MrpProduction]]:
re-validates admin group; raises if no serial is assigned; if `state == 'done'`, first calls
`_sh_reset_done_mo_to_draft()` (below) to reverse the MO back to `draft`; strips the lot out of the
MO's linked `sh.finished.product.lot_ids`; clears `mrp.production.lot_producing_id`; sets
`stock.lot.sh_is_released = True`; logs a `release` event to `sh.serial.reassign.log`
(`from_production_id = this MO`, `to_production_id = False`).

**Release on a `done` MO — `_sh_reset_done_mo_to_draft()`** [[03_models#MrpProduction]]: core Odoo
forbids releasing/reassigning a lot once real `stock.move.line` rows reference it
(`odoo/addons/stock/models/stock_lot.py:158-165`), and a `done` MO's lot always has such rows. To make
Release work on a `done` MO, this method reverses it to `draft` first: `move_raw_ids`,
`move_byproduct_ids`, `move_dest_ids`, `move_finished_ids` and their move lines → `state='draft'`,
`qty_done=0`; quants unreserved via `_sh_unreseve_qty()` (adds `move_line.qty_done` back at the
source location, subtracts it at the destination — restoring pre-consumption quantities);
`workorder_ids` → `state='ready'`, `qty_produced=0`; `finished_move_line_ids` → `draft`; `picking_ids`
and their moves/move lines → `draft`; `qty_producing` → `0`; finally `state` → `'draft'`. Since
`mrp.production.state` is itself a **computed** field (`_compute_state`, keyed off exactly these
move/workorder/quantity fields), every one of these resets is needed for the compute to land cleanly
on `draft` rather than `to_close`/`progress`/`done` — confirmed via a direct ORM test against a real
`done` MO (state transitioned `done` → `draft`, `qty_producing` → `0`, all moves → `draft`/`0.0`, lot
correctly marked released). Reference for this reversal pattern:
`custom/addons/sh_mrp_cancel`'s Cancel-to-Draft flow (`process_action_mrp_cancel_draft`) — only that
flow was used as a reference; no other logic from that module was adopted (no accounting/valuation
handling, no delete/cancel-permanently paths).
After the reset, the MO is an ordinary `draft`/`confirmed` MO: it goes through the standard Odoo
Confirm → Assign Components → Mark as Done cycle again once a new serial is assigned (Step B/C below),
same as any other MO — no special-casing exists downstream of the reset.

**Step B — Automatic reuse on the next Assign Serial No (name-level, via the wizard):** The next time
**any** MO with a matching company + prefix runs `action_assign_serial_number()`
[[03_models#MrpProduction]], released serial NAMES (lowest first, via
`stock.lot.sh_get_released_serials()` [[03_models#StockLot]]) are pre-filled into the
`stock.assign.serial` wizard's `serial_numbers` text list at creation, and only the remaining
quantity gets freshly generated names appended (via `generate_serial_numbers_production()`). The
module's `stock.assign.serial` override [[03_models#StockAssignSerialNumbers]] then reuses the
released lot records (or reuses just the name via a new lot on product mismatch) during
`_assign_serial_numbers()`, logging a `reuse` event per reused name.
IMPORTANT design constraint that forced this shape: sibling one-unit MOs do NOT exist when the button
is clicked — core `_split_productions()` creates them inside the wizard's `apply()`. An earlier
implementation drained the pool onto pre-existing sibling MO records before the wizard ran; it
silently did (almost) nothing because there was only one pre-split MO at that point. Do not
reintroduce pre-split record-level draining.
Example matching the client's own scenario: serials 1-25 already consumed elsewhere, 26-50 released,
live sequence at 200 — a new 50-unit run consumes 26-50 first (25 units), then continues 201-225 for
the remaining 25.

**Cross-product reuse rule** [current design, v16.0.6 fourth UAT round]: a RELEASED lot has no stock
moves against it, so core Odoo allows repointing its `product_id` directly (guard in
`stock.lot.write()`, `odoo/addons/stock/models/stock_lot.py:158-165`, only blocks the change once
`stock.move.line` rows reference the lot). Reuse across products therefore repoints the SAME
`stock.lot` record — `lot.product_id = new_product.id` — rather than creating a new row per product;
there is exactly one lot record per serial name, ever. `_sh_take_released_lot()`
[[03_models#MrpProduction]] implements this for the one-click Reassign button; the automatic batch
path applies the identical rule inside the `stock.assign.serial` override's
`_assign_serial_numbers()` [[03_models#StockAssignSerialNumbers]]. Full audit trail (who assigned
what, when, to which MO, released when) lives entirely in `sh.serial.reassign.log`, not in duplicate
lot records — see [[09_known_issues]] for the superseded first-iteration design.

**Step C — Manual reassignment (one-click, no wizard):** Per the ticket's "provision to reassign a
serial number" + "option to assign the next available serial number", an admin-only **Reassign Serial
No** button (visible only when the MO has no serial yet) calls
`mrp.production.action_reassign_serial_number()` directly — no popup/selection. It takes the lowest
released serial for the MO's type prefix if any exists (via `_sh_take_released_lot()`, so the
cross-product rule applies), else creates a brand-new lot at the next free number via
`_sh_next_free_serial_number()`. A selection wizard (`sh.serial.reassign.wizard`) was briefly built
during the second UAT round and then removed at the client's request ("no need any selection, direct
assign") — do not resurrect it without asking.
See also: [[03_models#MrpProduction]], [[03_models#StockLot]], [[03_models#ShSerialReassignLog]],
[[09_known_issues]]
