
from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    note = fields.Text(string="Note")
    non_standard = fields.Boolean(string="Non Standard")
    freight__ = fields.Float(string="Freight", default=0.00)
    insurance__ = fields.Float(string="Insurance", default=0.00)
    packing__ = fields.Float(string="Packing", default=0.00)

