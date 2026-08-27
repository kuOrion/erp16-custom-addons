# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, _, fields, api
from odoo.exceptions import UserError, ValidationError
import re

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sh_serial_no_type = fields.Selection(
        string='Serial No Type',
        selection=[('type1', 'Type 1'), ('type2', 'Type 2')],
        default='type1',
    )
    sh_finished_product_ids = fields.One2many('sh.finished.product', 'production_id', string='Finished Product')
    sh_produce_qty = fields.Float('Produce Quantity')
    sh_auto_assign_serial_no = fields.Boolean(related='product_id.sh_auto_assign_serial_no', string='Auto Assign Serial Number')
    sh_main_mo = fields.Boolean(
        compute='_compute_sh_main_mo',store=True )
    # Separate from sh_main_mo on purpose: sh_main_mo must always stay on the
    # lowest-id sibling (stock_picking.py's traceability lookup depends on
    # that meaning to find the Done MO). This field instead tracks whichever
    # sibling still needs a serial assigned - a backorder split created by a
    # partial Assign Serial No (Produce Quantity < total) has a higher id and
    # would otherwise never show the Assign Serial No button.
    sh_serial_btn_mo = fields.Boolean(
        compute='_compute_sh_serial_btn_mo', store=True)
    # count_assign_serial_button_click = fields.Integer(string='Count Assign Serial Button Click', default=0)
    sh_total_qty = fields.Integer(string='Total Quantity')
    # sh_count_finished_product = fields.Integer(string='Count Finished Product', compute='_compute_sh_count_finished_product')
    sh_is_serial_btn_invisible = fields.Boolean(string='Hide Serial No Button', compute='_compute_serial_btn_visibility')
    sh_serial_history_ids = fields.Many2many(
        'sh.serial.reassign.log', compute='_compute_sh_serial_history_ids',
        string='Serial No History')

    def _compute_sh_serial_history_ids(self):
        for record in self:
            record.sh_serial_history_ids = self.env['sh.serial.reassign.log'].search([
                '|', ('from_production_id', '=', record.id),
                ('to_production_id', '=', record.id),
            ])

    # def _compute_sh_count_finished_product(self):
    #     for record in self:
    #         if record.sh_finished_product_ids:
    #             record.sh_count_finished_product = record.sh_finished_product_ids[0].sh_product_qty
    #         else:
    #             record.sh_count_finished_product = 0  

    # @api.constrains('sh_produce_qty', 'product_id')
    # def _check_produce_qty(self):
    #     for rec in self:
    #         if rec.product_id.sh_auto_assign_serial_no and rec.sh_produce_qty <= 0:
    #             raise ValidationError(_("Produce Quantity must be greater than 0."))
            
    @api.depends('sh_total_qty', 'sh_finished_product_ids')
    def _compute_serial_btn_visibility(self):
        for record in self:
            if record.sh_finished_product_ids and record.sh_total_qty == record.sh_finished_product_ids[0].sh_product_qty:
                record.sh_is_serial_btn_invisible = True
            else:
                record.sh_is_serial_btn_invisible = False

    @api.depends('sh_serial_no_type')
    def _compute_sh_main_mo(self):
        for record in self:
            record.sh_main_mo = True
            if self.procurement_group_id and self.procurement_group_id.mrp_production_ids:
                sorted_production = sorted(self.procurement_group_id.mrp_production_ids, key=lambda x: x.id)
                for production in sorted_production:
                    production.sh_main_mo = False
                sorted_production[0].sh_main_mo = True

    @api.depends('sh_serial_no_type', 'state', 'lot_producing_id')
    def _compute_sh_serial_btn_mo(self):
        for record in self:
            record.sh_serial_btn_mo = True
            if record.procurement_group_id and record.procurement_group_id.mrp_production_ids:
                sorted_production = sorted(record.procurement_group_id.mrp_production_ids, key=lambda x: x.id)
                for production in sorted_production:
                    production.sh_serial_btn_mo = False
                # Lowest-id sibling that still has no serial assigned and is
                # not done/cancelled - the one Assign Serial No should target
                # next, including a backorder split created by a partial
                # assignment (Produce Quantity < total on the original MO).
                pending = [p for p in sorted_production
                           if not p.lot_producing_id and p.state not in ('done', 'cancel')]
                main = pending[0] if pending else sorted_production[0]
                main.sh_serial_btn_mo = True



    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        if self.product_qty > 0:
            self.sh_total_qty = self.product_qty
        else:
            self.sh_total_qty = 0


    @api.onchange('sh_serial_no_type')
    def _onchange_sh_serial_no_type(self):
        company = self.company_id
        if self.sh_serial_no_type == 'type1':
           
            message = company.sh_confirirmation_message_type1
            if message:
                return {
                    'warning': {
                        'title': _("Type 1 Confirmation"),
                        'message': message,
                    }
                }
        elif self.sh_serial_no_type == 'type2':
            message = company.sh_confirirmation_message_type2
            if message:
                return {
                    'warning': {
                        'title': _("Type 2 Confirmation"),
                        'message': message,
                    }
                }
    
    def write(self, vals):
        """A prefix has been added to the lot to identify the previous lot number by type."""
        # Server-side guard: on a Done MO the Lot/Serial Number must not be
        # changed/cleared from the form (even after UNLOCK). Release Serial No
        # first resets Done -> Draft, then clears the lot, so it still works.
        if 'lot_producing_id' in vals and not self.env.context.get('sh_allow_lot_producing_write'):
            for rec in self:
                if rec.state == 'done':
                    new_lot_id = vals.get('lot_producing_id') or False
                    old_lot_id = rec.lot_producing_id.id if rec.lot_producing_id else False
                    if new_lot_id != old_lot_id:
                        raise UserError(_(
                            "You cannot change or remove the Lot/Serial Number on a "
                            "Done Manufacturing Order. Use the Release Serial No "
                            "button instead so stock and Finished Product stay consistent."
                        ))
        res = super(MrpProduction, self).write(vals)
        if vals.get('lot_producing_id'):
            new_lot = self.env['stock.lot'].browse(vals['lot_producing_id'])
            if new_lot and new_lot.sh_is_released:
                # Whichever path assigned this serial (our own buttons or the
                # standard Lot/Serial Number field), it is no longer sitting
                # unused - clear the flag so it cannot be offered to another
                # MO later, and log the event for history.
                new_lot.sh_is_released = False
                already_logged = self.env['sh.serial.reassign.log'].sudo().search([
                    ('lot_id', '=', new_lot.id), ('to_production_id', 'in', self.ids),
                ], limit=1)
                if not already_logged:
                    for rec in self:
                        rec._sh_log_serial_event(new_lot, False, rec, 'reuse')
            for rec in self:
                if rec.sh_serial_no_type == 'type1' and self.company_id.sh_prefix_type1:
                    rec.lot_producing_id.write({
                       'sh_config_prifix_type':self.company_id.sh_prefix_type1
                    })
                elif rec.sh_serial_no_type == 'type2' and self.company_id.sh_prefix_type2:
                    rec.lot_producing_id.write({
                       'sh_config_prifix_type': self.company_id.sh_prefix_type2
                   })
                  
                else:
                   return res
        return res
    

    def _sh_unreseve_qty(self):
        """Reverse quant reservation/quantity for this MO's move lines.
        Reference: custom/addons/sh_mrp_cancel (Cancel-to-Draft flow only)."""
        for move in self.sudo().mapped(
            'move_raw_ids') | self.sudo().mapped('move_byproduct_ids') \
                | self.sudo().mapped('move_dest_ids') | self.sudo().mapped('move_finished_ids'):
            for move_line in move.sudo().move_line_ids:
                quant = self.env['stock.quant'].sudo().search([
                    ('location_id', '=', move_line.location_id.id),
                    ('product_id', '=', move_line.product_id.id),
                    ('lot_id', '=', move_line.lot_id.id),
                ], limit=1)
                if quant:
                    quant.write({'quantity': quant.quantity + move_line.qty_done})
                quant = self.env['stock.quant'].sudo().search([
                    ('location_id', '=', move_line.location_dest_id.id),
                    ('product_id', '=', move_line.product_id.id),
                    ('lot_id', '=', move_line.lot_id.id),
                ], limit=1)
                if quant:
                    quant.write({'quantity': quant.quantity - move_line.qty_done})

    def _sh_reset_done_mo_to_draft(self):
        """Reverse a DONE MO back to draft so its serial can be released and
        reused: undo moves/move lines/pickings/workorders, unreserve quants.
        Reference: custom/addons/sh_mrp_cancel process_action_mrp_cancel_draft()
        (Cancel-to-Draft flow only — no other logic from that module is used)."""
        self.ensure_one()
        if self.sudo().move_raw_ids:
            self.sudo().move_raw_ids.write({'state': 'draft'})
            self.sudo().move_raw_ids.mapped('move_line_ids').write({'state': 'draft', 'qty_done': 0})
            self._sh_unreseve_qty()
        if self.sudo().workorder_ids:
            self.sudo().workorder_ids.write({'state': 'ready', 'qty_produced': 0})
        if self.sudo().move_byproduct_ids:
            self.sudo().move_byproduct_ids.write({'state': 'draft'})
            self.sudo().move_byproduct_ids.mapped('move_line_ids').write({'state': 'draft', 'qty_done': 0})
        if self.sudo().move_dest_ids:
            self.sudo().move_dest_ids.write({'state': 'draft'})
            self.sudo().move_dest_ids.mapped('move_line_ids').write({'state': 'draft', 'qty_done': 0})
        if self.sudo().move_finished_ids:
            self.sudo().move_finished_ids.write({'state': 'draft'})
            self.sudo().move_finished_ids.mapped('move_line_ids').write({'state': 'draft', 'qty_done': 0})
        if self.sudo().finished_move_line_ids:
            self.sudo().finished_move_line_ids.write({'state': 'draft'})
        if self.sudo().picking_ids:
            self.sudo().picking_ids.mapped('move_ids_without_package').write({'state': 'draft'})
            self.sudo().picking_ids.mapped('move_ids_without_package').mapped(
                'move_line_ids').write({'state': 'draft', 'qty_done': 0})
            self.sudo().picking_ids.write({'state': 'draft'})
        self.sudo().write({'qty_producing': 0, 'state': 'draft'})

    def _sh_detach_lot_from_finished_product(self, lot):
        """Remove `lot` from every Finished Product that still holds it and
        keep the displayed quantity in sync with the remaining serial list.

        Finished Product rows are stored on the MAIN MO of a split group, but
        Release is clicked on the individual sibling MO that owns the serial.
        Searching only by the sibling's production_id therefore misses the
        real Finished Product row and leaves the serial listed under the old
        product — which is what the client saw after reassignment.
        """
        self.ensure_one()
        finished_products = self.env['sh.finished.product'].search([
            ('lot_ids', 'in', lot.id),
        ])
        if lot.sh_finished_product_id:
            finished_products |= lot.sh_finished_product_id
        for finished in finished_products:
            remaining_lots = finished.lot_ids.filtered(lambda l: l.id != lot.id)
            finished.write({
                'lot_ids': [(6, 0, remaining_lots.ids)],
                'sh_product_qty': len(remaining_lots),
            })
        if lot.sh_finished_product_id:
            lot.sh_finished_product_id = False

    def _sh_clear_lot_stock(self, lot):
        """Fully clear stock.quant rows for a released serial.

        After cancel-to-draft, residual quants can remain under the OLD
        product (e.g. at the production location). If those rows are left
        behind, Inventory still shows the serial against the original product
        even after the lot is reassigned to a different product/MO.
        """
        self.ensure_one()
        quants = self.env['stock.quant'].sudo().search([('lot_id', '=', lot.id)])
        for quant in quants:
            if quant.quantity:
                self.env['stock.quant'].sudo()._update_available_quantity(
                    quant.product_id,
                    quant.location_id,
                    -quant.quantity,
                    lot_id=quant.lot_id,
                    package_id=quant.package_id,
                    owner_id=quant.owner_id,
                )
            if quant.reserved_quantity:
                quant.sudo().write({'reserved_quantity': 0.0})
        leftover = self.env['stock.quant'].sudo().search([('lot_id', '=', lot.id)])
        if leftover:
            leftover.sudo().unlink()

    def action_release_serial_number(self):
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_(
                "Only the System Administrator can release a Serial Number."))
        if not self.lot_producing_id:
            raise UserError(_(
                "This Manufacturing Order has no Serial Number assigned."))
        lot = self.lot_producing_id
        if self.state == 'done':
            self._sh_reset_done_mo_to_draft()
        # A released lot must be free of THIS MO's OWN stock.move.line
        # references so it can later be reassigned to a different product
        # (core Odoo blocks a product change on a lot referenced by ANY move
        # line whose product_id differs from the target - resetting state to
        # draft alone leaves the lines in place and does not clear this).
        # Scoped to this MO's own moves only - a lot can also be referenced
        # by move lines on unrelated, already-Done pickings (e.g. a Sale
        # Delivery or Internal Transfer that already shipped/moved this
        # serial elsewhere), and unlinking THOSE is both wrong (destroys real
        # delivery/transfer history) and blocked by core Odoo itself with a
        # hard UserError ("You can not delete product moves if the picking is
        # done"), which used to abort the whole release.
        own_move_ids = (self.move_raw_ids | self.move_finished_ids | self.move_byproduct_ids).ids
        self.env['stock.move.line'].sudo().search([
            ('lot_id', '=', lot.id), ('move_id', 'in', own_move_ids),
        ]).unlink()
        # Also drop this lot from OPEN pickings (draft/assigned/…). Done pick
        # history must stay for audit; those done lines are why cross-product
        # reuse cannot always repoint the same lot record (handled on reassign).
        self._sh_clear_lot_from_open_move_lines(lot)
        # Drop every residual quant for this serial so Inventory no longer
        # lists it under the original product after release/reassign.
        self._sh_clear_lot_stock(lot)
        # Detach from ANY Finished Product (main MO row, not only this sibling).
        self._sh_detach_lot_from_finished_product(lot)
        self.lot_producing_id = False
        lot.sh_is_released = True
        self._sh_log_serial_event(lot, self, False, 'release')
        # Refresh Finished Product on the last transfer's main MO (existing FP
        # owner) so qty/serial list stay in sync after release.
        self._sh_rebuild_group_finished_product()

    def action_reassign_serial_number(self):
        """Directly assign a serial: lowest released one for this MO's type
        first, otherwise a brand-new number at the next free slot."""
        self.ensure_one()
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_(
                "Only the System Administrator can reassign a Serial Number."))
        if self.lot_producing_id:
            raise UserError(_(
                "This Manufacturing Order already has Serial Number %s. "
                "Release it first.") % self.lot_producing_id.name)
        company = self.company_id
        if self.sh_serial_no_type == 'type1':
            prefix, padding = company.sh_prefix_type1, company.sh_number_of_degit_type1
        elif self.sh_serial_no_type == 'type2':
            prefix, padding = company.sh_prefix_type2, company.sh_number_of_degit_type2
        else:
            raise UserError(_(
                "Please select a Serial No Type on the Manufacturing Order first."))
        if not prefix:
            raise UserError(_("Please first add a Prefix for the selected Serial No Type."))
        released = self.env['stock.lot'].sh_get_released_serials(company, prefix, 1)
        if released:
            self._sh_take_released_lot(released[0])
        else:
            number = self._sh_next_free_serial_number(prefix, padding)
            new_lot = self.env['stock.lot'].create({
                'name': '%s%s' % (prefix, str(number).zfill(padding)),
                'product_id': self.product_id.id,
                'company_id': company.id,
                'sh_config_prifix_type': prefix,
            })
            self.lot_producing_id = new_lot.id
            self._sh_log_serial_event(new_lot, False, self, 'reuse')

    def action_mass_release_serial_number(self):
        """List-view mass action: release whichever selected MOs actually
        have a serial assigned; silently skip the rest instead of erroring
        the whole batch out over one record with nothing to release."""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_(
                "Only the System Administrator can release a Serial Number."))
        for production in self.filtered('lot_producing_id'):
            production.action_release_serial_number()

    def action_mass_reassign_serial_number(self):
        """List-view mass action: reassign whichever selected MOs currently
        have no serial; silently skip the rest (already-assigned MOs)."""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_(
                "Only the System Administrator can reassign a Serial Number."))
        for production in self.filtered(lambda mo: not mo.lot_producing_id):
            production.action_reassign_serial_number()

    def _sh_log_serial_event(self, lot, from_production, to_production, action):
        # sudo(): this log is read-only for everyone via ACL (no manual
        # create/write/unlink allowed), so the module itself must bypass
        # that restriction to record its own release/reuse events.
        self.env['sh.serial.reassign.log'].sudo().create({
            'lot_id': lot.id,
            'from_production_id': from_production.id if from_production else False,
            'to_production_id': to_production.id if to_production else False,
            'action': action,
        })

    def _sh_clear_lot_from_open_move_lines(self, lot):
        """Remove lot from non-done move lines (open picks/packs) so release
        does not leave the serial reserved on a draft/assigned picking.

        Uses SQL for the lot_id clear so ORM reservation checks on messy
        quant data cannot block release/reassign (common after partial
        release of already-picked serials).
        """
        self.env.cr.execute(
            """
            UPDATE stock_move_line
               SET lot_id = NULL
             WHERE lot_id = %s
               AND state NOT IN ('done', 'cancel')
            """,
            (lot.id,),
        )
        self.env['stock.move.line'].invalidate_model(['lot_id'])

    def _sh_repoint_or_clone_lot_for_product(self, lot, product):
        """Prepare a released lot for `product`.

        Same product: reuse the same stock.lot row.
        Different product: try to repoint product_id (works when only MO moves
        existed and were unlinked on release). If core Odoo blocks the change
        because done pick/pack move lines still reference the old product
        (client case: serial already left WH/Stock), create a lot row for the
        NEW product with the SAME serial name, archive the old row (qty 0) so
        WH/Stock only shows the new product — never both with stock.
        """
        self.ensure_one()
        self._sh_detach_lot_from_finished_product(lot)
        self._sh_clear_lot_from_open_move_lines(lot)
        self._sh_clear_lot_stock(lot)

        if lot.product_id == product:
            lot.sh_is_released = False
            return lot

        # Prefer same lot row when Odoo allows product change.
        try:
            lot.with_context(sh_allow_lot_producing_write=True).write({
                'product_id': product.id,
                'sh_is_released': False,
            })
            return lot
        except UserError:
            pass

        # Done stock moves still reference this lot under the old product —
        # cannot repoint. New lot same serial name for the new product.
        existing_for_product = self.env['stock.lot'].search([
            ('name', '=', lot.name),
            ('product_id', '=', product.id),
            ('company_id', '=', lot.company_id.id),
        ], limit=1)
        if existing_for_product:
            new_lot = existing_for_product
            new_lot.sh_is_released = False
            self._sh_clear_lot_stock(new_lot)
        else:
            new_lot = self.env['stock.lot'].create({
                'name': lot.name,
                'product_id': product.id,
                'company_id': lot.company_id.id,
                'sh_config_prifix_type': lot.sh_config_prifix_type,
                'sh_is_released': False,
            })

        # Carry full Release/Reuse history onto the NEW lot so the serial
        # form the user opens from the new MO still shows Released From +
        # later Auto-Reused (history was only on the old product lot).
        self._sh_copy_serial_reassign_history(lot, new_lot)

        # Retire old product's lot row: not released anymore, stock already
        # cleared. Keep the row for stock move-line history under the old
        # product (core Odoo forbids deleting/repointing it).
        if lot.sh_is_released:
            lot.sh_is_released = False
        return new_lot

    def _sh_copy_serial_reassign_history(self, from_lot, to_lot):
        """Copy sh.serial.reassign.log rows from one lot to another (same
        serial name after cross-product clone) without duplicating identical
        events already present on the target."""
        if not from_lot or not to_lot or from_lot == to_lot:
            return
        Log = self.env['sh.serial.reassign.log'].sudo()
        existing = {
            (log.action, log.from_production_id.id, log.to_production_id.id, log.create_date)
            for log in Log.search([('lot_id', '=', to_lot.id)])
        }
        for log in Log.search([('lot_id', '=', from_lot.id)], order='id asc'):
            key = (log.action, log.from_production_id.id, log.to_production_id.id, log.create_date)
            if key in existing:
                continue
            # create() then force create_date/user so the timeline matches
            # the original release/reuse events.
            new_log = Log.create({
                'lot_id': to_lot.id,
                'from_production_id': log.from_production_id.id or False,
                'to_production_id': log.to_production_id.id or False,
                'action': log.action,
            })
            self.env.cr.execute(
                """
                UPDATE sh_serial_reassign_log
                   SET create_date = %s,
                       create_uid = %s,
                       write_date = %s,
                       write_uid = %s
                 WHERE id = %s
                """,
                (
                    log.create_date,
                    log.create_uid.id or self.env.uid,
                    log.write_date or log.create_date,
                    log.write_uid.id or self.env.uid,
                    new_log.id,
                ),
            )
            existing.add(key)

    def _sh_take_released_lot(self, lot):
        """Consume a released lot for this MO (same or different product)."""
        self.ensure_one()
        assigned_lot = self._sh_repoint_or_clone_lot_for_product(lot, self.product_id)
        self.lot_producing_id = assigned_lot.id
        self._sh_log_serial_event(assigned_lot, False, self, 'reuse')
        return assigned_lot

    def _sh_next_free_serial_number(self, prefix, padding):
        """Compute the next free numeric suffix for `prefix` by scanning actual
        stock.lot names (not the sh_config_prifix_type tag, which may be stale
        or wrong), so a fresh ir.sequence never collides with existing lots."""
        existing_lots = self.env['stock.lot'].search([
            ('company_id', '=', self.company_id.id),
            ('name', '=like', '%s%%' % prefix),
        ])
        max_number = 0
        for lot in existing_lots:
            suffix = (lot.name or '')[len(prefix):]
            if suffix.isdigit():
                max_number = max(max_number, int(suffix))
        return max_number + 1

    def _sh_rebuild_group_finished_product(self, target_mo=None):
        """Rebuild ONE Finished Product row for the whole split-MO family.

        target_mo = main order of the *latest Assign Serial transfer*
        (the MO where Assign Serial No was clicked — e.g. first main, then
        later the backorder main). All done serials of the family are listed
        there. Not the absolute last child MO of the group, and not always
        the original first main.

        On Release (target_mo not passed): keep the existing Finished Product
        owner in the group and only refresh qty/serial list.
        """
        self.ensure_one()
        if not self.procurement_group_id:
            return
        group_mos = self.procurement_group_id.mrp_production_ids
        if not group_mos:
            return

        if target_mo is None:
            # Release path: stay on whatever MO already holds Finished Product
            # (that is the last transfer's main order).
            existing_fps = self.env['sh.finished.product'].search([
                ('production_id', 'in', group_mos.ids),
            ], order='id desc', limit=1)
            target_mo = existing_fps.production_id if existing_fps else self
        else:
            target_mo = target_mo

        done_productions = group_mos.filtered(
            lambda production: production.state == 'done' and production.lot_producing_id
        )
        lots = done_productions.mapped('lot_producing_id').filtered(
            lambda lot: lot.product_id == target_mo.product_id and not lot.sh_is_released
        )
        finished_qty = len(lots)

        # One Finished Product only — remove rows on every other MO in the group.
        orphan_fps = self.env['sh.finished.product'].search([
            ('production_id', 'in', group_mos.ids),
            ('production_id', '!=', target_mo.id),
        ])
        if orphan_fps:
            orphan_fps.unlink()

        existing_record = self.env['sh.finished.product'].search(
            [('production_id', '=', target_mo.id)], limit=1)
        if existing_record:
            if finished_qty:
                existing_record.write({
                    'name': target_mo.name,
                    'product_id': target_mo.product_id.id,
                    'sh_product_qty': finished_qty,
                    'lot_ids': [(6, 0, lots.ids)],
                })
            else:
                existing_record.write({
                    'sh_product_qty': 0,
                    'lot_ids': [(5, 0, 0)],
                })
        elif finished_qty:
            self.env['sh.finished.product'].create({
                'name': target_mo.name,
                'product_id': target_mo.product_id.id,
                'sh_product_qty': finished_qty,
                'production_id': target_mo.id,
                'lot_ids': [(6, 0, lots.ids)],
                'company_id': target_mo.company_id.id,
            })

    def action_assign_serial_number(self):
        company = self.company_id
        assign_serial = self.env['stock.assign.serial']
        # if self.count_assign_serial_button_click >= 0:
        #     self.count_assign_serial_button_click = 1
        if self.product_id.sh_auto_assign_serial_no and self.sh_produce_qty <= 0:
            raise ValidationError(_("Produce Quantity must be greater than 0."))

        if self.sh_serial_no_type == 'type1':
            if not company.sh_prefix_type1:
                raise ValidationError('Please First Add Prefix for Type 1')
            
            number_of_degit = company.sh_number_of_degit_type1
            prefix = company.sh_prefix_type1
            serial_type = 'type1'

            exist_lot = self.env['stock.lot'].search([
                ('sh_config_prifix_type', '=', prefix),
                ('company_id', '=', self.company_id.id),
            ], order='id DESC', limit=1)
            exist_serial = False
            if exist_lot:
                exist_serial = self.env['stock.lot'].sh_get_next_serial(company, self.product_id,prefix,serial_type)
            # New unused prefix must start at 1 (do not keep the old Type 1
            # sequence counter after the prefix string is changed).
            number_next = self._sh_next_free_serial_number(prefix, number_of_degit)
            if number_next == 1:
                exist_serial = False
            
            # self.env.cr.execute("""
            #     SELECT id FROM stock_lot
            #     WHERE sh_config_prifix_type = %s AND company_id = %s
            #     ORDER BY id DESC LIMIT 1
            # """, (prefix, company.id))
            # lot_res = self.env.cr.fetchone()
            # if lot_res:
            #     # Get the record using browse, then call the existing helper function.
            #     exist_lot = self.env['stock.lot'].browse(lot_res[0])
            #     exist_serial = exist_lot.sh_get_next_serial(company, self.product_id, prefix, serial_type)
            # else:
            #     exist_serial = False

            if not exist_serial:
                sequence = self.env['ir.sequence'].sudo().search([
                    ('code', '=', 'mrp_serial_assign.serial.type1'),
                    ('company_id', 'in', [company.id, False]),
                ], limit=1)
                if sequence:
                    # The sequence row is looked up by a fixed code, so if the
                    # company's prefix/digit settings changed since it was
                    # first created, its stored prefix/padding must be synced
                    # too - otherwise next_by_id() keeps stamping the old
                    # prefix even though the number itself is correct.
                    # Write number_next (not number_next_actual) so the
                    # PostgreSQL sequence used by next_by_id() is reset.
                    sequence.write({
                        'prefix': prefix,
                        'padding': number_of_degit,
                        'number_next': number_next,
                    })
                else:
                    sequence = self.env['ir.sequence'].sudo().create({
                        'name': 'MRP Serial Sequence',
                        'code': 'mrp_serial_assign.serial.type1',
                        'prefix': prefix,
                        'padding': number_of_degit,
                        'number_next': number_next,
                        'number_increment': 1,
                        'company_id': company.id,
                    })
                # self.env.cr.execute("""
                # INSERT INTO ir_sequence (name, code, prefix, padding, number_next, number_increment)
                # VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                # """, ('MRP Serial Sequence', 'mrp_serial_assign.serial.type1', prefix, number_of_degit, 1, 1))
                # seq_id = self.env.cr.fetchone()[0]
                # sequence = self.env['ir.sequence'].browse(seq_id)
                serial = sequence.next_by_id()
            
                next_serial_number = serial
            else:
                next_serial_number = exist_serial
                
        elif self.sh_serial_no_type == 'type2':
            if not company.sh_prefix_type2:
                raise ValidationError('Please First Add Prefix for Type 2')
            
            number_of_degit = company.sh_number_of_degit_type2
            prefix = company.sh_prefix_type2
            serial_type = 'type2'
            exist_lot = self.env['stock.lot'].search([
                ('sh_config_prifix_type', '=', prefix),
                ('company_id', '=', self.company_id.id),
            ], order='id DESC', limit=1)
            exist_serial = False
            if exist_lot:
                exist_serial = self.env['stock.lot'].sh_get_next_serial(company, self.product_id,prefix,serial_type)
            # New unused prefix must start at 1 (do not keep the old Type 2
            # sequence counter after the prefix string is changed).
            number_next = self._sh_next_free_serial_number(prefix, number_of_degit)
            if number_next == 1:
                exist_serial = False
            # self.env.cr.execute("""
            # SELECT id FROM stock_lot
            # WHERE sh_config_prifix_type = %s AND company_id = %s
            # ORDER BY id DESC LIMIT 1
            # """, (prefix, company.id))
            # lot_res = self.env.cr.fetchone()
            # if lot_res:
            #     exist_lot = self.env['stock.lot'].browse(lot_res[0])
            #     exist_serial = exist_lot.sh_get_next_serial(company, self.product_id, prefix, serial_type)
            # else:
            #     exist_serial = False
            if not exist_serial:
                sequence = self.env['ir.sequence'].sudo().search([
                    ('code', '=', 'mrp_serial_assign.serial.type2'),
                    ('company_id', 'in', [company.id, False]),
                ], limit=1)
                if sequence:
                    sequence.write({
                        'prefix': prefix,
                        'padding': number_of_degit,
                        'number_next': number_next,
                    })
                else:
                    sequence = self.env['ir.sequence'].sudo().create({
                        'name': 'MRP Serial Sequence',
                        'code': 'mrp_serial_assign.serial.type2',
                        'prefix': prefix,
                        'padding': number_of_degit,
                        'number_next': number_next,
                        'number_increment': 1,
                        'company_id': company.id,
                    })
                # self.env.cr.execute("""
                # INSERT INTO ir_sequence (name, code, prefix, padding, number_next, number_increment)
                # VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                # """, ('MRP Serial Sequence', 'mrp_serial_assign.serial.type2', prefix, number_of_degit, 1, 1))
                # seq_id = self.env.cr.fetchone()[0]
                # sequence = self.env['ir.sequence'].browse(seq_id)
                serial = sequence.next_by_id()
            
                next_serial_number = serial
            else:
                next_serial_number = exist_serial
        else:
            return False
        # apply_serial = assign_serial.create({
        # 'production_id': self.id,
        # 'next_serial_count': self.product_qty,
        # 'produced_qty': self.product_qty,
        # 'expected_qty': self.product_qty,
        # 'next_serial_number': next_serial_number,
        # })

        # Sibling MOs split off earlier may not carry the same
        # sh_serial_no_type as the main MO; force it so write()'s
        # prefix-tagging stamps the lot with the correct type instead of
        # mislabeling it (which corrupts sh_get_next_serial lookups for
        # both types going forward).
        if self.procurement_group_id:
            pending_productions = self.procurement_group_id.mrp_production_ids.filtered(
                lambda production: production.state not in ('done', 'cancel')
            )
            mismatched_type = pending_productions.filtered(
                lambda production: production.sh_serial_no_type != self.sh_serial_no_type)
            if mismatched_type:
                mismatched_type.write({'sh_serial_no_type': self.sh_serial_no_type})

        # Use released serial numbers first (lowest first): feed their names
        # into the wizard's list, and only generate brand-new numbers for the
        # remaining quantity. The overridden stock.assign.serial reuses the
        # released lot records instead of creating duplicates.
        released_lots = self.env['stock.lot'].sh_get_released_serials(
            company, prefix, self.sh_produce_qty)
        released_names = released_lots.mapped('name')
        remaining_qty = self.sh_produce_qty - len(released_names)

        record_id = self.id
        if self.procurement_group_id.mrp_production_ids:
            to_confirmed_productions = self.procurement_group_id.mrp_production_ids.filtered(
                lambda production: production.state == 'confirmed'
            )

            # record_id = to_confirmed_productions[0].id
            if to_confirmed_productions:
                record_id = to_confirmed_productions[0].id
            else:
                record_id = self.id

        self.env.cr.execute("""
        INSERT INTO stock_assign_serial (production_id, next_serial_count, produced_qty, expected_qty, next_serial_number, serial_numbers)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (record_id, max(remaining_qty, 0), len(released_names), self.sh_produce_qty,
              next_serial_number, "\n".join(released_names) or None))
        assign_serial_id = self.env.cr.fetchone()[0]
        apply_serial = self.env['stock.assign.serial'].browse(assign_serial_id)
        if remaining_qty > 0:
            apply_serial.generate_serial_numbers_production()
        apply_serial.apply()
        if self.sh_produce_qty > 0 and self.procurement_group_id:
            done_production = 1
            mrp_production_ids = self.procurement_group_id.mrp_production_ids.filtered(
                lambda production: production.state != 'done'
            )
            for production in mrp_production_ids:
                if done_production <= self.sh_produce_qty:
                    production.button_mark_done()
                    done_production += 1
        # else:
        #     if self.sh_produce_qty > 0 and self.procurement_group_id:
        #         to_close_productions = self.procurement_group_id.mrp_production_ids.filtered(
        #             lambda production: production.state == 'to_close'
        #         )
        #         done_production = 1
        #         for production in to_close_productions:
        #             if done_production <= self.sh_produce_qty:
        #                 production.button_mark_done()
        #                 done_production += 1

        # Move/rebuild Finished Product onto THIS MO (the main order of the
        # current Assign Serial transfer — first main, or later backorder main).
        # All done serials of the family are listed there.
        self._sh_rebuild_group_finished_product(target_mo=self)

        qty = len(self.procurement_group_id.mrp_production_ids) if self.procurement_group_id else ''
        base = re.sub(r"\s*\([^)]*\)\s*$", "", self.name or "")
        self.name = f"{base} ({qty})"


  
    @api.model
    def _auto_update_mo_sequence(self):
        main_mos = self.search([
            ('sh_main_mo', '=', True),
            ('company_id', '=', self.env.company.id),
        ])
        for mo in main_mos:
            if not mo.name:
                # skip blank‐named MOs
                continue
            qty = len(mo.procurement_group_id.mrp_production_ids) if mo.procurement_group_id else 0
            base = re.sub(r"\s*\([^)]*\)\s*$", "", mo.name)
            new_name = f"{base} ({qty})"
            if new_name != mo.name:
                mo.name = new_name

      