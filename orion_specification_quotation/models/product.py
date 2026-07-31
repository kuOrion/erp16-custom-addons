from odoo import models, fields, api

class ProductProduct(models.Model):
    _inherit = 'product.product'

    n_specification_display = fields.Text(
        string="N Specification",
        compute="_compute_n_specification_display",
        store=False,
        readonly=True
    )

    def _compute_n_specification_display(self):
        for product in self:
            # Search for the N Specification in sh.product.variant.extra.line
            extra_line = self.env['sh.product.variant.extra.line'].search([
                ('sh_product_id', '=', product.id),
                ('sh_name', '=', 'N Specification')
            ], limit=1)
            product.n_specification_display = extra_line.sh_value if extra_line else False