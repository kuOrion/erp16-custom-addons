# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError,UserError


class ProductTemplateAttributeLine(models.Model):
    _inherit = "product.template.attribute.line"
    _order = "sequence, id"

    parent_attribute_value_id = fields.Many2one(
        'product.template.attribute.value',
        string="Parent Attribute Value",
        index=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(string='Sequence', default=999)

    # ==========================================
    #   CONSTRAINT: UNIQUE NAME / PRODUCT
    # ==========================================
    @api.constrains('attribute_id', 'product_tmpl_id')
    def _check_duplicate_attribute_name_per_template(self):
        for line in self:
            if not line.attribute_id or not line.product_tmpl_id:
                continue

            # First look for potential duplicates by case-insensitive name
            potential_duplicates = self.search([
                ('product_tmpl_id', '=', line.product_tmpl_id.id),
                ('attribute_id.name', '=ilike', line.attribute_id.name),
                ('id', '!=', line.id),
            ])

            # Then keep only exact case-sensitive matches
            duplicate_lines = potential_duplicates.filtered(
                lambda d_line: d_line.attribute_id.name == line.attribute_id.name
            )

            if duplicate_lines:
                raise ValidationError(_(
                    "An attribute with the name '%s' already exists for this product. \n"
                    "Attribute names must be unique per product."
                ) % line.attribute_id.name)

    # ======================================================
    #   ONCHANGE: CLEANUP NEW ATTRIBUTE IF LINE NOT SAVED
    # ======================================================
    @api.onchange('attribute_id')
    def _onchange_attribute_id_check_duplicate(self):
        for line in self:
            if not line.attribute_id or not line.product_tmpl_id:
                continue

            # Attribute the user just selected / created (may be a brand new product.attribute)
            new_attr = line.attribute_id
            new_attr_name = new_attr.name

            # All attribute lines (including unsaved NewId ones) for this template
            all_lines = line.product_tmpl_id.attribute_line_ids

            # Duplicate if another line (different origin) has the same attribute name
            duplicate_lines = all_lines.filtered(lambda l:
                l.attribute_id.name == new_attr_name
                and l._origin.id != line._origin.id      # compare DB origins, ignore NewId
            )

            if duplicate_lines:
                # 1) REVERT/CLEAR THE FIELD SO THE LINE WON'T BE SAVED WITH THIS ATTRIBUTE
                if line._origin and line._origin.id:
                    # Editing an existing line: revert to original attribute
                    line.attribute_id = line._origin.attribute_id
                else:
                    # Brand new line: just clear the field
                    line.attribute_id = False

                # 2) IF THIS ATTRIBUTE IS NOT USED IN ANY SAVED LINES, DELETE IT
                #
                # search_count() checks only DB records, not NewId ones.
                # So if the user created this attribute via "Create and Edit..."
                # and no saved product.template.attribute.line uses it, we can safely unlink it.
                if new_attr and new_attr.exists():
                    line_count = self.env['product.template.attribute.line'].search_count([
                        ('attribute_id', '=', new_attr.id)
                    ])
                    if line_count == 0:
                        new_attr.unlink()

                # 3) Show warning in the UI
                return {
                    'warning': {
                        'title': _("Duplicate Attribute"),
                        'message': _(
                            "An attribute with the name '%s' already exists for this product. \n"
                            "Attribute names must be unique per product."
                        ) % new_attr_name,
                    }
                }

    def _sh_resequence_hierarchical(self):
        """ Arrange attribute lines in a parent-child hierarchy and update sequences globally. """
        if self.env.context.get('sh_skip_resequence'):
            return

        templates = self.mapped('product_tmpl_id')
        for template in templates:
            all_lines = self.env['product.template.attribute.line'].search([
                ('product_tmpl_id', '=', template.id)
            ])
            roots = all_lines.filtered(lambda l: not l.parent_attribute_value_id).sorted(lambda l: (l.sequence, l.id))
            ordered_ids = []
            visited = set()

            def walk(line):
                if line.id in visited:
                    return
                visited.add(line.id)
                ordered_ids.append(line.id)
                children = all_lines.filtered(
                    lambda l: l.parent_attribute_value_id and l.parent_attribute_value_id.attribute_line_id == line
                ).sorted(lambda l: (l.sequence, l.id))
                for child in children:
                    walk(child)

            for root in roots:
                walk(root)

            for i, line_id in enumerate(ordered_ids):
                line = all_lines.filtered(lambda l: l.id == line_id)
                new_seq = (i + 1) * 10
                if line.sequence != new_seq:
                    line.with_context(sh_skip_resequence=True).write({'sequence': new_seq})

    def _get_all_descendant_ids(self, line, all_template_lines):
        """ Recursively find all descendant attribute lines for a given line. """
        children = all_template_lines.filtered(
            lambda l: l.parent_attribute_value_id and l.parent_attribute_value_id.attribute_line_id == line
        )
        res = set(children.ids)
        for child in children:
            res |= self._get_all_descendant_ids(child, all_template_lines)
        return res

    def _sh_insert_hierarchically(self):
        """ Insert records into the correct sequence position based on parentage with minimal movement. """
        if self.env.context.get('sh_skip_resequence'):
            return

        # Process one by one to handle shifting correctly
        for line in self:
            if not line.parent_attribute_value_id:
                continue
            
            parent_line = line.parent_attribute_value_id.attribute_line_id
            if not parent_line:
                continue

            # Refresh all lines for this template to get latest sequences
            all_lines = self.env['product.template.attribute.line'].search([
                ('product_tmpl_id', '=', line.product_tmpl_id.id)
            ])

            # Find all current descendants of the parent (excluding the record itself)
            descendant_ids = self._get_all_descendant_ids(parent_line, all_lines)
            branch_ids = descendant_ids | {parent_line.id}
            if line.id in branch_ids:
                branch_ids.remove(line.id)
            
            branch_lines = all_lines.filtered(lambda l: l.id in branch_ids)
            
            # Target sequence is right after the last descendant in the branch
            if branch_lines:
                new_seq = max(branch_lines.mapped('sequence')) + 1
            else:
                new_seq = parent_line.sequence + 1

            # Shift records that would be displaced
            to_shift = all_lines.filtered(lambda l: l.sequence >= new_seq and l.id != line.id)
            if to_shift:
                # We update sequences. Sorting reverse to avoid collisions if we were using unique index
                for other in to_shift.sorted('sequence', reverse=True):
                    other.with_context(sh_skip_resequence=True).write({'sequence': other.sequence + 1})

            line.with_context(sh_skip_resequence=True).write({'sequence': new_seq})



    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only the System Administrator can create new Product attribute lines."))
        # Link sub-attribute to the main product template
        for vals in vals_list:
            if vals.get('parent_attribute_value_id'):
                parent_ptav = self.env['product.template.attribute.value'].browse(vals['parent_attribute_value_id'])
                if parent_ptav.exists():
                    if not vals.get('product_tmpl_id'):
                        vals['product_tmpl_id'] = parent_ptav.product_tmpl_id.id

            # Ensure new records without explicit sequence go to the bottom (using 999 instead of 10)
            if not self._context.get('sh_keep_sequence') and ('sequence' not in vals or vals.get('sequence') == 10 or vals.get('sequence') == 0):
                vals['sequence'] = 999

                # If a new attribute is being created (attribute_id is a NewId)
                if isinstance(vals.get('attribute_id'), (list, tuple)) and vals['attribute_id'][0] == 0:
                    attribute_vals = vals['attribute_id'][2]
                    # check if parent ptav is in logic
                    if vals.get('parent_attribute_value_id'):
                        parent_ptav = self.env['product.template.attribute.value'].browse(vals['parent_attribute_value_id'])
                        if parent_ptav:
                            attribute_vals['sh_parent_value'] = parent_ptav.product_attribute_value_id.id
                            attribute_vals['sh_parent_attribute'] = parent_ptav.attribute_id.id
                            attribute_vals['sh_is_custom_attribute'] = True
                            attribute_vals['sh_product_tmpl_id'] = parent_ptav.product_tmpl_id.id

        # Original logic from the file
        res = super(ProductTemplateAttributeLine, self).create(vals_list)
        for record in res:
            if record.attribute_id and not record.attribute_id.sh_product_tmpl_id:
                record.attribute_id.sh_product_tmpl_id = record.product_tmpl_id

        # Targeted hierarchical insertion for new records
        # This places the new record after its parent's last child without moving others drastically
        if res and not self.env.context.get('sh_skip_resequence'):
            res._sh_insert_hierarchically()

        return res



    def write(self, vals):
        res = super(ProductTemplateAttributeLine, self).write(vals)
        # We only trigger hierarchical movement if the hierarchy structure itself changes (parent changed).
        # We NO LONGER trigger it when 'sequence' changes (manual handle drag).
        # This allows manual ordering to persist until a structural change or new addition happens.
        if not self.env.context.get('sh_skip_resequence') and 'parent_attribute_value_id' in vals:
            self._sh_insert_hierarchically()
        return res



    def unlink(self):
        res = super(ProductTemplateAttributeLine, self).unlink()
        return res