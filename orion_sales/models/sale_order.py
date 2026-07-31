from odoo import models, fields, api
from num2words import num2words


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    total_inr = fields.Float(string="Total (INR)", compute="_compute_totals", store=True)
    round_off = fields.Float(string="Round Off", compute="_compute_totals", store=True)
    grand_total_inr = fields.Float(string="Grand Total (INR)", compute="_compute_totals", store=True)
    grand_total_in_words = fields.Char(string="Grand Total (in Words)", compute="_compute_totals", store=True)


    @api.depends('order_line.price_subtotal')
    def _compute_totals(self):
        for order in self:
            total = sum(line.price_subtotal for line in order.order_line)
            decimal_part = total - int(total)

            grand_total = int(total) + (1 if decimal_part >= 0.50 else 0)
            round_off = grand_total - total

            order.total_inr = total
            order.round_off = round_off
            order.grand_total_inr = grand_total
            order.grand_total_in_words = num2words(grand_total, lang='en').capitalize()



