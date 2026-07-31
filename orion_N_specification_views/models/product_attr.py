from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    n_specification_display = fields.Text(
        string="N Specification",
        compute="_compute_n_specification_display",
        store=False,
        readonly=True
    )

    def _compute_n_specification_display(self):
        for template in self:
            spec_value = False
            # Search in product.template.attribute.value (standard Odoo model)
            attr_value = self.env['product.template.attribute.value'].search([
                ('product_tmpl_id', '=', template.id),
                ('attribute_id.name', '=', 'N Specification')
            ], limit=1)
            if attr_value:
                # The description is on the product.attribute.value
                spec_value = attr_value.product_attribute_value_id.description or attr_value.product_attribute_value_id.name
            template.n_specification_display = spec_value