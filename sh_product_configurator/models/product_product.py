# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from datetime import timedelta, time
from odoo import fields, models, _, api, SUPERUSER_ID
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_id = fields.Many2one('product.product')
    product_uom_qty = fields.Float('Quantity', digits='Product Unit of Measure', default=1.0)
    product_template_id = fields.Many2one('product.template',string="Product")
    product_no_variant_attribute_value_ids = fields.Many2many(
        comodel_name='product.template.attribute.value',
        string="Extra Values",
        compute='_compute_no_variant_attribute_values',
        store=True, readonly=False, precompute=True, ondelete='restrict')

    # Override the field to remove the domain domain=[('attribute_line_id.value_count', '>', 1)]
    product_template_variant_value_ids = fields.Many2many(
        'product.template.attribute.value',
        relation='product_variant_combination',
        string="Variant Values",
        ondelete='restrict', domain=[]
    )

    product_custom_attribute_value_ids = fields.One2many(
        comodel_name='product.attribute.custom.value', inverse_name='sh_product_id',
        string="Custom Values",
        compute='_compute_custom_attribute_values',
        store=True, readonly=False, precompute=True, copy=True)

    show_product_template_field = fields.Boolean(compute="_compute_show_template_field", store=False)
    sh_is_created_manually = fields.Boolean()
    sh_is_record_saved = fields.Boolean()


    @api.depends('product_template_variant_value_ids')
    def _compute_show_template_field(self):
        for rec in self:
            rec.show_product_template_field = not bool(rec.product_template_variant_value_ids)

    def _custom_default_code(self):
        sep = self.env.company.sh_pdt_seq_sep
        if sep : sep = sep
        else : sep = ''

        digit = self.env.company.sh_pdt_attr_digit
        if digit > 0 : digit = digit
        else : digit = None

        for product in self:
            attr_values = product.product_template_attribute_value_ids.filtered(lambda v: not v.attribute_id.sh_is_custom_attribute) 
            attr_value_map = {
                val.attribute_id.id: val.product_attribute_value_id
                for val in attr_values
            }
 
            skip_attr_ids = set()
 
            for val in attr_values:
                attr = val.attribute_id
                if attr.sh_parent_attribute and attr.sh_parent_value:
                    parent_attr_id = attr.sh_parent_attribute.id
                    parent_val_id = attr.sh_parent_value.id
 
                    selected_val = attr_value_map.get(parent_attr_id)
                    if selected_val and selected_val.id == parent_val_id:
                        skip_attr_ids.add(attr.id)
 
            parts = [
                val.product_attribute_value_id.name[:digit]
                for val in attr_values
                if val.attribute_id.id not in skip_attr_ids
            ]
            default_code = sep.join(parts)
 
            if default_code:
                product.default_code = default_code.upper()

    @api.model
    def create(self, vals):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only the System Administrator can create new Product Variants."))

        # Manual variant/new product flow from the variant form can try to
        # create a fresh product.template underneath. Keep the duplicate-name
        # restriction in that case instead of reusing an existing template.
        if (
            self.env.context.get('create_product_product')
            and not vals.get('product_tmpl_id')
            and not vals.get('product_template_id')
            and vals.get('name')
        ):
            existing_template = self.env['product.template'].with_context(active_test=False).search([
                ('name', '=', vals['name']),
            ], order='id asc', limit=1)
            if existing_template:
                raise UserError(_(
                    "A product with the name '%s' already exists. Please use a different product name."
                ) % vals['name'])

        # If user selected an existing template through the custom field,
        # bind variant to that template before super() to avoid creating
        # a new template and triggering duplicate product-name validation.
        if vals.get('product_template_id') and not vals.get('product_tmpl_id'):
            vals['product_tmpl_id'] = vals['product_template_id']

        if vals.get('product_template_id'):
            vals['sh_is_created_manually'] = True
        # Keep explicit temporary flag coming from UI flows.
        # Do not force it to True when caller sent sh_is_record_saved=False.
        if vals.get('name') and 'sh_is_record_saved' not in vals:
            vals['sh_is_record_saved'] = True

        # if vals.get('name'):
        #     match_found =  self.env['product.product'].sudo().search([('name','=',vals.get('name'))])
        #     if match_found:
        #         raise UserError(_('Variant already exist with same name. Please enter different name to link with product'))

        products = super(ProductProduct,self).create(vals)
        if self.env.company.sh_product_int_ref_gen:
            sep = self.env.company.sh_pdt_new_seq_sep
            if sep : sep = sep
            else : sep = ''

            digit = self.env.company.sh_pdt_attr_digit
            if digit > 0 : digit = digit
            else : digit = None

            for product in products:
                attr_values = product.product_template_attribute_value_ids.filtered(lambda v: not v.attribute_id.sh_is_custom_attribute)

                # Map: attribute_id => value_id
                attr_value_map = {
                    val.attribute_id.id: val.product_attribute_value_id
                    for val in attr_values
                }

                skip_attr_ids = set()  # Attribute IDs to skip from final string

                # Phase 1: identify child attributes to skip
                for val in attr_values:
                    attr = val.attribute_id
                    if attr.sh_parent_attribute and attr.sh_parent_value:
                        parent_attr_id = attr.sh_parent_attribute.id
                        parent_val_id = attr.sh_parent_value.id

                        selected_val = attr_value_map.get(parent_attr_id)
                        if selected_val and selected_val.id == parent_val_id:
                            skip_attr_ids.add(attr.id)

                # Phase 2: build default_code from non-skipped values
                parts = [
                    val.product_attribute_value_id.name[:digit]
                    for val in attr_values
                    if val.attribute_id.id not in skip_attr_ids
                ]
                default_code = sep.join(parts)

                if default_code:
                    product.default_code = default_code.upper()
        return products

    def write(self, vals):
        # Before saving variant values, remove temporary duplicate variants
        # one-by-one so DB unique constraint does not crash the transaction.
        if (
            'product_template_attribute_value_ids' in vals
            and not self.env.context.get('sh_skip_product_template_sync')
        ):
            ptav_commands = vals.get('product_template_attribute_value_ids') or []
            for record in self:
                new_ptav_ids = set(record.product_template_attribute_value_ids.ids)
                for command in ptav_commands:
                    if command[0] == 6:
                        new_ptav_ids = set(command[2] or [])
                    elif command[0] == 4:
                        new_ptav_ids.add(command[1])
                    elif command[0] == 3:
                        new_ptav_ids.discard(command[1])
                    elif command[0] == 5:
                        new_ptav_ids = set()

                if not new_ptav_ids or not record.product_tmpl_id:
                    continue

                combination_indices = self.env['product.template.attribute.value'].browse(
                    list(new_ptav_ids)
                )._ids2str()

                duplicates = self.with_context(active_test=False).search([
                    ('id', '!=', record.id),
                    ('product_tmpl_id', '=', record.product_tmpl_id.id),
                    ('active', '=', True),
                    ('combination_indices', '=', combination_indices),
                ], order='id')

                # Delete only temporary variants one by one.
                for duplicate in duplicates:
                    if not duplicate.sh_is_record_saved:
                        duplicate.with_context(sh_skip_product_template_sync=True).unlink()

                remaining = self.with_context(active_test=False).search([
                    ('id', '!=', record.id),
                    ('product_tmpl_id', '=', record.product_tmpl_id.id),
                    ('active', '=', True),
                    ('combination_indices', '=', combination_indices),
                ], limit=1)
                if remaining:
                    raise UserError(_(
                        "A variant with the same combination already exists for '%s'."
                    ) % record.product_tmpl_id.display_name)

        if vals.get('product_template_id') and vals.get('product_template_id') != False:
            vals['sh_is_created_manually'] = True

        temp_product_template_id = False
        sync_product_template = not self.env.context.get('sh_skip_product_template_sync')
        if sync_product_template and 'product_template_id' in vals and vals['product_template_id'] != False:
            temp_product_template_id = self.product_tmpl_id.id
            vals['product_tmpl_id'] = vals['product_template_id']
            target_duplicates = self.with_context(active_test=False).search([
                ('id', 'not in', self.ids),
                ('product_tmpl_id', '=', vals['product_tmpl_id']),
                ('active', '=', True),
                ('combination_indices', 'in', self.mapped('combination_indices')),
            ])
            if target_duplicates:
                for product in self:
                    # This record is a side-effect temporary standalone variant.
                    # Remove it before raising a clean warning so the user won't
                    # keep seeing duplicate product/product-variant leftovers.
                    if product.product_tmpl_id.id != vals['product_tmpl_id'] and not product.sh_is_created_manually:
                        product.sudo().unlink()
                self.env.cr.commit()
                raise UserError(_(
                    "A variant with the same combination already exists for product '%s'. "
                    "Please choose another variant combination."
                ) % self.env['product.template'].browse(vals['product_tmpl_id']).display_name)
        res = super().write(vals)
        for product in self:
            if sync_product_template and product.product_template_id:
                self.env['product.template'].sudo().browse(temp_product_template_id).active = False

        # Only run logic if 'product_template_attribute_value_ids' is in vals or forced
        if 'product_template_attribute_value_ids' in vals or 'force_update_default_code' in vals:
            for product in self:
                if self.env.company.sh_product_int_ref_gen:
                    sep = self.env.company.sh_pdt_new_seq_sep or ''
                    digit = self.env.company.sh_pdt_attr_digit or None

                    attr_values = product.product_template_attribute_value_ids.filtered(lambda v: not v.attribute_id.sh_is_custom_attribute)
                    # Map: attribute_id => value_id
                    attr_value_map = {
                        val.attribute_id.id: val.product_attribute_value_id
                        for val in attr_values
                    }

                    skip_attr_ids = set()

                    # Phase 1: find child attributes to skip
                    for val in attr_values:
                        attr = val.attribute_id
                        if attr.sh_parent_attribute and attr.sh_parent_value:
                            parent_attr_id = attr.sh_parent_attribute.id
                            parent_val_id = attr.sh_parent_value.id

                            selected_val = attr_value_map.get(parent_attr_id)
                            if selected_val and selected_val.id == parent_val_id:
                                skip_attr_ids.add(attr.id)

                    # Phase 2: build default_code
                    parts = [
                        val.product_attribute_value_id.name[:digit]
                        for val in attr_values
                        if val.attribute_id.id not in skip_attr_ids
                    ]
                    default_code = sep.join(parts)

                    if default_code:
                        product.default_code = default_code.upper()

        return res

    @api.depends('product_variant_id')
    def _compute_custom_attribute_values(self):
        for line in self:
            if not line.product_variant_id:
                line.product_custom_attribute_value_ids = False
                continue
            if not line.product_custom_attribute_value_ids:
                continue
            valid_values = line.product_variant_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the is_custom values that don't belong to this template
            for pacv in line.product_custom_attribute_value_ids:
                if pacv.custom_product_template_attribute_value_id not in valid_values:
                    line.product_custom_attribute_value_ids -= pacv

    @api.depends('product_variant_id')
    def _compute_no_variant_attribute_values(self):
        for line in self:
            if not line.product_variant_id:
                line.product_no_variant_attribute_value_ids = False
                continue
            if not line.product_no_variant_attribute_value_ids:
                continue
            valid_values = line.product_variant_id.product_tmpl_id.valid_product_template_attribute_line_ids.product_template_value_ids
            # remove the no_variant attributes that don't belong to this template
            for ptav in line.product_no_variant_attribute_value_ids:
                if ptav._origin not in valid_values:
                    line.product_no_variant_attribute_value_ids -= ptav


class ProductAttributeCustomValue(models.Model):
    _inherit = "product.attribute.custom.value"

    sh_product_id = fields.Many2one('product.product', string="Sales Order Line", ondelete='cascade')
