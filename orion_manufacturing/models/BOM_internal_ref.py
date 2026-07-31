from odoo import models, fields

class MrpBomLine(models.Model):
    _inherit = 'mrp.bom.line'

    product_internal_reference = fields.Char(
        string='Internal Reference',
        related='product_id.default_code',
        readonly=True,
        store=True,
        help='Internal reference for the product or component in this Bill of Material'
    )