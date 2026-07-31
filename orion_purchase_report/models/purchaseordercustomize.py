from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    line_number = fields.Integer(string="Sr. No", compute="_compute_line_number", store=True)
    cgst = fields.Float(string="CGST (%)", default=0.0)
    sgst = fields.Float(string="SGST (%)", default=0.0)
    igst = fields.Float(string="IGST (%)", default=0.0)

    cgst_amount = fields.Float(string="CGST Amount", compute="_compute_tax_amount", store=True)
    sgst_amount = fields.Float(string="SGST Amount", compute="_compute_tax_amount", store=True)
    igst_amount = fields.Float(string="IGST Amount", compute="_compute_tax_amount", store=True)

    @api.depends('price_unit', 'product_qty', 'cgst', 'sgst', 'igst')
    def _compute_tax_amount(self):
        for line in self:
            base_amount = line.price_unit * line.product_qty
            line.cgst_amount = base_amount * (line.cgst / 100)
            line.sgst_amount = base_amount * (line.sgst / 100)
            line.igst_amount = base_amount * (line.igst / 100)

    @api.depends('order_id.order_line')
    def _compute_line_number(self):
        for order in self.mapped('order_id'):
            for index, line in enumerate(order.order_line, start=1):
                line.line_number = index
