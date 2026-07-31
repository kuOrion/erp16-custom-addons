# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, _,api
from odoo.addons.web.controllers.utils import fix_view_modes,generate_views
import odoo
from odoo.http import request

def fix_view_modes(action):
    if not action.get('views'):
        generate_views(action)

    if action.pop('view_type', 'form') != 'form':
        return action

    if 'view_mode' in action:
        action['view_mode'] = ','.join(
            mode if mode != 'tree' else 'list'
            for mode in action['view_mode'].split(','))
    action['views'] = [
        [id, mode if mode != 'tree' else 'list']
        for id, mode in action['views']
    ]
    allowed_views = action['views']
    find_model = False
    domain = [('model', '=', 'sh.access.manager')]
    find_model = request.env['ir.model'].sudo().search(domain)
    if find_model:
        domain = [('active_rule', '=', True),('responsible_user_ids', 'in', request.env.user.ids)]
        find_access = request.env['sh.access.manager'].sudo().search(domain)
        if find_access:
            view_list = []
            for model_access in find_access.sh_access_model_line:
                if model_access.sudo().model_id.model == action['res_model']:                    
                    for allowed in allowed_views:
                        for views in model_access.view_ids:                           
                            if allowed[1] == views.technical_name and views.technical_name not in view_list:
                                view_list.append(views.technical_name)
            for views in view_list:
                for allowed in allowed_views:
                    if allowed[1] == views:
                        del allowed_views[allowed_views.index(allowed)]
            action['views'] = allowed_views            
    return action
odoo.addons.web.controllers.utils.fix_view_modes = fix_view_modes

class ViewList(models.Model):
    _name = "sh.view.list"
    _description = "Holds All Available Views"

    name = fields.Char("Name")
    technical_name = fields.Char("Tech Name")