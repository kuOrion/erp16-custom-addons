# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'

    child_attribute_line_ids = fields.One2many(
        'product.template.attribute.line',
        'parent_attribute_value_id',
        string="Sub-Attributes"
    )

    # sh_child_attribute_name_char = fields.Char(string='Child Attribute Name')
    description = fields.Char(
        string='Description',
        related='product_attribute_value_id.description',
        readonly=False,
        store=True
    )
    # sh_value_ids = fields.One2many('sh.product.template.attribute.value.line', 'sh_parent_value_id', string='Child Values')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(ProductTemplateAttributeValue, self).create(vals_list)
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only the System Administrator can create new product attribute values."))
        res._sync_child_attributes()
        return res

    def write(self, vals):
        res = super(ProductTemplateAttributeValue, self).write(vals)
        # Only sync if child_attribute_line_ids might have changed or if the record itself is updated
        if 'child_attribute_line_ids' in vals or any(field in vals for field in self._fields):
            self._sync_child_attributes()
        return res

    def _sync_child_attributes(self):
        for record in self:
            for child_line in record.child_attribute_line_ids:
                if child_line.attribute_id:
                    attribute_to_update = child_line.attribute_id

                    update_vals = {}
                    # Ensure parent_ptav.attribute_id exists before accessing its .id
                    if record.attribute_id and (not attribute_to_update.sh_parent_attribute or attribute_to_update.sh_parent_attribute.id != record.attribute_id.id):
                        update_vals['sh_parent_attribute'] = record.attribute_id.id

                    # Ensure parent_ptav.product_attribute_value_id exists before accessing its .id
                    if record.product_attribute_value_id and (not attribute_to_update.sh_parent_value or attribute_to_update.sh_parent_value.id != record.product_attribute_value_id.id):
                        update_vals['sh_parent_value'] = record.product_attribute_value_id.id

                    # Ensure product_tmpl_id exists before accessing its .id
                    if record.product_tmpl_id and (not attribute_to_update.sh_product_tmpl_id or attribute_to_update.sh_product_tmpl_id.id != record.product_tmpl_id.id):
                        update_vals['sh_product_tmpl_id'] = record.product_tmpl_id.id

                    if not attribute_to_update.sh_is_custom_attribute:
                        update_vals['sh_is_custom_attribute'] = True

                    if update_vals:
                        attribute_to_update.write(update_vals)

# class ShProductTemplateAttributeValueLine(models.Model):
#     _name = 'sh.product.template.attribute.value.line'
#     _description = 'Product Template Attribute Value Line'
#     _order = 'sequence'

    # sequence = fields.Integer('Sequence', default=10)
    # name = fields.Char('Value', required=True)
    # product_attribute_value_id_direct = fields.Many2one(
    #     'product.attribute.value',
    #     string='Direct Attribute Value',
    #     ondelete='restrict',
    #     help="Direct link to the product attribute value for synchronization."
    # )
    # description = fields.Char(
    #     'Description',
    #     related='product_attribute_value_id_direct.description',
    #     readonly=False,
    #     store=True
    # )
    # is_custom = fields.Boolean('Is Custom')
    # sh_parent_value_id = fields.Many2one('product.template.attribute.value', string='Parent Value', ondelete='cascade')
