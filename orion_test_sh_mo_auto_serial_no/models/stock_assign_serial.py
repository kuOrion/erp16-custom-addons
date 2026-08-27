# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from collections import Counter

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare


class StockAssignSerialNumbers(models.TransientModel):
    _inherit = 'stock.assign.serial'

    @api.onchange('serial_numbers')
    def _onchange_serial_numbers(self):
        """Overridden from mrp: released serial numbers are meant to be reused,
        so they must not trigger the 'Existing Serial Numbers' error."""
        self.show_apply = False
        self.show_backorders = False
        serial_numbers = self._get_serial_numbers()
        duplicate_serial_numbers = [serial_number for serial_number, counter in Counter(serial_numbers).items() if counter > 1]
        if duplicate_serial_numbers:
            self.serial_numbers = ""
            self.produced_qty = 0
            raise UserError(_('Duplicate Serial Numbers (%s)') % ','.join(duplicate_serial_numbers))
        existing_serial_numbers = self.env['stock.lot'].search([
            ('company_id', '=', self.production_id.company_id.id),
            ('product_id', '=', self.production_id.product_id.id),
            ('name', 'in', serial_numbers),
            ('sh_is_released', '=', False),
        ])
        if existing_serial_numbers:
            self.serial_numbers = ""
            self.produced_qty = 0
            raise UserError(_('Existing Serial Numbers (%s)') % ','.join(existing_serial_numbers.mapped('display_name')))
        if len(serial_numbers) > self.expected_qty:
            self.serial_numbers = ""
            self.produced_qty = 0
            raise UserError(_('There are more Serial Numbers than the Quantity to Produce'))
        self.produced_qty = len(serial_numbers)
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        self.show_apply = float_compare(self.produced_qty, self.expected_qty, precision_digits=precision) == 0
        self.show_backorders = self.produced_qty > 0 and self.produced_qty < self.expected_qty

    def _assign_serial_numbers(self, cancel_remaining_quantity=False):
        """Overridden from mrp: when a serial name matches a released lot,
        reuse that SAME lot record instead of creating a duplicate. A
        released lot has no stock moves against it yet, so core Odoo allows
        repointing product_id directly (see stock.lot.write())."""
        serial_numbers = self._get_serial_numbers()
        productions = self.production_id._split_productions(
            {self.production_id: [1] * len(serial_numbers)}, cancel_remaining_quantity, set_consumed_qty=True)
        product = self.production_id.product_id
        company = self.production_id.company_id
        released_by_name = {
            lot.name: lot for lot in self.env['stock.lot'].search([
                ('company_id', '=', company.id),
                ('name', 'in', serial_numbers),
                ('sh_is_released', '=', True),
            ])
        }
        production_lots = []
        reused_names = set()
        for serial_name in serial_numbers:
            released_lot = released_by_name.get(serial_name)
            if released_lot:
                # Same helpers as Reassign: same product reuses the lot row;
                # different product repoints when possible, otherwise clones
                # the serial name onto a new lot for the new product and
                # archives the old row (client dual-product stock case).
                reused_lot = self.production_id._sh_repoint_or_clone_lot_for_product(
                    released_lot, product)
                reused_names.add(serial_name)
                production_lots.append(reused_lot)
            else:
                production_lots.append(self.env['stock.lot'].create({
                    'product_id': product.id,
                    'company_id': company.id,
                    'name': serial_name,
                }))
        for production, production_lot in zip(productions, production_lots):
            production.lot_producing_id = production_lot.id
            production.qty_producing = production.product_qty
            if production_lot.name in reused_names:
                # sudo(): log is read-only for everyone via ACL, module writes its own events.
                self.env['sh.serial.reassign.log'].sudo().create({
                    'lot_id': production_lot.id,
                    'to_production_id': production.id,
                    'action': 'reuse',
                })
            for workorder in production.workorder_ids:
                workorder.qty_produced = workorder.qty_producing

        if productions and len(production_lots) < len(productions):
            productions[-1].move_raw_ids.move_line_ids.write({'qty_done': 0})
            productions[-1].state = "confirmed"
