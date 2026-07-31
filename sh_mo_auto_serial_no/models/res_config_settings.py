# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    sh_number_of_degit_type1 = fields.Integer(string='Number Of Digit')
    sh_prefix_type1 = fields.Char(string='Prefix')
    sh_confirirmation_message_type1 = fields.Char(string='Confirmation Message')
    sh_number_of_degit_type2 = fields.Integer(string='Number Of Digit')
    sh_prefix_type2 = fields.Char(string='Prefix')
    sh_confirirmation_message_type2 = fields.Char(string='Confirmation Message')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_number_of_degit_type1 = fields.Integer(string='Number Of Degit', related='company_id.sh_number_of_degit_type1', readonly=False)
    sh_prefix_type1 = fields.Char(string='Prefix', related='company_id.sh_prefix_type1', readonly=False)
    sh_confirirmation_message_type1 = fields.Char(string='Confirmation Message', related='company_id.sh_confirirmation_message_type1', readonly=False)
    sh_number_of_degit_type2 = fields.Integer(string='Number Of Degit', related='company_id.sh_number_of_degit_type2', readonly=False)
    sh_prefix_type2 = fields.Char(string='Prefix', related='company_id.sh_prefix_type2', readonly=False)
    sh_confirirmation_message_type2 = fields.Char(string='Confirmation Message', related='company_id.sh_confirirmation_message_type2', readonly=False)