from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    amount_total_round = fields.Monetary(
        string="Total",
        compute="_compute_amount_total_round",
        currency_field='currency_id',
        store=True
    )

    @api.depends('amount_total')
    def _compute_amount_total_round(self):
        for order in self:
            order.amount_total_round = round(order.amount_total)
