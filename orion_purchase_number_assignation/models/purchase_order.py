from odoo import models, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = (
                self.env['ir.sequence'].next_by_code('purchase.rfq') or 'New'
            )
        return super().create(vals)

    def button_confirm(self):
        res = super().button_confirm()
        for order in self:
            if order.state in ['purchase', 'done']:
                order.name = (
                    self.env['ir.sequence'].next_by_code('purchase.po') or order.name
                )
        return res