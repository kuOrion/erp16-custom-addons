# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields,api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    sh_finished_product_id = fields.Many2one('sh.finished.product', string='Finished Product')
    sh_config_prifix_type = fields.Char(string='Serial No Prefix 1')
    
    
    @api.model
    def sh_get_next_serial(self, company, product, prifix, serial_type):
        """Custom Method for Return the next serial number to be attributed to the product."""
        if product.tracking != "none":
            last_serial = self.env['stock.lot'].search(
                [('company_id', '=', company.id), ('sh_config_prifix_type', '=', prifix)],
                limit=1, order='id DESC')
            if last_serial:
                return self.env['stock.lot'].generate_lot_names(last_serial.name, 2)[1]
        return False
    
    @api.model
    def _get_next_serial(self, company, product):
        """Return the next serial number to be attributed to the product."""
        if product.tracking != "none":
            last_serial = self.env['stock.lot'].search(
                [('company_id', '=', company.id), ('product_id', '=', product.id),('sh_config_prifix_type', '=', None)],
                limit=1, order='id DESC')
            if last_serial:
                return self.env['stock.lot'].generate_lot_names(last_serial.name, 2)[1]
        return False
    