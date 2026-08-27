# Manufacturing Auto Serial Number — Overview
Status: [ACTIVE]
Version: 16.0.6
Last Updated: 2026-07-14

## Purpose
Kaustubha Udyog's manufacturing flow splits a single Manufacturing Order (MO) demand into multiple
backorder/split MOs sharing one `procurement_group_id` (standard Odoo behavior when producing in
batches). Standard Odoo has no concept of company-configurable, auto-incrementing serial number
prefixes tied to a "type", no easy way to bulk mark-done a set of split MOs at once, no way to
recover from a serial number mistakenly assigned to the wrong MO/product, and no simple way to
consume a specific finished-goods lot when picking/delivering downstream. This module adds all of
that, plus keeps MO/internal-transfer display names annotated with a live count so the "family" of
split documents stays identifiable in list views.

## What It Achieves
- Two independently configurable serial number "types" (Type 1 / Type 2) at the company level — each
  has its own prefix, digit padding, and an optional confirmation warning message shown when selected
  on the MO.
- One-click **Assign Serial Number** action on the "main" MO of a split-production group: generates
  (or continues) an `ir.sequence`-backed serial per the selected type, creates a `stock.assign.serial`
  wizard record via raw SQL insert, generates lot numbers, applies them, and cascades
  `button_mark_done()` across sibling split MOs up to the entered "Produce Quantity".
  See [[02_data_flow#Flow 1]].
- [ADDED: v16.0.6] An admin-only **Release Serial No** action on the MO: detaches a wrongly-assigned
  serial from its MO (the `stock.lot` record stays intact — only the association is removed), marking
  that serial reusable. If the MO is already `done`, Release first reverses it back to `draft`
  (moves, move lines, workorders, quantities, pickings) so the serial can be safely reassigned and the
  MO re-run through the standard Confirm → Assign Components → Mark as Done flow. See
  [[02_data_flow#Flow 5]].
- [ADDED: v16.0.6] An admin-only **Reassign Serial No** action on the MO (visible only when it has no
  serial): one click, no selection UI — assigns the lowest released serial for the MO's type if one
  exists, else the next new number. See [[02_data_flow#Flow 5]].
- [ADDED: v16.0.6] **Assign Serial Number now drains the released-serial pool first** (lowest number
  first) before falling back to generating new serials from the live sequence — so a released serial
  gets reused by the very next production run needing that prefix, instead of sitting idle forever.
  See [[02_data_flow#Flow 5]].
- [ADDED: v16.0.6] An admin-only **release/reuse history**, viewable on both the `stock.lot` (Serial
  Number) form and the `mrp.production` (MO) form, via the new `sh.serial.reassign.log` model.
- A **Finished Product** record (`sh.finished.product`) per MO that accumulates produced quantity and
  the list of lots/serials produced, viewable from a new "Finished Product" tab on the MO form.
- On `stock.picking` (deliveries/internal transfers), lets a user pick a **source MO** or a **source
  internal transfer** as a lot-supply reference; `action_assign()` is heavily overridden to greedily
  reserve `stock.quant`s tied to that MO's/transfer's specific lots before falling through to standard
  reservation.
- Auto-appending a live `"(qty)"` suffix to MO and internal-transfer picking names, refreshed by two
  daily cron jobs plus various write-time hooks, so users watching a list view can see progress without
  opening each record.
- A `start_lot_id`/`end_lot_id` range-select convenience on the stock move operations popup that lets a
  user bulk-select a contiguous lot ID range and delete every move line not falling within it.

## Key Concepts
- **Main MO**: within a `procurement_group_id`'s set of split MOs, the one with the lowest `id` is
  flagged `sh_main_mo=True` (computed, stored). Only the main MO shows the "Assign Serial No" and
  (when a serial is assigned) "Release Serial No" buttons.
- **Type 1 / Type 2**: two parallel, independently configured serial-numbering schemes. Selecting one
  on the MO (`sh_serial_no_type`) drives which company prefix/digit-count/confirmation-message and
  which dedicated `ir.sequence` (`mrp_serial_assign.serial.type1` / `type2`) is used.
- **`sh_config_prifix_type`** (on `stock.lot`, note the spelling — not a typo to "fix", it's the actual
  field name in the DB): stores which prefix type generated a given lot, so the *next* serial for that
  type can be derived by looking up the lot with the same prefix and calling `generate_lot_names` for
  the next value in sequence, rather than always trusting `ir.sequence` (source of truth flips to
  "last actual lot" once one exists).
- **[ADDED: v16.0.6] `sh_is_released`** (on `stock.lot`): explicit flag marking a serial as detached
  from its MO and available for reuse. Set `True` by "Release Serial No", set back `False` the moment
  it's consumed by the pool-draining step of "Assign Serial Number".
- **[ADDED: v16.0.6] Release on a `done` MO**: releasing a serial from an MO already in state `done`
  first resets that MO to `draft` (all moves/move lines to `draft` with quantities zeroed, quants
  unreserved, workorders to `ready`, pickings to `draft`) before detaching the serial, since core Odoo
  forbids releasing/reassigning a lot with real stock history against it. Confirmed working via direct
  ORM test against a real `done` MO: state transitioned `done` → `draft` cleanly, and the MO could be
  re-confirmed and re-run through Assign Serial No (pool-first) and back to `to_close`/`done` normally
  afterward. See [[02_data_flow#Flow 5]].
- **Source MO / Source Internal Transfer** (`sh_source_mo_id`, `sh_internal_picking_id` on
  `stock.picking`): mutually exclusive user-selected hints telling `action_assign()` which specific
  lots to prioritize when reserving stock for this picking.
- **Produce Quantity** (`sh_produce_qty`): how many of the split MOs in the group to mark done in this
  single "Assign Serial No" click (not the produced quantity of the current MO alone). As of v16.0.6
  this quantity may be fulfilled partly from released serials and partly from freshly generated ones.

## Module Map
[[01_architecture]] | [[02_data_flow]] | [[03_models]] | [[04_views_xml]] | [[05_owl_components]] | [[06_controllers]] | [[07_csv_data]] | [[08_dependencies]] | [[09_known_issues]]
