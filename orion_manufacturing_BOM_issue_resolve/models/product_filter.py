from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    has_bom = fields.Boolean(
        string='Has BOM',
        compute='_compute_has_bom',
        store=True
    )

    @api.depends()
    def _compute_has_bom(self):
        bom_obj = self.env['mrp.bom']
        for product in self:
            product.has_bom = bool(
                bom_obj.search_count([
                    ('product_tmpl_id', '=', product.id)
                ])
            )