# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models, _, api
from lxml import etree
from odoo.models import BaseModel
import odoo
import xml.etree.ElementTree as ET
import json


class AccessManager(models.Model):
    _name = "sh.field.access"
    _description = "Field Access"

    model_id = fields.Many2one('ir.model', string="Model")
    # field_ids = fields.Many2many(
    #     "ir.model.fields", domain="[('model_id','=',model_id),('required','=',False)]", string="Fields")
    
    field_ids = fields.Many2many('ir.model.fields', 'hide_field_ir_model_fields_rel', 'hide_field_id', 'ir_field_id', string='Field')


    # field_ids = fields.Many2many(
    #     "ir.model.fields", domain="[('model_id','=',model_id)]", string="Fields")
    readonly = fields.Boolean("Readonly")
    required = fields.Boolean("Required")
    invisible = fields.Boolean("Invisible")
    access_manager_id = fields.Many2one(
        "sh.access.manager", string="Access Manager")


class Model(models.AbstractModel):
    _inherit = 'base'

    @api.model
    def get_view(self, view_id=None, view_type='form', **options):
        """ get_view([view_id | view_type='form'])

        Get the detailed composition of the requested view like model, view architecture

        :param int view_id: id of the view or None
        :param str view_type: type of the view to return if view_id is None ('form', 'tree', ...)
        :param dict options: boolean options to return additional features:
            - bool mobile: true if the web client is currently using the responsive mobile view
            (to use kanban views instead of list views for x2many fields)
        :return: composition of the requested view (including inherited views and extensions)
        :rtype: dict
        :raise AttributeError:

            * if the inherited view has unknown position to work with other than 'before', 'after', 'inside', 'replace'
            * if some tag other than 'position' is found in parent view

        :raise Invalid ArchitectureError: if there is view type other than form, tree, calendar, search etc... defined on the structure
        """
        view = self.env['ir.ui.view'].sudo().browse(view_id)
        self.check_access_rights('read')

        result = dict(self._get_view_cache(view_id, view_type, **options))

        node = etree.fromstring(result['arch'])
        node = self.env['ir.ui.view']._postprocess_access_rights(node)
        node = self.env['ir.ui.view']._postprocess_context_dependent(node)
        result['arch'] = etree.tostring(
            node, encoding="unicode").replace('\t', '')
        root = ET.fromstring(result['arch'])

        domain = [('access_manager_id.active_rule', '=', True), ('model_id.model', '=',
                                                                 result['model']), ('access_manager_id.responsible_user_ids', 'in', self.env.user.ids)]
        find_field_access = self.env['sh.field.access'].sudo().search(domain)
        # for view_type in root.iter('type'):
        if find_field_access:
            for fields_access in find_field_access:
                for fields in fields_access.field_ids:
                    for field_elem in root.iter('field'):
                        if field_elem.attrib.get('name') == fields.name and view_type == 'form':
                            if field_elem.attrib.get('modifiers'):
                                modifiers_dict = json.loads(
                                    field_elem.attrib['modifiers'])
                                if fields_access.readonly:
                                    modifiers_dict['readonly'] = True
                                    updated_modifiers = json.dumps(
                                        modifiers_dict)
                                    field_elem.attrib['modifiers'] = updated_modifiers
                                if fields_access.required:
                                    modifiers_dict['required'] = True
                                    updated_modifiers = json.dumps(
                                        modifiers_dict)
                                    field_elem.attrib['modifiers'] = updated_modifiers
                                if fields_access.invisible:
                                    modifiers_dict['invisible'] = True
                                    updated_modifiers = json.dumps(
                                        modifiers_dict)
                                    field_elem.attrib['modifiers'] = updated_modifiers
                            else:
                                if fields_access.readonly:
                                    sh_readonly_dict = '{"readonly": true}'
                                    field_elem.attrib['modifiers'] = sh_readonly_dict
                                if fields_access.required:
                                    sh_required_dict = '{"required": true}'
                                    field_elem.attrib['modifiers'] = sh_required_dict
                                if fields_access.invisible:
                                    sh_invisible_dict = '{"invisible": true}'
                                    field_elem.attrib['modifiers'] = sh_invisible_dict

                    for label_elem in root.iter('label'):
                        if label_elem.attrib.get('for') == fields.name and view_type == 'form':
                            if fields_access.invisible:
                                # label_elem.attrib['class'] = "d-none"
                                if label_elem.attrib.get('modifiers'):
                                    label_modifiers_dict = json.loads(
                                        label_elem.attrib['modifiers'])
                                    label_modifiers_dict['invisible'] = True
                                else:
                                    sh_invisible_dict = '{"invisible": true}'
                                    label_elem.attrib['modifiers'] = sh_invisible_dict

        # for field_elem in root.iter('field'):
        #     if field_elem.attrib.get('name') == 'responsible_user_ids':
        #         print("\n\n\n\n field_elem before",field_elem.attrib)
        #         if field_elem.attrib.get('modifiers'):
        #             # Convert modifiers JSON string to a dictionary
        #             modifiers_dict = json.loads(field_elem.attrib['modifiers'])

        #             # Add the "readonly" key with the value "true" to the modifiers dictionary
        #             modifiers_dict['readonly'] = True

        #             # Convert modifiers dictionary back to a JSON string
        #             updated_modifiers = json.dumps(modifiers_dict)

        #             # Update the response with the modified modifiers string
        #             field_elem.attrib['modifiers'] = updated_modifiers

        # Convert the modified XML back to a string
        modified_xml_string = ET.tostring(
            root, encoding='unicode').replace('\t', '')

        result['arch'] = modified_xml_string

        return result
