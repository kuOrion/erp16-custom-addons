# from odoo import models, fields, api
#
# class StockLot(models.Model):
#     _inherit = 'stock.lot'
#
#     production_id = fields.Many2one(
#         'mrp.production',
#         string="Manufacturing Order",
#         compute='_compute_production_id',
#         store=True
#     )
#
#     @api.depends('quant_ids')
#     def _compute_production_id(self):
#         for lot in self:
#             production = False
#
#             # stock.move.line links to move_id, which links to production_id
#             move_lines = self.env['stock.move.line'].search([
#                 ('lot_id', '=', lot.id),
#                 ('move_id.production_id', '!=', False),
#             ], limit=1)
#
#             if move_lines:
#                 production = move_lines.move_id.production_id
#
#             lot.production_id = production

from odoo import models, fields, api

class StockLot(models.Model):
    _inherit = 'stock.lot'

    production_id = fields.Many2one(
        'mrp.production',
        string="Manufacturing Order",
        compute='_compute_production_id',
        store=True
    )

    current_location_id = fields.Many2one(
        'stock.location',
        string="Current Location",
        compute='_compute_current_location',
        store=True
    )

    @api.depends('quant_ids', 'quant_ids.location_id', 'quant_ids.quantity')
    def _compute_current_location(self):
        for lot in self:
            # Pick the internal location with highest qty
            quants = lot.quant_ids.filtered(
                lambda q: q.location_id.usage == 'internal' and q.quantity > 0
            )
            if quants:
                lot.current_location_id = quants.sorted('quantity', reverse=True)[0].location_id
            else:
                lot.current_location_id = False

    @api.depends('quant_ids')
    def _compute_production_id(self):
        for lot in self:
            production = False
            move_lines = self.env['stock.move.line'].search([
                ('lot_id', '=', lot.id),
                ('move_id.production_id', '!=', False),
            ], limit=1)
            if move_lines:
                production = move_lines.move_id.production_id
            lot.production_id = production