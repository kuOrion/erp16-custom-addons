# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, _, fields, api

class StockMove(models.Model):
    _inherit = 'stock.location'

    def should_bypass_reservation(self):
        self.ensure_one()
        return self.usage in ('supplier','internal' ,'customer', 'inventory', 'production') or self.scrap_location or (self.usage == 'transit' and not self.company_id)