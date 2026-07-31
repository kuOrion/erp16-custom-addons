# from odoo import models, fields, api
#
# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     po_quantity = fields.Float(string='PO Quantity')
#     received_quantity = fields.Float(string='Received Quantity')
#     accepted_quantity = fields.Float(string='Accepted Quantity')
#     rejected_quantity = fields.Float(string='Rejected Quantity', compute='_compute_rejected_quantity', store=True)
#     rejection = fields.Char(string='Reason for Rejection')
#
#     @api.depends('received_quantity', 'accepted_quantity')
#     def _compute_rejected_quantity(self):
#         for move in self:
#             if move.received_quantity and move.accepted_quantity:
#                 move.rejected_quantity = move.received_quantity - move.accepted_quantity
#             else:
#                 move.rejected_quantity = 0.0
#
#     @api.onchange('product_uom_qty', 'quantity_done')
#     def _onchange_grn_quantities(self):
#         for move in self:
#             # Populate PO Quantity and Received Quantity only if empty
#             if not move.po_quantity:
#                 move.po_quantity = move.product_uom_qty
#             if not move.received_quantity:
#                 move.received_quantity = move.quantity_done

# #
# # from odoo import models, fields, api
# #
# # class StockMove(models.Model):
# #     _inherit = 'stock.move'
# #
# #     po_quantity = fields.Float(string='PO Quantity')
# #     received_quantity = fields.Float(string='Received Quantity')
# #     # rejected_quantity = fields.Float(string='Rejected Quantity')
# #     rejected_quantity = fields.Float(string='Rejected Quantity', compute='_compute_rejected_quantity', store=True)
# #     accepted_quantity = fields.Float(string='Accepted Quantity')
# #     rejection = fields.Char(string='Reason for Rejection')
# #
# #     @api.onchange('quantity_done', 'product_uom_qty')
# #     def _onchange_quantity_done(self):
# #         for move in self:
# #             move.po_quantity = move.product_uom_qty
# #             move.received_quantity = move.quantity_done
# #             move.accepted_quantity = move.quantity_done
# #
# #
# #
# #     @api.depends('move_line_ids')
# #     def _compute_rejected_quantity(self):
# #         """
# #         Get scrapped quantity for this move.
# #         Scraps are stored in stock.scrap model, linked to the move by product & picking.
# #         """
# #         for move in self:
# #             scrap_qty = self.env['stock.scrap'].search([
# #                 ('product_id', '=', move.product_id.id),
# #                 ('picking_id', '=', move.picking_id.id),
# #             ])
# #             move.rejected_quantity = sum(scrap_qty.mapped('scrap_qty'))
#
#
# from odoo import models, fields, api
#
# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     po_quantity = fields.Float(string='PO Quantity')
#     received_quantity = fields.Float(string='Received Quantity')
#     rejected_quantity = fields.Float(string='Rejected Quantity')  # Editable now
#     accepted_quantity = fields.Float(string='Accepted Quantity')
#     rejection = fields.Char(string='Reason for Rejection')
#
#     @api.onchange('quantity_done', 'product_uom_qty', 'rejected_quantity')
#     def _onchange_quantities(self):
#         """
#         Update quantities when done qty, PO qty, or rejected qty changes.
#         """
#         for move in self:
#             move.po_quantity = move.product_uom_qty
#             move.received_quantity = move.quantity_done
#             move.accepted_quantity = move.quantity_done - (move.rejected_quantity or 0)
#
#
#
# from odoo import models, fields, api
#
#
# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     po_quantity = fields.Float(string='PO Quantity')
#     received_quantity = fields.Float(string='Received Quantity')
#     rejected_quantity = fields.Float(string='Rejected Quantity')  # Editable now
#     accepted_quantity = fields.Float(string='Accepted Quantity')
#     rejection = fields.Char(string='Reason for Rejection')
#     scrap_created = fields.Boolean(string='Scrap Created', default=False)
#
#     @api.onchange('quantity_done', 'product_uom_qty', 'rejected_quantity')
#     def _onchange_quantities(self):
#         """
#         Update quantities when done qty, PO qty, or rejected qty changes.
#         """
#         for move in self:
#             move.po_quantity = move.product_uom_qty
#             move.received_quantity = move.quantity_done
#             move.accepted_quantity = move.quantity_done - (move.rejected_quantity or 0)
#
#     def write(self, vals):
#         """Override write method to create scrap when rejected_quantity is updated"""
#         result = super(StockMove, self).write(vals)
#
#         # Check if rejected_quantity was updated
#         if 'rejected_quantity' in vals:
#             for move in self:
#                 if move.rejected_quantity > 0 and not move.scrap_created:
#                     move._create_scrap_for_rejection()
#                     move.scrap_created = True
#
#         return result
#
#     def _create_scrap_for_rejection(self):
#         """Create scrap record for rejected quantity"""
#         self.ensure_one()
#
#         if self.rejected_quantity <= 0:
#             return
#
#         # Find or get default scrap location
#         scrap_location = self.env['stock.location'].search([
#             ('scrap_location', '=', True)
#         ], limit=1)
#
#         if not scrap_location:
#             # Create a default scrap location if none exists
#             scrap_location = self.env['stock.location'].create({
#                 'name': 'Scrap Location',
#                 'location_id': self.env.ref('stock.stock_location_locations').id,
#                 'scrap_location': True,
#                 'usage': 'inventory',
#             })
#
#         # Create scrap record
#         scrap_vals = {
#             'product_id': self.product_id.id,
#             'product_uom_id': self.product_uom.id,
#             'scrap_qty': self.rejected_quantity,
#             'location_id': self.location_dest_id.id,  # Source location (where stock was received)
#             'scrap_location_id': scrap_location.id,  # Destination (scrap location)
#             'origin': f"GRN Rejection: {self.picking_id.name}" if self.picking_id else "GRN Rejection",
#             'name': f"Rejection from {self.picking_id.name}" if self.picking_id else f"Rejection - {self.product_id.name}",
#         }
#
#         # Add rejection reason if available
#         if self.rejection:
#             scrap_vals['name'] += f" - Reason: {self.rejection}"
#
#         # Create the scrap record
#         scrap = self.env['stock.scrap'].create(scrap_vals)
#
#         # Optionally, you can auto-validate the scrap
#         # Uncomment the next line if you want to auto-validate scraps
#         # scrap.action_validate()
#
#         return scrap
#
#     @api.model
#     def create(self, vals):
#         """Override create method to handle rejection on creation"""
#         result = super(StockMove, self).create(vals)
#
#         # If rejected quantity is set during creation
#         if vals.get('rejected_quantity', 0) > 0:
#             result._create_scrap_for_rejection()
#             result.scrap_created = True
#
#         return result











from odoo import models, fields, api
from odoo.exceptions import UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    po_quantity = fields.Float(string='PO Quantity', compute='_compute_po_quantity', store=True)
    received_quantity = fields.Float(string='Received Quantity', compute='_compute_received_quantity', store=True)
    rejected_quantity = fields.Float(string='Rejected Quantity')  # Editable now
    accepted_quantity = fields.Float(string='Accepted Quantity', compute='_compute_accepted_quantity', store=True)
    rejection = fields.Char(string='Reason for Rejection')
    scrap_created = fields.Boolean(string='Scrap Created', default=False)
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line', index=True)

    @api.depends('purchase_line_id.product_qty', 'product_uom_qty')
    def _compute_po_quantity(self):
        for move in self:
            if move.purchase_line_id:
                move.po_quantity = move.purchase_line_id.product_uom._compute_quantity(
                    move.purchase_line_id.product_qty,
                    move.product_uom
                )
            else:
                move.po_quantity = move.product_uom_qty

    @api.depends('quantity_done')
    def _compute_received_quantity(self):
        for move in self:
            move.received_quantity = move.quantity_done

    @api.depends('received_quantity', 'rejected_quantity')
    def _compute_accepted_quantity(self):
        for move in self:
            move.accepted_quantity = move.received_quantity - (move.rejected_quantity or 0)

#     @api.onchange('rejected_quantity')
#     def _onchange_rejected_quantity(self):
#         """Trigger scrap creation when rejected quantity changes."""
#         for move in self:
#             if move.rejected_quantity > 0 and not move.scrap_created:
#                 move._create_scrap_for_rejection()
#                 move.scrap_created = True
# #
#     def write(self, vals):
#         """Override write to handle scrap creation."""
#         res = super(StockMove, self).write(vals)
#
#         if 'rejected_quantity' in vals:
#             for move in self:
#                 if move.rejected_quantity > 0 and not move.scrap_created:
#                     move._create_scrap_for_rejection()
#                     move.scrap_created = True
#         return res
#
#     def _create_scrap_for_rejection(self):
#         for move in self:
#             if move.rejected_quantity > 0 and not move.scrap_created:
#                 scrap_location = self.env['stock.location'].search([
#                     ('scrap_location', '=', True),
#                     ('company_id', '=', move.company_id.id)
#                 ], limit=1)
#                 if not scrap_location:
#                     raise UserError("No scrap location found for this company.")
#
#                 self.env['stock.scrap'].create({
#                     'product_id': move.product_id.id,
#                     'scrap_qty': move.rejected_quantity,
#                     'product_uom_id': move.product_uom.id,
#                     'location_id': move.location_id.id,
#                     'scrap_location_id': scrap_location.id,
#                     'company_id': move.company_id.id,
#                     'origin': move.origin,
#                 })
#                 move.scrap_created = True
