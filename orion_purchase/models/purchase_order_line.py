from odoo import models, fields


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    product_uom = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        required=True,
        domain="[('category_id', '=', product_uom_category_id)]"
    )

    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id',
        store=True
    )