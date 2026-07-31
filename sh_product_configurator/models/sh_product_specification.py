# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import models, fields, api


class ShProductVariantSpecLine(models.Model):
    _name = 'sh.product.variant.spec.line'
    _description = 'SH Variant Specification Line'

    sh_product_id = fields.Many2one(
        'product.product', ondelete='cascade', required=True)
    sh_name = fields.Char(string="Attribute")
    sh_value = fields.Char(string="Description")

class ShProductVariantExtraLine(models.Model):
    _name = 'sh.product.variant.extra.line'
    _description = 'SH Variant Extra Specification Line'

    sh_product_id = fields.Many2one(
        'product.product', ondelete='cascade', required=True)
    sh_name = fields.Char(string="Name")
    sh_value = fields.Char(string="Value")

class ProductProduct(models.Model):
    _inherit = 'product.product'

    # MIDDLE – auto spec from attributes (computed)
    sh_spec_line_ids = fields.One2many(
        'sh.product.variant.spec.line',
        'sh_product_id',
        string="Specification Lines",
        compute="_compute_sh_spec_lines",
        readonly=True,
        store=True,
    )

    # RIGHT – manual spec lines
    sh_extra_spec_line_ids = fields.One2many(
        'sh.product.variant.extra.line',
        'sh_product_id',
        string="Extra Specification",
    )

    @api.depends(
        'product_template_attribute_value_ids',
        'product_template_attribute_value_ids.product_attribute_value_id',
        'product_template_attribute_value_ids.product_attribute_value_id.description',
    )
    def _compute_sh_spec_lines(self):
        for product in self:
            commands = [(5, 0, 0)]  # clear existing lines
            for ptav in product.product_template_attribute_value_ids.sorted(
                    key=lambda v: v.id): # This is the current sorting
                attr_name = ptav.attribute_id.name or ''
                desc = ptav.product_attribute_value_id.description or ''
                line_data = {
                    'sh_product_id': product.id,
                    'sh_name': attr_name,
                    'sh_value': desc,
                }
                commands.append((0, 0, line_data))
            product.sh_spec_line_ids = commands

    @api.model_create_multi
    def create(self, vals_list):
        products = super(ProductProduct, self).create(vals_list)
        products._compute_sh_spec_lines()
        return products

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        if any(key in vals for key in ['product_template_attribute_value_ids', 'attribute_line_ids', 'active']):
            self._compute_sh_spec_lines()
        return res

    def read(self, fields=None, load='_classic_read'):
        if not fields or 'sh_spec_line_ids' in fields:
            self._compute_sh_spec_lines()
        return super(ProductProduct, self).read(fields=fields, load=load)