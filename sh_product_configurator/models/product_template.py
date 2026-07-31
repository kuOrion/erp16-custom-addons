
# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies Pvt. Ltd.

from odoo import _, api, fields, models
from odoo.tools import config
from odoo.exceptions import UserError
import itertools

class ProductTemplate(models.Model):
    _inherit = "product.template"

    sh_is_duplicated_template = fields.Boolean(
        string="Duplicated Template",
        copy=False,
        help="Technical field used to validate renamed duplicated products.",
    )

    def _should_skip_duplicate_name_validation(self, template_name):
        template_name = (template_name or '').strip()
        return bool(template_name) and template_name.upper().startswith(('N', 'R'))

    @api.model_create_multi
    def create(self, vals_list):
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only the System Administrator can create new Products."))
        skip_duplicate_name_check = self.env.context.get('create_product_product')
        for vals in vals_list:
            if (
                not skip_duplicate_name_check
                and vals.get('name')
                and not vals.get('sh_is_duplicated_template')
                and not self._should_skip_duplicate_name_validation(vals['name'])
            ):
                self._validate_unique_product_name(vals['name'])
        return super(ProductTemplate, self).create(vals_list)

    def _validate_unique_product_name(self, template_name, excluded_template_ids=None):
        template_name = (template_name or '').strip()
        if not template_name:
            return

        if self._should_skip_duplicate_name_validation(template_name):
            return

        excluded_template_ids = excluded_template_ids or []

        existing_template = self.with_context(active_test=False).search([
            ('name', '=', template_name),
            ('id', 'not in', excluded_template_ids),
        ], limit=1)
        if existing_template:
            raise UserError(_(
                "A product with the name '%s' already exists. Please use a different product name."
            ) % template_name)

    def write(self, vals):
        if self.env.context.get('sh_skip_duplicate_name_check'):
            return super(ProductTemplate, self).write(vals)

        renamed_templates = self.env['product.template']
        new_name = vals.get('name')
        if new_name:
            for template in self:
                normalized_new_name = (new_name or '').strip()
                if not normalized_new_name:
                    continue

                if normalized_new_name == (template.name or '').strip():
                    continue

                template._validate_unique_product_name(
                    normalized_new_name,
                    excluded_template_ids=template.ids,
                )
                if template.sh_is_duplicated_template:
                    renamed_templates |= template

        res = super(ProductTemplate, self).write(vals)

        if renamed_templates:
            renamed_templates.with_context(sh_skip_duplicate_name_check=True).write({
                'sh_is_duplicated_template': False,
            })

        return res

    def _should_copy_bom_on_duplicate(self):
        self.ensure_one()
        return True

    def _get_variant_match_key(self, product):
        product.ensure_one()
        return product.combination_indices or tuple(sorted(
            ptav.product_attribute_value_id.name
            for ptav in product.product_template_variant_value_ids
        ))

    def _get_matching_duplicate_combination(self, old_product, new_template):
        old_product.ensure_one()
        new_template.ensure_one()

        mapped_ptavs = self.env['product.template.attribute.value']
        new_ptavs = new_template.valid_product_template_attribute_line_ids.product_template_value_ids
        for old_ptav in old_product.product_template_variant_value_ids:
            matching_ptav = new_ptavs.filtered(
                lambda ptav: ptav.attribute_id.name == old_ptav.attribute_id.name
                and ptav.product_attribute_value_id.name == old_ptav.product_attribute_value_id.name
            )[:1]
            if matching_ptav:
                mapped_ptavs |= matching_ptav
        return mapped_ptavs

    def _get_or_create_duplicate_variant(self, old_product, new_template, variant_map):
        old_product.ensure_one()
        new_template.ensure_one()

        old_variant_key = self._get_variant_match_key(old_product)
        new_variant = variant_map.get(old_variant_key)
        if new_variant:
            return new_variant

        duplicate_combination = self._get_matching_duplicate_combination(old_product, new_template)
        if not duplicate_combination:
            return self.env['product.product']

        new_variant = self.env['product.product'].sudo().with_context(
            sh_skip_product_template_sync=True,
        ).create({
            'product_tmpl_id': new_template.id,
            'product_template_attribute_value_ids': [(6, 0, duplicate_combination.ids)],
        })
        self.env.flush_all()
        self.env.invalidate_all()
        new_template = self.with_context(active_test=False).browse(new_template.id)
        new_variant = new_variant.exists()
        if not new_variant:
            new_variant = new_template.product_variant_ids.filtered(
                lambda product: self._get_variant_match_key(product) == old_variant_key
            )[:1]

        if new_variant:
            variant_map[self._get_variant_match_key(new_variant)] = new_variant
        return new_variant

    def _prepare_duplicate_template_for_bom_sync(self, new_template):
        new_template.ensure_one()
        new_template = self.with_context(active_test=False).browse(new_template.id)
        self.env.flush_all()
        self.env.invalidate_all()
        new_template = self.with_context(active_test=False).browse(new_template.id)
        new_template._create_variant_ids()
        self.env.flush_all()
        self.env.invalidate_all()
        new_template = self.with_context(active_test=False).browse(new_template.id)

        # Ensure each duplicated variant is linked to the duplicated template
        # before BoMs are copied, so the copied BoM points to the new product.
        for new_variant in new_template.product_variant_ids:
            if new_variant.product_template_id != new_template:
                new_variant.with_context(sh_skip_product_template_sync=True).write({
                    'product_template_id': new_template.id,
                })

        self.env.flush_all()
        self.env.invalidate_all()

    def _copy_duplicate_boms(self, new_template):
        self.ensure_one()
        Bom = self.env['mrp.bom']
        old_boms = Bom.search([('product_tmpl_id', '=', self.id)])
        if not old_boms:
            return

        # On duplicate we do NOT create variants for the new template. Copy
        # each BOM as a template-level BOM (product_id=False) so components
        # and details are preserved, but variant-specific BOMs lose their
        # variant link. Users can re-link them to a manually created variant
        # later if needed.
        for old_bom in old_boms:
            old_bom.copy({
                'product_tmpl_id': new_template.id,
                'product_id': False,
            })

    def _copy_variant_extra_data(self, new_template):
        self.ensure_one()
        variant_map = {
            self._get_variant_match_key(new_variant): new_variant
            for new_variant in new_template.product_variant_ids
        }

        for old_variant in self.product_variant_ids:
            new_variant = variant_map.get(self._get_variant_match_key(old_variant))
            if not new_variant:
                continue

            # Copy manual specification lines
            if old_variant.sh_extra_spec_line_ids:
                for old_spec_line in old_variant.sh_extra_spec_line_ids:
                    old_spec_line.copy({'sh_product_id': new_variant.id})

            # Preserve the custom template reference without reassigning the
            # duplicated variant to another real product template.
            variant_updates = {}
            if old_variant.product_template_id:
                linked_template = old_variant.product_template_id
                if linked_template == self:
                    linked_template = new_template
                variant_updates['product_template_id'] = linked_template.id

            if variant_updates:
                new_variant.with_context(sh_skip_product_template_sync=True).write(variant_updates)

    def _create_variant_ids(self):
        # Reimplementation of the standard _create_variant_ids that SKIPS the
        # single-value push block. In this module, attributes added via the
        # template form are always dynamic (`create_variant='dynamic'`) and
        # users cannot pick existing attributes. Standard Odoo pushes
        # single-value attribute values onto the pre-existing empty variant,
        # which turns that empty variant into a "configured" one. We don't
        # want that: variants must be created explicitly from the variant
        # form only. Everything else mirrors the standard behavior.
        #
        # Context guard: during duplicate flow we skip variant creation
        # entirely so the new template has zero variants.
        if self.env.context.get('sh_skip_variant_creation'):
            return True
        if not self:
            return

        self.env.flush_all()
        Product = self.env["product.product"]

        variants_to_create = []
        variants_to_activate = Product
        variants_to_unlink = Product

        for tmpl_id in self:
            lines_without_no_variants = tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes()

            all_variants = tmpl_id.with_context(active_test=False).product_variant_ids.sorted(
                lambda p: (p.active, -p.id)
            )

            current_variants_to_create = []
            current_variants_to_activate = Product

            # NOTE: Standard Odoo writes single-value attributes onto every
            # existing variant here. We intentionally skip that step so the
            # pre-existing empty variant stays empty when dynamic attributes
            # are added post-save. See method docstring.

            existing_variants = {
                variant.product_template_attribute_value_ids: variant for variant in all_variants
            }

            if not tmpl_id.has_dynamic_attributes():
                all_combinations = itertools.product(*[
                    ptal.product_template_value_ids._only_active() for ptal in lines_without_no_variants
                ])
                for combination_tuple in all_combinations:
                    combination = self.env['product.template.attribute.value'].concat(*combination_tuple)
                    is_combination_possible = tmpl_id._is_combination_possible_by_config(
                        combination, ignore_no_variant=True
                    )
                    if not is_combination_possible:
                        continue
                    if combination in existing_variants:
                        current_variants_to_activate += existing_variants[combination]
                    else:
                        current_variants_to_create.append(tmpl_id._prepare_variant_values(combination))
                        if len(current_variants_to_create) > 1000:
                            raise UserError(_(
                                'The number of variants to generate is too high. '
                                'You should either not generate variants for each combination or generate them on demand from the sales order. '
                                'To do so, open the form view of attributes and change the mode of *Create Variants*.'
                            ))
                variants_to_create += current_variants_to_create
                variants_to_activate += current_variants_to_activate
            else:
                for variant in existing_variants.values():
                    is_combination_possible = tmpl_id._is_combination_possible_by_config(
                        combination=variant.product_template_attribute_value_ids,
                        ignore_no_variant=True,
                    )
                    if is_combination_possible:
                        current_variants_to_activate += variant
                variants_to_activate += current_variants_to_activate

            variants_to_unlink += all_variants - current_variants_to_activate

        if variants_to_activate:
            variants_to_activate.write({'active': True})
        if variants_to_create:
            Product.create(variants_to_create)
        if variants_to_unlink:
            variants_to_unlink._unlink_or_archive()
            if self.exists() != self:
                raise UserError(_(
                    "This configuration of product attributes, values, and exclusions would lead to no possible variant. Please archive or delete your product directly if intended."
                ))

        self.env.flush_all()
        self.env.invalidate_all()
        return True

    # def _create_variant_ids(self):
    #     obj = self.with_context(creating_variants=True)
    #     return super(ProductTemplate, obj)._create_variant_ids()

    # def _create_variant_ids(self):
    #     if not self:
    #         return
    #
    #     self.env.flush_all()
    #     Product = self.env["product.product"]
    #
    #     variants_to_create = []
    #     variants_to_activate = Product
    #     variants_to_unlink = Product
    #
    #     for tmpl_id in self:
    #         lines_without_no_variants = tmpl_id.valid_product_template_attribute_line_ids._without_no_variant_attributes()
    #
    #         all_variants = tmpl_id.with_context(active_test=False).product_variant_ids.sorted(lambda p: (p.active, -p.id))
    #
    #         current_variants_to_create = []
    #         current_variants_to_activate = Product
    #
    #         # adding an attribute with only one value should not recreate product
    #         # write this attribute on every product to make sure we don't lose them
    #         single_value_lines = lines_without_no_variants.filtered(lambda ptal: len(ptal.product_template_value_ids._only_active()) == 1)
    #         if single_value_lines:
    #             for variant in all_variants:
    #                 combination = variant.product_template_attribute_value_ids | single_value_lines.product_template_value_ids._only_active()
    #                 # Do not add single value if the resulting combination would
    #                 # be invalid anyway.
    #                 if (
    #                     len(combination) == len(lines_without_no_variants) and
    #                     combination.attribute_line_id == lines_without_no_variants
    #                 ):
    #                     variant.product_template_attribute_value_ids = combination
    #
    #         # Set containing existing `product.template.attribute.value` combination
    #         existing_variants = {
    #             variant.product_template_attribute_value_ids: variant for variant in all_variants
    #         }
    #
    #         # Determine which product variants need to be created based on the attribute
    #         # configuration. If any attribute is set to generate variants dynamically, skip the
    #         # process.
    #         # Technical note: if there is no attribute, a variant is still created because
    #         # 'not any([])' and 'set([]) not in set([])' are True.
    #         if not tmpl_id.has_dynamic_attributes():
    #             # Iterator containing all possible `product.template.attribute.value` combination
    #             # The iterator is used to avoid MemoryError in case of a huge number of combination.
    #             all_combinations = itertools.product(*[
    #                 ptal.product_template_value_ids._only_active() for ptal in lines_without_no_variants
    #             ])
    #             # For each possible variant, create if it doesn't exist yet.
    #             for combination_tuple in all_combinations:
    #                 combination = self.env['product.template.attribute.value'].concat(*combination_tuple)
    #                 is_combination_possible = tmpl_id._is_combination_possible_by_config(combination, ignore_no_variant=True)
    #                 if not is_combination_possible:
    #                     continue
    #                 if combination in existing_variants:
    #                     current_variants_to_activate += existing_variants[combination]
    #                 else:
    #                     current_variants_to_create.append(tmpl_id._prepare_variant_values(combination))
    #                     if len(current_variants_to_create) > 1000:
    #                         raise UserError(_(
    #                             'The number of variants to generate is too high. '
    #                             'You should either not generate variants for each combination or generate them on demand from the sales order. '
    #                             'To do so, open the form view of attributes and change the mode of *Create Variants*.'))
    #             variants_to_create += current_variants_to_create
    #             variants_to_activate += current_variants_to_activate
    #
    #         else:
    #             for variant in existing_variants.values():
    #                 is_combination_possible = tmpl_id._is_combination_possible_by_config(
    #                     combination=variant.product_template_attribute_value_ids,
    #                     ignore_no_variant=True,
    #                 )
    #                 if is_combination_possible:
    #                     current_variants_to_activate += variant
    #             variants_to_activate += current_variants_to_activate
    #
    #         variants_to_unlink += all_variants - current_variants_to_activate
    #
    #     if variants_to_activate:
    #         pass
    #         # variants_to_activate.write({'active': True})
    #     if variants_to_create:
    #         Product.create(variants_to_create)
    #     if variants_to_unlink:
    #         variants_to_unlink._unlink_or_archive()
    #         # prevent change if exclusion deleted template by deleting last variant
    #         if self.exists() != self:
    #             raise UserError(_("This configuration of product attributes, values, and exclusions would lead to no possible variant. Please archive or delete your product directly if intended."))
    #
    #     # prefetched o2m have to be reloaded (because of active_test)
    #     # (eg. product.template: product_variant_ids)
    #     # We can't rely on existing invalidate because of the savepoint
    #     # in _unlink_or_archive.
    #     self.env.flush_all()
    #     self.env.invalidate_all()
    #     return True
    #
    # # def _is_combination_possible(self, combination, parent_combination=None, ignore_no_variant=False):
    # #     is_possible = super(ProductTemplate, self)._is_combination_possible(combination, parent_combination, ignore_no_variant)
    # #     if not is_possible:
    # #         return False
    # #
    # #     # Check for parent-child consistency
    # #     for ptav in combination:
    # #         # ptav.attribute_line_id is the specific line for this template
    # #         parent_value = ptav.attribute_line_id.parent_attribute_value_id
    # #         if parent_value and parent_value not in combination:
    # #             # This value belongs to a child attribute, but its parent value is not in the combination.
    # #             # Therefore, this combination is not possible.
    # #             return False
    # #
    # #     return True
    # #

    def copy(self, default=None):
        if default is None:
            default = {}
        # Create the new template without attributes first
        new_default = dict(default)
        if self._should_skip_duplicate_name_validation(self.name):
            new_default.setdefault('name', self.name)

        new_default['attribute_line_ids'] = []
        if self._should_skip_duplicate_name_validation(new_default.get('name') or self.name):
            new_default['sh_is_duplicated_template'] = True
        # Duplicate must not auto-create any variants: attributes are dynamic
        # in this module, so variants are created manually by the user.
        self = self.with_context(sh_skip_variant_creation=True)
        new_tmpl = super(ProductTemplate, self).copy(new_default)

        # Mapping for hierarchy restoration
        ptav_map = {}  # original_ptav -> new_ptav
        line_map = {}  # original_line -> new_line

        # 1. Create new attributes and lines
        for old_line in self.attribute_line_ids.sorted('sequence'):
            # Create NEW shared attribute (this also copies its values)
            new_attr = old_line.attribute_id.copy({
                'sh_product_tmpl_id': new_tmpl.id,
            })
            
            # Map old values to new values by name (since IDs changed)
            new_value_ids = []
            for old_val in old_line.value_ids:
                matching_new_val = new_attr.value_ids.filtered(lambda v: v.name == old_val.name)
                if matching_new_val:
                    new_value_ids.append(matching_new_val[0].id)

            # Create NEW template attribute line (skip re-sequence for now, but KEEP original sequence)
            new_line = self.env['product.template.attribute.line'].with_context(
                sh_skip_resequence=True, 
                sh_keep_sequence=True
            ).create({
                'product_tmpl_id': new_tmpl.id,
                'attribute_id': new_attr.id,
                'value_ids': [(6, 0, new_value_ids)],
                'sequence': old_line.sequence,
            })
            line_map[old_line] = new_line


            # Map PTAVs by their base product_attribute_value_id
            for new_ptav in new_line.product_template_value_ids:
                old_ptav = old_line.product_template_value_ids.filtered(
                    lambda p: p.product_attribute_value_id.name == new_ptav.product_attribute_value_id.name
                )
                if old_ptav:
                    ptav_map[old_ptav[0]] = new_ptav


        # 2. Restore parent-child hierarchy
        for old_line, new_line in line_map.items():
            if old_line.parent_attribute_value_id:
                new_parent_ptav = ptav_map.get(old_line.parent_attribute_value_id)
                if new_parent_ptav:
                    new_line.with_context(sh_skip_resequence=True).parent_attribute_value_id = new_parent_ptav
                    
                    # Update metadata on the attribute itself
                    new_line.attribute_id.write({
                        'sh_parent_attribute': new_parent_ptav.attribute_id.id,
                        'sh_parent_value': new_parent_ptav.product_attribute_value_id.id,
                    })

        # 3. Final hierarchical re-sequence is no longer called globally
        # to ensure that manual sequence adjustments from the original product are preserved.
        # NOTE: On duplicate we intentionally do NOT create variants for the
        # new template. Attributes are dynamic, so variants must be created
        # manually by the user from the variant form. This keeps the
        # duplicated template clean (zero variants) and lets _copy_duplicate_boms
        # copy BOMs at the template level only.
        if self._should_copy_bom_on_duplicate():
            self._copy_duplicate_boms(new_tmpl)

        # 4. Copy variant extra data (specifications, custom template links, etc.)
        # With zero variants on the new template, variant_map inside this
        # helper is empty and the method becomes a no-op, which is desired.
        self._copy_variant_extra_data(new_tmpl)

        return new_tmpl
