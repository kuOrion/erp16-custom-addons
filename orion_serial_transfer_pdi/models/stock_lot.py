# from odoo import models, api
# from odoo.exceptions import UserError
#
#
# class StockLot(models.Model):
#     _inherit = 'stock.lot'
#
#     def action_transfer_to_pdi(self):
#
#         pdi_location = self.env['stock.location'].search([
#             ('name', '=', 'PDI')
#         ], limit=1)
#
#         if not pdi_location:
#             raise UserError("PDI location not found")
#
#         picking_type = self.env['stock.picking.type'].search([
#             ('code', '=', 'internal')
#         ], limit=1)
#
#         for lot in self:
#
#             quant = self.env['stock.quant'].search([
#                 ('lot_id', '=', lot.id),
#                 ('quantity', '>', 0)
#             ], limit=1)
#
#             if not quant:
#                 raise UserError(f"No stock found for Serial {lot.name}")
#
#             source_location = quant.location_id
#             product = lot.product_id
#
#             picking = self.env['stock.picking'].create({
#                 'picking_type_id': picking_type.id,
#                 'location_id': source_location.id,
#                 'location_dest_id': pdi_location.id,
#                 'origin': 'Serial Transfer to PDI',
#             })
#
#             move = self.env['stock.move'].create({
#                 'name': product.name,
#                 'product_id': product.id,
#                 'product_uom_qty': 1,
#                 'product_uom': product.uom_id.id,
#                 'picking_id': picking.id,
#                 'location_id': source_location.id,
#                 'location_dest_id': pdi_location.id,
#             })
#
#             self.env['stock.move.line'].create({
#                 'move_id': move.id,
#                 'product_id': product.id,
#                 'product_uom_id': product.uom_id.id,
#                 'qty_done': 1,
#                 'lot_id': lot.id,
#                 'location_id': source_location.id,
#                 'location_dest_id': pdi_location.id,
#                 'picking_id': picking.id,
#             })
#
#             picking.action_confirm()
#             picking.button_validate()


from odoo import models, api
from odoo.exceptions import UserError

class StockLot(models.Model):
    _inherit = 'stock.lot'

    def action_transfer_to_pdi(self):
        pdi_location = self.env['stock.location'].search([
            ('name', '=', 'PDI')
        ], limit=1)
        if not pdi_location:
            raise UserError("PDI location not found")

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal')
        ], limit=1)
        if not picking_type:
            raise UserError("No internal picking type found")

        # Inventory adjustment location (virtual) for force-adding stock
        inventory_location = self.env['stock.location'].search([
            ('usage', '=', 'inventory')
        ], limit=1)
        if not inventory_location:
            raise UserError("Inventory adjustment location not found")

        for lot in self:
            product = lot.product_id

            # Search for existing quant in internal location
            quant = self.env['stock.quant'].search([
                ('lot_id', '=', lot.id),
                ('quantity', '>', 0),
                ('location_id.usage', '=', 'internal'),
            ], limit=1)

            # If no quant found, force-create stock via inventory adjustment
            if not quant:
                # Use a default internal source location (e.g. WH/Stock)
                source_location = self.env['stock.location'].search([
                    ('usage', '=', 'internal'),
                    ('name', '=', 'Stock'),
                ], limit=1)
                if not source_location:
                    source_location = self.env['stock.location'].search([
                        ('usage', '=', 'internal'),
                    ], limit=1)

                # Force create quant (inventory adjustment)
                self.env['stock.quant'].sudo().create({
                    'product_id': product.id,
                    'location_id': source_location.id,
                    'lot_id': lot.id,
                    'quantity': 1,
                    'inventory_quantity': 1,
                })

                # Apply the inventory adjustment
                new_quant = self.env['stock.quant'].search([
                    ('lot_id', '=', lot.id),
                    ('location_id', '=', source_location.id),
                ], limit=1)
                new_quant.action_apply_inventory()

                quant = new_quant

            source_location = quant.location_id

            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type.id,
                'location_id': source_location.id,
                'location_dest_id': pdi_location.id,
                'origin': f'Force Transfer to PDI - {lot.name}',
            })

            move = self.env['stock.move'].create({
                'name': product.name,
                'product_id': product.id,
                'product_uom_qty': 1,
                'product_uom': product.uom_id.id,
                'picking_id': picking.id,
                'location_id': source_location.id,
                'location_dest_id': pdi_location.id,
            })

            self.env['stock.move.line'].create({
                'move_id': move.id,
                'product_id': product.id,
                'product_uom_id': product.uom_id.id,
                'qty_done': 1,
                'lot_id': lot.id,
                'location_id': source_location.id,
                'location_dest_id': pdi_location.id,
                'picking_id': picking.id,
            })

            picking.action_confirm()
            picking.button_validate()