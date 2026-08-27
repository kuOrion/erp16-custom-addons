# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import _, api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    sh_auto_assign_serial_no = fields.Boolean(string='Auto Assign Serial Number', default=True)