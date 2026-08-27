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

    def write(self, vals):
        prefix_keys = [key for key in ('sh_prefix_type1', 'sh_prefix_type2') if key in vals]
        old_prefixes = {}
        if prefix_keys:
            for company in self:
                old_prefixes[company.id] = (company.sh_prefix_type1, company.sh_prefix_type2)
        result = super().write(vals)
        if prefix_keys:
            for company in self:
                old_type1, old_type2 = old_prefixes.get(company.id, (False, False))
                if 'sh_prefix_type1' in vals and company.sh_prefix_type1 != old_type1:
                    company._sh_sync_serial_sequence(
                        'mrp_serial_assign.serial.type1',
                        company.sh_prefix_type1,
                        company.sh_number_of_degit_type1,
                    )
                if 'sh_prefix_type2' in vals and company.sh_prefix_type2 != old_type2:
                    company._sh_sync_serial_sequence(
                        'mrp_serial_assign.serial.type2',
                        company.sh_prefix_type2,
                        company.sh_number_of_degit_type2,
                    )
        return result

    def _sh_sync_serial_sequence(self, sequence_code, prefix, padding):
        """Keep the Type 1/Type 2 sequence aligned with the Settings prefix.

        New unused prefix → next number is 1.
        Prefix that already has lot names → continue from max suffix + 1
        so existing serials are not duplicated.
        """
        self.ensure_one()
        if not prefix:
            return
        existing_lots = self.env['stock.lot'].search([
            ('company_id', '=', self.id),
            ('name', '=like', '%s%%' % prefix),
        ])
        max_number = 0
        for lot in existing_lots:
            suffix = (lot.name or '')[len(prefix):]
            if suffix.isdigit():
                max_number = max(max_number, int(suffix))
        number_next = max_number + 1
        sequence = self.env['ir.sequence'].sudo().search([
            ('code', '=', sequence_code),
            ('company_id', 'in', [self.id, False]),
        ], limit=1)
        if sequence:
            sequence.sudo().write({
                'prefix': prefix,
                'padding': padding,
                'number_next': number_next,
            })


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_number_of_degit_type1 = fields.Integer(string='Number Of Degit', related='company_id.sh_number_of_degit_type1', readonly=False)
    sh_prefix_type1 = fields.Char(string='Prefix', related='company_id.sh_prefix_type1', readonly=False)
    sh_confirirmation_message_type1 = fields.Char(string='Confirmation Message', related='company_id.sh_confirirmation_message_type1', readonly=False)
    sh_number_of_degit_type2 = fields.Integer(string='Number Of Degit', related='company_id.sh_number_of_degit_type2', readonly=False)
    sh_prefix_type2 = fields.Char(string='Prefix', related='company_id.sh_prefix_type2', readonly=False)
    sh_confirirmation_message_type2 = fields.Char(string='Confirmation Message', related='company_id.sh_confirirmation_message_type2', readonly=False)