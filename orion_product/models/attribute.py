from odoo import models, fields, api


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'
    description = fields.Text(string="Description")


# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#
#     attribute_descriptions = fields.Char(compute='_compute_attribute_descriptions', store=True)
#
#     @api.depends('product_template_attribute_value_ids.product_attribute_value_id.description')
#     def _compute_attribute_descriptions(self):
#         for product in self:
#             descriptions = [
#                 val.product_attribute_value_id.description
#                 for val in product.product_template_attribute_value_ids
#                 if val.product_attribute_value_id.description
#             ]
#             product.attribute_descriptions = ', '.join(descriptions)