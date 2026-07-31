# -*- coding: utf-8 -*-
# Part of softhealer. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class InheritProductAttribute(models.Model):
    _inherit = 'product.attribute'

    sh_parent_attribute = fields.Many2one('product.attribute',string='Parent Attribute')
    sh_parent_value = fields.Many2one('product.attribute.value',string='Parent Value', domain=[('attribute_id','=',sh_parent_attribute)])
    sh_product_tmpl_id = fields.Many2one('product.template', string='Product Template', readonly=True)
    description = fields.Char(string='Description')
    create_variant = fields.Selection(default='dynamic')
    sh_is_custom_attribute = fields.Boolean(string='Is Custom Attribute')

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only the System Administrator can create new Product Attribute."))
        for vals in vals_list:
            # Check if parent info is already in vals (e.g., from a direct create with parent info)
            if not vals.get('sh_parent_value') and not vals.get('sh_parent_attribute'):
                # Try to get the parent PTAV ID from active_id in context
                # In this scenario, active_id should be the ID of the product.template.attribute.value
                parent_ptav_id_from_context = self._context.get('active_id')
                if parent_ptav_id_from_context:
                    parent_ptav = self.env['product.template.attribute.value'].browse(parent_ptav_id_from_context)
                    if parent_ptav.exists():
                        vals['sh_parent_value'] = parent_ptav.id
                        vals['sh_parent_attribute'] = parent_ptav.attribute_id.id
                        vals['sh_is_custom_attribute'] = True
                        vals['sh_product_tmpl_id'] = parent_ptav.product_tmpl_id.id


        res = super().create(vals_list)
        return res


class InheritProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    description = fields.Char(string='Description')

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only the System Administrator can create new Product Attribute Values."))
        return super().create(vals_list)
