# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import _, api, fields, models

class ShFinishedProduct(models.Model):
    _name = 'sh.finished.product'
    _description = 'Finished Product'

    name = fields.Char(string='Name',related='production_id.name',store=True)
    product_id = fields.Many2one('product.product', string='Product')
    sh_serial_no = fields.Char(string='Serial No')
    sh_product_qty = fields.Float(string='Product Qty')
    location_id = fields.Many2one('stock.location',related='production_id.location_dest_id', string='Location')
    production_id = fields.Many2one('mrp.production', string='Production')
    company_id = fields.Many2one(
        'res.company', 'Company', default=lambda self: self.env.company,
        index=True, required=True)
    lot_id = fields.Many2one('stock.lot', string='Lot/Serial Number')
    lot_ids = fields.One2many('stock.lot','sh_finished_product_id', string='Lot/Serial No')

    
    def sh_show_details_action(self):
        return {
            'name': _('Product Details'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'sh.finished.product',
            'res_id': self.id,
            'target': 'new',
        }
