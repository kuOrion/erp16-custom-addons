# Views (XML)
Status: [ACTIVE]
Back to [[00_overview]]

## mrp_production_views.xml
- `sh_mo_auto_serial_no_mrp_production_form_view_inherited` (inherits `mrp.mrp_production_form_view`) —
  after `user_id`: adds `sh_auto_assign_serial_no` (invisible, drives required-ness elsewhere),
  `sh_serial_no_type` (required if auto-assign), `sh_produce_qty` (required if auto-assign),
  `sh_main_mo`/`sh_total_qty`/`sh_is_serial_btn_invisible` (all invisible technical fields); after the
  `action_cancel` button: adds the "Assign Serial No" button (`action_assign_serial_number`, visible
  when `sh_main_mo=True`, `state != 'draft'`, `sh_is_serial_btn_invisible=False`, **and**
  [CHANGED: v16.0.6, fifth UAT round] `lot_producing_id` is NOT set — added this 4th condition so
  Assign and Release never show together on the same MO), [ADDED: v16.0.6] the "Release Serial No"
  button (`action_release_serial_number`, visible only when `lot_producing_id` is set,
  `groups="base.group_system"`), and [ADDED: v16.0.6, second UAT round] the "Reassign Serial No"
  button (`action_reassign_serial_number`, visible only when `lot_producing_id` is NOT set,
  `groups="base.group_system"`, and [CHANGED: v16.0.6, sixth UAT round] also hidden on `state ==
'draft'` — matches Assign Serial No's own draft-hiding rule; found showing on a raw Draft MO with no
serial, which let it be clicked before the MO was even confirmed — mutually exclusive with Release by
construction); inside the
  notebook: adds a "Finished Product" page showing `sh_finished_product_ids` as a non-editable tree
  (product, quantity, a "show details" row button), and [ADDED: v16.0.6] a "Serial No History" page
  (`groups="base.group_system"`) showing `sh_serial_history_ids` as a non-editable tree (lot, action,
  from/to MO, user, date).
- `sh_mo_auto_serial_no_mrp_view_mrp_production_filter_inherited` (inherits
  `mrp.view_mrp_production_filter`) — adds a "Main MO" filter (`sh_main_mo = True`) after the
  `activities_exception` filter.
- Overrides the standard `mrp.mrp_production_action` window action to default-filter to
  `search_default_sh_main_mo: True` in its context — so the main MO list view only ever shows main MOs
  by default.
- `sh_mo_auto_serial_no_action_mass_release_serial` / `sh_mo_auto_serial_no_action_mass_reassign_serial`
  [ADDED: v16.0.6, third UAT round] — `ir.actions.server` records bound to `mrp.production`'s list
  view (`binding_view_types="list"`), admin-only (`groups_id` = `base.group_system`), calling
  `action_mass_release_serial_number()` / `action_mass_reassign_serial_number()` on the selected
  recordset. Appear in the MO list view's **Action** menu when one or more rows are checked.
Related model: [[03_models#MrpProduction]]

## product_views.xml
- `sh_mo_auto_serial_no_view_template_property_form_inherited` (inherits
  `stock.view_template_property_form`) — after the `tracking` field in the `traceability` group, adds
  `sh_auto_assign_serial_no`, visible only when `tracking == 'serial'`.
Related model: [[03_models#ProductTemplate]]

## res_config_setting_views.xml
- `sh_mo_auto_serial_no_res_config_settings_view_form_inherited` (inherits
  `mrp.res_config_settings_view_form`) — inside the MRP settings tab (`div[@data-key='mrp']`), adds a
  "MO Assign Serial No." section with two side-by-side boxes: "Type 1: Apply Serial Number Globally"
  and "Type 2: ..." — each showing digit count, prefix, and confirmation message fields.
Related model: [[03_models#ResConfigSettings]]

## sh_finished_product_views.xml
- `view_sh_finished_product_tree` — simple list: name, product, quantity, a "show details" row button.
- `view_sh_finished_product_form` — read-only product/quantity/production fields, plus a "Serial Number"
  notebook page listing `lot_ids` (non-editable tree: name, product_qty).
- `action_sh_finished_product` — standalone window action (tree/form) for `sh.finished.product`, though
  no menu item ships in this module's data — likely accessed only via the "show details" row buttons
  and the MO form's Finished Product tab (`sh_show_details_action`).
Related model: [[03_models#ShFinishedProduct]]

## stock_move_views.xml
- `sh_mo_auto_serial_no_view_stock_move_operations_inherited` (inherits
  `stock.view_stock_move_operations`) — before `next_serial`: adds `start_lot_id`/`end_lot_id` (domain
  restricted to `mo_lot_ids`), invisible `mo_lot_ids` tag field, and the "Update" button
  (`sh_action_update_move_line`). A large commented-out block shows an earlier, more elaborate design
  (source-MO/source-transfer fields, a "select all" checkbox with per-line onchange) that predates the
  current simpler lot-range approach — kept for historical reference, not active.
- `sh_mo_auto_serial_no_view_view_stock_move_line_operation_tree_inherited` (inherits
  `stock.view_stock_move_line_operation_tree`) — forces `force_save="1"` on `reserved_uom_qty` (ensures
  the field's value is always sent on save even if not touched/dirtied — needed because this module's
  reservation logic sets it programmatically outside normal onchange flows). A commented-out xpath shows
  where `sh_select_record` (see [[03_models#StockMoveLine]]) was meant to be placed but isn't currently
  wired in.
Related model: [[03_models#StockMove]], [[03_models#StockMoveLine]]

## stock_picking_views.xml
- `sh_mo_auto_serial_no_stock_picking_form_view_inherited` (inherits `stock.view_picking_form`) —
  before the `action_see_move_scrap` button: adds two stat buttons, "MO" (`action_mo_records`, visible
  only if `mo_count != 0`) and "Internal Transfer" (`action_internal_transfer_records`, visible only if
  `internal_transfer_count != 0`); after `location_id`: adds `sh_source_mo_id`
  (domain-restricted to `sh_source_mo_ids`, readonly once `state='done'`), invisible `sh_source_mo_ids`
  tag field, `sh_internal_picking_id` (similarly domain-restricted/readonly), invisible
  `sh_internal_picking_ids` tag field.
- Overrides the standard `stock.action_picking_tree_ready` ("To Do") window action to add
  `'operation_type_view': True` into its context (consumed by `stock.picking.type._get_action()` and
  possibly other views checking this context flag, though no direct consumer of that specific key is
  visible elsewhere in this module's Python — likely intended for a view-level `attrs`/`groups`
  condition or a future feature).
Related model: [[03_models#StockPicking]]

## stock_lot_views.xml — [ADDED: v16.0.6]
- `sh_mo_auto_serial_no_view_production_lot_form_inherited` (inherits `stock.view_production_lot_form`)
  — adds a "Release History" page inside the existing notebook, `groups="base.group_system"`, showing
  `sh_reassign_log_ids` as a non-editable tree (action, from MO, to MO, user, date). Deliberately
  placed as a direct `notebook position="inside"` addition (not depending on the parent notebook's own
  `display_complete`-based `attrs`, since page-level visibility doesn't inherit the wrapping element's
  `attrs`) so the tab appears regardless of that unrelated condition.
- `sh_mo_auto_serial_no_search_product_lot_filter_inherited` [ADDED: v16.0.6, third UAT round]
  (inherits `stock.search_product_lot_filter`) — adds `sh_config_prifix_type` as a searchable field,
  two plain filters ("Released for Reuse" / "Not Released", visible to all users — the released
  state itself isn't sensitive, only the release/reassign actions are admin-only) next to the
  existing `product_id` field, and two Group By options ("Released for Reuse", "Serial No Prefix")
  alongside the existing "Product" group-by. Lets any user quickly isolate the release pool from
  Inventory ▸ Lots/Serial Numbers without typing a manual filter.
Related model: [[03_models#StockLot]], [[03_models#ShSerialReassignLog]]
