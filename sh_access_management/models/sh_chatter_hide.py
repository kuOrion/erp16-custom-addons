# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, api

class SmartButtonList(models.Model):
    _name = "sh.hide.chatter"
    _description = "Smart Button List"

    name = fields.Char("Navbar Name")
    model_ids = fields.Many2many('ir.model',string="Model")
    access_manager_id = fields.Many2one("sh.access.manager",string="Access Manager")

    @api.model
    def checkhide_chatter(self,kwargs):
        domain = [('access_manager_id.active_rule', '=', True),('access_manager_id.responsible_user_ids', 'in', [int(kwargs['user_id'])])]
        find_records = self.env['sh.hide.chatter'].sudo().search(domain)
        record_list = []
        if find_records:
            for records in find_records:
                for record in records.sudo().model_ids:
                    if record.model not in record_list:
                        record_list.append(record.model)
        return record_list