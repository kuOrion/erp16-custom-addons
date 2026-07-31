from odoo import models, _
from odoo.exceptions import UserError


class StockLot(models.Model):
    _inherit = "stock.lot"

    # def action_transfer_to_fg(self):
    #     self.ensure_one()
    #
    #     stock_location = self.env['stock.location'].search([
    #         ('complete_name', '=', 'WH/Stock')
    #     ], limit=1)
    #
    #     fg_location = self.env['stock.location'].search([
    #         ('complete_name', '=', 'WH/FG')
    #     ], limit=1)
    #
    #     if not stock_location:
    #         raise UserError(_("WH/Stock location not found."))
    #
    #     if not fg_location:
    #         raise UserError(_("WH/FG location not found."))
    #
    #     quant = self.env['stock.quant'].search([
    #         ('lot_id', '=', self.id),
    #         ('location_id', '=', stock_location.id),
    #         ('quantity', '>', 0),
    #     ], limit=1)
    #
    #     if not quant:
    #         raise UserError(
    #             _("This serial number is not available in WH/Stock.")
    #         )
    #
    #     picking_type = self.env['stock.picking.type'].search([
    #         ('code', '=', 'internal'),
    #         ('warehouse_id', '!=', False),
    #     ], limit=1)
    #
    #     if not picking_type:
    #         raise UserError(_("No Internal Transfer operation type found."))
    #
    #     # Create Picking
    #     picking = self.env['stock.picking'].create({
    #         'picking_type_id': picking_type.id,
    #         'location_id': stock_location.id,
    #         'location_dest_id': fg_location.id,
    #         'origin': self.name,
    #     })
    #
    #     # Create Move
    #     move = self.env['stock.move'].create({
    #         'name': self.product_id.display_name,
    #         'product_id': self.product_id.id,
    #         'product_uom_qty': 1,
    #         'product_uom': self.product_id.uom_id.id,
    #         'picking_id': picking.id,
    #         'location_id': stock_location.id,
    #         'location_dest_id': fg_location.id,
    #     })
    #
    #     # Confirm move
    #     move._action_confirm()
    #
    #     # Create only ONE move line
    #     self.env['stock.move.line'].create({
    #         'move_id': move.id,
    #         'picking_id': picking.id,
    #         'product_id': self.product_id.id,
    #         'product_uom_id': self.product_id.uom_id.id,
    #         'qty_done': 1,
    #         'lot_id': self.id,
    #         'location_id': stock_location.id,
    #         'location_dest_id': fg_location.id,
    #     })
    #
    #     # Validate transfer
    #     picking.button_validate()
    #
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': _('Success'),
    #             'message': _(
    #                 'Serial Number %s transferred from WH/Stock to WH/FG.'
    #             ) % self.name,
    #             'type': 'success',
    #             'sticky': False,
    #         }
    #     }

    def action_transfer_to_fg(self):

        stock_location = self.env['stock.location'].search([
            ('complete_name', '=', 'WH/Stock')
        ], limit=1)

        fg_location = self.env['stock.location'].search([
            ('complete_name', '=', 'WH/FG')
        ], limit=1)

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal'),
            ('warehouse_id', '!=', False),
        ], limit=1)

        for lot in self:

            quant = self.env['stock.quant'].search([
                ('lot_id', '=', lot.id),
                ('location_id', '=', stock_location.id),
                ('quantity', '>', 0),
            ], limit=1)

            if not quant:
                continue

            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': stock_location.id,
                'location_dest_id': fg_location.id,
                'origin': lot.name,
            })

            move = self.env['stock.move'].create({
                'name': lot.product_id.display_name,
                'product_id': lot.product_id.id,
                'product_uom_qty': 1,
                'product_uom': lot.product_id.uom_id.id,
                'picking_id': picking.id,
                'location_id': stock_location.id,
                'location_dest_id': fg_location.id,
            })

            move._action_confirm()

            self.env['stock.move.line'].create({
                'move_id': move.id,
                'picking_id': picking.id,
                'product_id': lot.product_id.id,
                'product_uom_id': lot.product_id.uom_id.id,
                'qty_done': 1,
                'lot_id': lot.id,
                'location_id': stock_location.id,
                'location_dest_id': fg_location.id,
            })

            picking.button_validate()

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('Selected serial numbers transferred successfully.'),
                'type': 'success',
                'sticky': False,
            }
        }