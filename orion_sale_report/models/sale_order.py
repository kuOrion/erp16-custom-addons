from odoo import models

class SaleOrderr(models.Model):
    _inherit = 'sale.order'

    def get_first_contact(self):
        self.ensure_one()
        contact = self.partner_id.child_ids.filtered(lambda p: p.type == 'contact')
        partner = contact[:1] if contact else self.partner_id
        return partner.name