# -*- coding: utf-8 -*-
# Part of softhealer. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class InheritResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_product_int_ref_gen = fields.Boolean("Product internal reference generator feature",related="company_id.sh_product_int_ref_gen",readonly=False)
    sh_pdt_attr_digit = fields.Integer("Product attribute name digit",related="company_id.sh_pdt_attr_digit",readonly=False)
    sh_pdt_seq_sep = fields.Char("Existing product sequence separate",related="company_id.sh_pdt_seq_sep",readonly=False)
    sh_pdt_new_seq_sep = fields.Char(string="Product attribute sequence separate",related="company_id.sh_pdt_new_seq_sep",readonly=False)

    def generate_int_ref(self):
        products = self.env['product.product'].search([])
        for product in products:
            product._custom_default_code()


class InheritResCompany(models.Model):
    _inherit = 'res.company'

    sh_product_int_ref_gen = fields.Boolean("Product internal reference generator feature",readonly=False)
    sh_pdt_attr_digit = fields.Integer("Product attribute name digit",readonly=False)
    sh_pdt_seq_sep = fields.Char("Existing product sequence separate",readonly=False)
    sh_pdt_new_seq_sep = fields.Char(string="New Product sequence separate",readonly=False)
