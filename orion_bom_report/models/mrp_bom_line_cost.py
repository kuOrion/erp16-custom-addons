from odoo import models, fields, api

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    component_cost = fields.Float(
        string='Cost',
        compute='_compute_component_cost',
        store=True
    )

    @api.depends('product_id', 'product_qty')
    def _compute_component_cost(self):
        for line in self:
            cost = line.product_id.standard_price or 0.0
            line.component_cost = cost * line.product_qty
