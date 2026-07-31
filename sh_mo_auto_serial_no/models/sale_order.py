# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def action_view_mrp_production(self):
        action = super(SaleOrder, self).action_view_mrp_production()
        ctx = dict(action.get('context') or {})
        ctx.update({
            'search_default_sh_main_mo': True,
        })
        action['context'] = ctx

        return action
       