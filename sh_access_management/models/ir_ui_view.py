# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, SUPERUSER_ID, _
from odoo.tools.translate import _
import ast

class ir_ui_view(models.Model):
    _inherit = 'ir.ui.view'

    def _postprocess_tag_button(self, node, name_manager, node_info):
        # Hide Any Button
        postprocessor = getattr(super(ir_ui_view, self), '_postprocess_tag_button', False)
        if postprocessor:
            super(ir_ui_view, self)._postprocess_tag_button(node, name_manager, node_info)

        hide = None
        hide_button_obj = self.env['sh.navbar.buttons.access']
        # hide_button_ids = hide_button_obj.sudo().search([('access_manager_id.company_ids','in',self.env.company.id),('model_id.model','=',name_manager.model._name),('access_manager_id.active','=',True),('access_manager_id.user_ids','in',self._uid)])
        hide_button_ids = hide_button_obj.sudo().search([('model_id.model','=',name_manager.model._name),('access_manager_id.active_rule','=',True),('access_manager_id.responsible_user_ids','in',self._uid)])

        # Filtered with same env user and current model
        sh_store_btn_data_ids = hide_button_ids.mapped('sh_store_btn_data_ids')
        # translation_obj = self.env['ir.translation']
        if sh_store_btn_data_ids:
            for btn in sh_store_btn_data_ids:
                if btn.sh_attribute_name == node.get('name'):
                    if node.get('string'):
                        # if translation_obj._get_source(None, ('model_terms',), self.env.lang, btn.sh_attribute_string, None) == node.get('string'):
                        if _(btn.sh_attribute_string) == node.get('string'):
                            hide = [btn]
                            break
                    else:
                        hide = [btn]
                        break
        if hide:
            node.set('invisible', '1')
            if 'attrs' in node.attrib.keys() and node.attrib['attrs']:
                del node.attrib['attrs']
            node_info['modifiers']['invisible'] = True


        return None
    


    def _postprocess_tag_page(self, node, name_manager, node_info):
        # Hide Any Notebook Page
        postprocessor = getattr(super(ir_ui_view, self), '_postprocess_tag_page', False)
        if postprocessor:
            super(ir_ui_view, self)._postprocess_tag_page(node, name_manager, node_info)

        hide = None
        hide_tab_obj = self.env['sh.navbar.buttons.access']
        # hide_tab_ids = hide_tab_obj.sudo().search([('access_manager_id.company_ids','in',self.env.company.id),('model_id.model','=',name_manager.model._name),('access_manager_id.active','=',True),('access_manager_id.user_ids','in',self._uid)])
        hide_tab_ids = hide_tab_obj.sudo().search([('model_id.model','=',name_manager.model._name),('access_manager_id.active_rule','=',True),('access_manager_id.responsible_user_ids','in',self._uid)])
        # translation_obj = self.env['ir.translation']
        # Filtered with same env user and current model
        sh_store_page_data_ids = hide_tab_ids.mapped('sh_store_page_data_ids')
        if sh_store_page_data_ids:
            for tab in sh_store_page_data_ids:
                # query = """SELECT value FROM ir_translation WHERE lang=%s AND type in (code) AND src=%s"""
                # self._cr.execute(query, params)
                # res = self._cr.fetchone()
                
                # if translation_obj._get_source(None, ('model_terms',), self.env.lang, tab.sh_attribute_string, None) == node.get('string'):
                if _(tab.sh_attribute_string) == node.get('string'):
                    if node.get('name'):
                        if tab.sh_attribute_name == node.get('name'):
                            hide = [tab]
                            break
                    else:
                        hide = [tab]
                        break    
        if hide:
            node.set('invisible', '1')
            if 'attrs' in node.attrib.keys() and node.attrib['attrs']:
                del node.attrib['attrs']
      
            node_info['modifiers']['invisible'] = True


        return None        