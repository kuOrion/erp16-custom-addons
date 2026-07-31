from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    detailed_type = fields.Selection(
        selection=[
            ('consu', 'Consumable'),
            ('service', 'Service'),
            ('product', 'Storable Product'),
        ],
        string="Product Type",
        default="product",   # still keep default
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # If no product type is given, force Storable Product
            if not vals.get("detailed_type"):
                vals["detailed_type"] = "product"
        return super().create(vals_list)
