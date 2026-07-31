# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models

class AccessManager(models.Model):
    _name = "sh.access.manager"
    _description = "Access Management"

    name = fields.Char("Name")
    responsible_user_ids = fields.Many2many("res.users",string="Users")
    company_id = fields.Many2one("res.company",string="Company")
    created_by = fields.Many2one("res.users",string="Created By")
    active_rule = fields.Boolean("Active",default="True")

    # pages
    sh_hide_menu_ids = fields.Many2many(comodel_name="ir.ui.menu",string="Hide Menu")
    sh_access_model_line = fields.One2many("sh.access.model",'access_manager_id',string="Access Model")    
    sh_field_access_line = fields.One2many("sh.field.access",'access_manager_id',string="Field Access")    
    sh_navbar_button_line = fields.One2many('sh.navbar.buttons.access','access_manager_id','Navbar Button Access')
    sh_hide_chatter_line = fields.One2many("sh.hide.chatter",'access_manager_id',string="Hide Chatter")

    def write(self,vals):
        self.env['ir.ui.menu'].sudo().clear_caches()
        # field_access = self.env['sh.field.access'].sudo().fields_view_get()
        # print("\n\n\n\n>>>>>> field_access >>>", field_access)
        res = super(AccessManager,self).write(vals)
        return res
    
    def unlink(self):
        self.sh_navbar_button_line.unlink()
        return super(AccessManager, self).unlink()
