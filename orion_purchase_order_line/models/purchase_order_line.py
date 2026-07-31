from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    specification = fields.Text(
        string='Specification',
        help='Product specification details'
    )