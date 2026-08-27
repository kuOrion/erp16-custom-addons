# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, _, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move.line'

    sh_select_record = fields.Boolean(
        string='Select',
    )
    
    # @api.onchange('sh_select_record')
    # def _onchange_sh_select_record(self):
    #     if self.sh_select_record:
    #         self.qty_done = 1
    #         self.reserved_uom_qty = self.qty_done
    #     else:
    #         self.reserved_uom_qty = 0
    #         self.qty_done = 0
        # self.move_id._compute_forecast_information()
        # self.move_id.picking_id.action_set_quantities_to_reservation()