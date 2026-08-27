# Known Issues
Status: [ACTIVE]
Back to [[00_overview]]

## Issue: standard "+ create new lot" widget bypasses Type1/Type2 prefix logic entirely
Status: [OPEN] (by design, confirmed with client)
Discovered: 2026-07-17 (UAT — typing/using the standard Lot/Serial Number "+" widget on a Type 1 MO
produced a BB-prefixed (Type 2) serial name, e.g. BB0167, instead of an AA-prefixed one)
Description: the standard Odoo Lot/Serial Number field's own "create new" widget (the `+` button next
to the field, and manual typing followed by "Create") calls **core** `stock.lot._get_next_serial()`
(`odoo/addons/stock/models/stock_lot.py:75-83`) — a completely different, un-overridden method from
this module's own `sh_get_next_serial()`. Core's version anchors purely on `product_id` (the most
recent lot ever created for that product, by id), with zero awareness of `sh_config_prifix_type` /
Type1 vs Type2 — so if a product's most recent lot happened to be created under Type 2 (prefix "BB"),
the standard widget will keep suggesting/accepting BB-prefixed names even when the MO's own
`sh_serial_no_type` is Type 1. This is the exact "wrong prefix continuation" flaw already fixed in
`sh_get_next_serial()` [[03_models#StockLot]] — but living in a **separate, un-touched core method**
that this module does not override.
Resolution: confirmed with client — **not fixing**. The standard widget/manual-entry path is left as
native Odoo behavior; users must use this module's **Assign Serial No** / **Reassign Serial No**
buttons (never the standard `+` widget or manual typing) to get correct, prefix-aware serial
generation. Document this operationally — it is not a bug in this module's own logic, it is a gap in
coverage of a core widget deliberately left unaddressed.

## Issue: unreachable condition in `_action_assign()`'s SHSMART CODE blocks
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `models/stock_move.py` gates both "SHSMART CODE" blocks in `_action_assign()` on
`move.picking_id.picking_type_code == 'outgoing' and move.picking_id.picking_type_code == 'internal'`
— a single field compared to two different literal values with `and`, which is never simultaneously
true. As written, this condition is always `False`, meaning the entire preferential-lot-reservation
block inside `_action_assign()` never executes; only the `else` branch (standard
`_update_reserved_quantity` call) ever runs. This is very likely meant to be `or`. The equivalent logic
in `stock.picking.action_assign()` uses `or` correctly (`picking.picking_type_code == 'outgoing' or
picking.picking_type_code == 'internal'`), suggesting this is a copy-paste slip rather than intentional.
Failure scenario: a user sets `sh_source_mo_id` on an outgoing/internal picking expecting reservation to
prefer that MO's lots when moves get reserved via the standard "Reserve" mechanism that flows through
`_action_assign` directly (e.g. background reservation, `procurement`-triggered reservation) rather than
through `stock.picking.action_assign()` — reservation silently falls back to default FIFO/lot-agnostic
behavior instead of honoring the hint.
Workaround: none currently — `stock.picking.action_assign()`'s own reservation re-do (which does work
correctly) masks this for the common "click Reserve on the picking form" path, so the bug is not
visible in that flow. Flag to the user before touching this method if the reported bug is
"lot preference is ignored" for a non-explicit-Reserve-click case.

## Issue: raw SQL wizard creation is fragile
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `mrp.production.action_assign_serial_number()` inserts directly into `stock_assign_serial`
via `self.env.cr.execute("INSERT INTO stock_assign_serial (...) VALUES (...) RETURNING id")` instead of
`self.env['stock.assign.serial'].create({...})`. This bypasses ORM defaults, `create()` overrides (if
any get added to that model later by this module or another), and column additions in future Odoo core
versions that aren't reflected in this hardcoded column list. Commented-out ORM-based code
(`assign_serial.create({...})`) sits directly above, suggesting this was a deliberate but undocumented
substitution — possibly a performance workaround, but the reason isn't recorded anywhere in the file.
As of v16.0.6, the INSERT also carries a `serial_numbers` column pre-filled with released serial
names — see [[changelog/v16.0.6]] — so the hardcoded column list has grown, increasing this fragility.
Workaround: none currently; flag to the user if a future Odoo upgrade adds a required/renamed column on
`stock.assign.serial` and this insert starts failing.

## Issue: `sh.finished.product` model has unused fields and open CRUD access
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `sh_serial_no` (Char) and `lot_id` (single Many2one) on `sh.finished.product` are declared
but never written to by any code path in this module — `lot_ids` (plural One2many) is the only field
actually populated. Additionally, `ir.model.access.csv` grants full CRUD on this model to
`base.group_user` (any internal user), with no record rules restricting by company despite
`company_id` being present on the model.
Workaround: none needed today; note for a future cleanup pass, and flag if company-level data isolation
on this model becomes a concern.

## Issue: `StockLocation` model class is misnamed `StockMove`
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `models/stock_location.py` declares `class StockMove(models.Model): _inherit =
'stock.location'` — the Python class name doesn't match what it inherits (there's a real, differently-
named `StockMove` class in `models/stock_move.py` too). This doesn't cause a functional bug (Odoo
dispatches by `_inherit`/`_name`, not Python class name) but is confusing during debugging/stack-trace
reading and future maintenance, and violates the company coding standard's expectation of clear naming.
Workaround: none needed functionally; recommend renaming to `StockLocation` in a future cleanup pass.

## Issue: near-duplicate reservation logic across `action_assign()` and `_action_assign()`
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `stock.picking.action_assign()` and `stock.move._action_assign()` both implement very
similar "search quants matching this MO's/transfer's lots at this location, split demand across
matches" logic independently, each with two near-identical blocks (`sh_source_mo_id` vs
`sh_internal_picking_id`) — i.e. four largely-copy-pasted reservation blocks total across the two
methods. Divergence between the copies (e.g. the `and`/`or` bug above existing in one copy but not
the other) is a direct symptom of this duplication. A shared helper method would reduce future drift.
Workaround: none needed today given the current `action_assign()`-flow-only bug surface; flag as a
refactor candidate given the company's stated code-review methodology around reuse/simplification.

## Issue: unused `sh_select_record` field and dead-code block on `stock.move.line`
Status: [OPEN]
Discovered: 2026-07-14 (KB creation review)
Description: `stock.move.line.sh_select_record` exists as a live field with commented-out onchange logic
in `models/stock_move_line.py`, and the corresponding view placement in `stock_move_views.xml` is also
fully commented out. The field currently has no effect on any behavior. Likely leftover from an earlier
design iteration (large commented blocks in `stock_move.py` and `stock_picking.py` reference a
"select all move line" / manual lot-assignment UI that was apparently superseded by the simpler
`start_lot_id`/`end_lot_id` range-select flow in [[02_data_flow#Flow 3]]).
Workaround: none needed; safe to remove in a future cleanup if confirmed unused, but do not remove
without confirming with the user first since dead code sometimes indicates in-progress/parked work.

## Issue: cross-product reuse — resolved history (two iterations)
Status: [RESOLVED] (v16.0.6, fourth UAT round, 2026-07-17)
Discovered: 2026-07-16 (UAT — a Table Top lot got set as lot_producing_id on a Table MO)
Iteration 1 (superseded): the released-serial pool is intentionally shared across products per
prefix (confirmed with client), but the first implementation reassigned the released `stock.lot`
RECORD directly to the consuming MO even when products differed — invalid at that time since a
`stock.lot`'s `product_id` was being changed on a record that could already carry stock-move history.
Iteration 1 fix: created a fresh `stock.lot` with the same name for the new product instead, retiring
the original. This worked but left duplicate rows (same name, N products, N lot records) once a
serial had been reused across several products — visible in UAT as "AA176" appearing twice in the
Lots/Serial Numbers list, once per product.
**Current design (client-requested simplification):** a RELEASED lot (by definition unused — no
stock moves against it) is safe to repoint via `lot.product_id = new_product.id` directly, per core
Odoo's own `stock.lot.write()` guard (`odoo/addons/stock/models/stock_lot.py:158-165`), which only
blocks a product change when `stock.move.line` rows already reference that lot. So reuse across
products now repoints the SAME lot record instead of creating a new one — one row per serial name,
ever, following whichever product currently owns it. History is preserved separately and completely
via `sh.serial.reassign.log` (one row per assign/release/reuse event, keyed by `lot_id`), which the
client confirmed is sufficient audit trail — old moves against a lot before a reassignment remain
attached to the same `lot_id`, so traceability reports for a specific STOCK MOVE still show the
product that was actually moved at that time; only the LOT's current `product_id` field reflects its
present owner.
Lives in two places: `_sh_take_released_lot()` (`models/mrp_production.py`, one-click Reassign
button) and the `stock.assign.serial` override's `_assign_serial_numbers()`
(`models/stock_assign_serial.py`, automatic batch path).

## Issue: pre-split pool-draining silently skipped the released pool
Status: [FIXED] (v16.0.6, second UAT round, 2026-07-17)
Discovered: 2026-07-17 (UAT — a 20-qty run generated all-new AA141+ despite released serials existing)
Description: the first reuse implementation assigned released lots onto sibling MO records *before*
the `stock.assign.serial` wizard ran — but sibling one-unit MOs do not exist at button-click time
(core `_split_productions()` creates them inside the wizard's `apply()`), so the draining pass saw at
most one MO and the batch generated all-new serials.
Fix: reuse moved to the serial-NAME level — released names are pre-filled into the wizard's
`serial_numbers` text and the module's `stock.assign.serial` override reuses the released lot records
during `_assign_serial_numbers()`. See [[02_data_flow#Flow 5]] Step B. Do not reintroduce pre-split
record-level draining.

## Issue: serial generation restarted at 1 / anchored on wrong lot
Status: [FIXED] (v16.0.6, second UAT round, 2026-07-16/17)
Discovered: 2026-07-16 (UAT — "Existing Serial Numbers (AA001..AA012)" then "(AA113..AA131)" errors)
Description: two stacked pre-existing generation flaws surfaced during UAT. (a) The `ir.sequence`
fallback branch unconditionally CREATED a brand-new sequence with `number_next=1` on every call where
no next-serial anchor was found, so repeated runs kept trying to recreate AA001+ and collided with
core Odoo's duplicate-lot check. (b) `sh_get_next_serial()` anchored on the newest lot row by id —
but a reused released serial creates a NEW row with an OLD low name, so generation could restart just
past a low number (AA112 → AA113) and collide with existing higher serials.
Fix: (a) the sequence is now searched by `code` + company and reused, with `number_next` set from
`_sh_next_free_serial_number()` (max numeric suffix by NAME + 1, tag-independent); (b)
`sh_get_next_serial()` now anchors on the highest serial number by NAME across all lots whose name
starts with the prefix. Numbering can no longer restart or collide regardless of reuse history.

## Issue: `write()` prefix-tagging trusts each MO's own `sh_serial_no_type`
Status: [MITIGATED] (v16.0.6, second UAT round)
Discovered: 2026-07-16 (UAT — BB-named lots tagged as AA via siblings with stale/blank type)
Description: the pre-existing `write()` override stamps `stock.lot.sh_config_prifix_type` from
whichever individual MO record's `sh_serial_no_type` is set when `lot_producing_id` is written —
sibling/backorder MOs can carry a stale or blank type (copied by `_split_productions`'s `copy_data`
from whichever record was split), mislabeling lots and historically poisoning next-serial lookups.
Mitigation: `action_assign_serial_number()` now force-normalizes `sh_serial_no_type` on all pending
group siblings before the wizard runs, and the generation fixes above made the lookups
name-anchored (tag-independent), so a stray mistag can no longer corrupt numbering. The `write()`
design itself is unchanged — treat any remaining tag mismatch as cosmetic.
