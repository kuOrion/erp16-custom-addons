from odoo import api, fields, models


class ProductConfigStepWizard(models.TransientModel):
    _inherit = 'product.configurator.wizard'

    internal_reference = fields.Char(
        string='Internal Reference',
        related='product_template_id.default_code',
        readonly=True,
        help="Product's internal reference/code",
    )
