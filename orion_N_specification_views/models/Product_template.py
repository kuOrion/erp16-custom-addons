from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    n_specification_desc = fields.Char(
        string='N Specification',
        compute='_compute_n_specification_desc',
        store=True,
        readonly=True,
        help='Description from N specification attribute value'
    )

    @api.depends('attribute_line_ids',
                 'attribute_line_ids.value_ids',
                 'attribute_line_ids.attribute_id.name')
    def _compute_n_specification_desc(self):
        """Compute N specification description from attribute values"""
        for record in self:
            description = ''
            for line in record.attribute_line_ids:
                # Check if attribute name contains 'N specification' (case-insensitive)
                if line.attribute_id.name and 'n specification' in line.attribute_id.name.lower():
                    # Get the first value's description
                    if line.value_ids:
                        for value in line.value_ids:
                            # Check if description field exists and has value
                            if hasattr(value, 'description') and value.description:
                                description = value.description
                                break
                    if description:
                        break
            record.n_specification_desc = description


# class ProductProduct(models.Model):
#     _inherit = 'product.product'
#
#     n_specification_desc = fields.Char(
#         string='N Specification',
#         compute='_compute_n_specification_desc',
#         store=True,
#         readonly=True,
#         help='Description from N specification attribute value'
#     )
#
#     @api.depends('product_template_attribute_value_ids',
#                  'product_template_attribute_value_ids.product_attribute_value_id',
#                  'product_template_attribute_value_ids.attribute_id.name')
#     def _compute_n_specification_desc(self):
#         """Compute N specification description from variant attribute values"""
#         for record in self:
#             description = ''
#             for ptav in record.product_template_attribute_value_ids:
#                 # Check if attribute name contains 'N specification' (case-insensitive)
#                 if ptav.attribute_id.name and 'n specification' in ptav.attribute_id.name.lower():
#                     # Check if description field exists and has value
#                     if hasattr(ptav.product_attribute_value_id, 'description') and ptav.product_attribute_value_id.description:
#                         description = ptav.product_attribute_value_id.description
#                         break
#             record.n_specification_desc = description

from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    n_specification_desc = fields.Char(
        string='N Specification',
        compute='_compute_n_specification_desc',
        store=True,
        readonly=True
    )

    @api.depends(
        'product_template_attribute_value_ids',
        'product_template_attribute_value_ids.product_attribute_value_id',
        'product_template_attribute_value_ids.product_attribute_value_id.description',
        'product_template_attribute_value_ids.attribute_id.name'
    )
    def _compute_n_specification_desc(self):

        for record in self:

            # If no variant attributes exist → do not show specification
            if not record.product_template_attribute_value_ids:
                record.n_specification_desc = False
                continue

            description = False

            for ptav in record.product_template_attribute_value_ids:

                if ptav.attribute_id.name and 'n specification' in ptav.attribute_id.name.lower():

                    value = ptav.product_attribute_value_id

                    description = value.description or value.name
                    break

            record.n_specification_desc = description