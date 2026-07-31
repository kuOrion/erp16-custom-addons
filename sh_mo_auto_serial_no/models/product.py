# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sh_auto_assign_serial_no = fields.Boolean(string='Auto Assign Serial Number', default=False)

    @api.onchange('tracking')
    def _onchange_tracking(self):
        if self.tracking == 'serial':
            self.sh_auto_assign_serial_no = True
        else:
            self.sh_auto_assign_serial_no = False
        return self.mapped('product_variant_ids')._onchange_tracking()
    
    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplate, self).create(vals_list)
        if res.tracking == 'serial':
            res.sh_auto_assign_serial_no = True
        return res
    
class Product(models.Model):
    _inherit = "product.product"

    sh_auto_assign_serial_no = fields.Boolean(string='Auto Assign Serial Number',related='product_tmpl_id.sh_auto_assign_serial_no',readonly=False, default=False)

    @api.onchange('tracking')
    def _onchange_tracking(self):
        if self.tracking == 'serial':
            self.sh_auto_assign_serial_no = True
        else:
            self.sh_auto_assign_serial_no = False
        if any(product.tracking != 'none' and product.qty_available > 0 for product in self):
            return {
                'warning': {
                    'title': _('Warning!'),
                    'message': _("You have product(s) in stock that have no lot/serial number. You can assign lot/serial numbers by doing an inventory adjustment.")}}

    @api.model_create_multi
    def create(self, vals_list):
        res = super(Product, self).create(vals_list)
        if res.tracking == 'serial':
            res.sh_auto_assign_serial_no = True
        return res
    