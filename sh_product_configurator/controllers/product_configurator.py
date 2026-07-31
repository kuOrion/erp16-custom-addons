# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
import logging
from odoo import http
from odoo.http import request

from odoo.addons.sale_product_configurator.controllers.main import ProductConfiguratorController
from odoo.addons.website_sale.controllers import main


class WebsiteSaleProductConfiguratorController(ProductConfiguratorController):

    @http.route(['/sale_product_configurator/configure'], type='json', auth="user", methods=['POST'])
    def configure(self, product_template_id, pricelist_id, **kw):
        # Call the original configure method to get the base context
        response_template = super().configure(product_template_id, pricelist_id, **kw)

        # Extract the context from the rendered template (this is a bit hacky)
        # A better way would be if super().configure returned a dict, but it returns HTML.
        # So, we need to re-render with our added context.

        # Re-extract parameters to build the context for re-rendering
        add_qty = float(kw.get('quantity', 1))
        product_template = request.env['product.template'].browse(int(product_template_id))
        pricelist = self._get_pricelist(pricelist_id)

        product_combination = False
        attribute_value_ids = set(kw.get('product_template_attribute_value_ids', []))
        attribute_value_ids |= set(kw.get('product_no_variant_attribute_value_ids', []))
        if attribute_value_ids:
            product_combination = request.env['product.template.attribute.value'].browse(
                attribute_value_ids
            ).filtered(
                lambda ptav: ptav.product_tmpl_id == product_template
            )

        if pricelist:
            product_template = product_template.with_context(pricelist=pricelist.id, partner=request.env.user.partner_id)

        attribute_parent_map = {}
        for attribute_line in product_template.attribute_line_ids:
            attribute = attribute_line.attribute_id
            if hasattr(attribute, 'sh_parent_attribute') and attribute.sh_parent_attribute and \
               hasattr(attribute, 'sh_parent_value') and attribute.sh_parent_value:
                # Find the product.template.attribute.value (PTAV) that corresponds to the sh_parent_value (PAV)
                # for the current product_template.
                parent_ptav = request.env['product.template.attribute.value'].search([
                    ('product_tmpl_id', '=', product_template.id),
                    ('attribute_id', '=', attribute.sh_parent_attribute.id),
                    ('product_attribute_value_id', '=', attribute.sh_parent_value.id),
                ], limit=1)

                if parent_ptav:
                    attribute_parent_map[attribute.id] = {
                        'parent_attribute_id': attribute.sh_parent_attribute.id,
                        'parent_value_id': parent_ptav.id, # Use the PTAV ID here
                    }

        # Re-render the template with the modified context
        return request.env['ir.ui.view']._render_template(
            "sale_product_configurator.configure",
            {
                'product': product_template,
                'pricelist': pricelist,
                'add_qty': add_qty,
                'product_combination': product_combination,
                'attribute_parent_map': json.dumps(attribute_parent_map),
            },
        )

    def _show_advanced_configurator(self, product_id, variant_values, pricelist, handle_stock, **kw):

        product = request.env['product.product'].browse(int(product_id))
        combination = request.env['product.template.attribute.value'].browse(variant_values)
        add_qty = float(kw.get('add_qty', 1))

        no_variant_attribute_values = combination.filtered(
            lambda product_template_attribute_value: product_template_attribute_value.attribute_id.create_variant == 'no_variant'
        )
        if no_variant_attribute_values:
            product = product.with_context(no_variant_attribute_values=no_variant_attribute_values)

        attribute_parent_map = {}
        for attribute_line in product.product_tmpl_id.attribute_line_ids: # Use product_tmpl_id here
            attribute = attribute_line.attribute_id
            if hasattr(attribute, 'sh_parent_attribute') and attribute.sh_parent_attribute and \
               hasattr(attribute, 'sh_parent_value') and attribute.sh_parent_value:
                # Find the product.template.attribute.value (PTAV) that corresponds to the sh_parent_value (PAV)
                # for the current product_template.
                parent_ptav = request.env['product.template.attribute.value'].search([
                    ('product_tmpl_id', '=', product.product_tmpl_id.id),
                    ('attribute_id', '=', attribute.sh_parent_attribute.id),
                    ('product_attribute_value_id', '=', attribute.sh_parent_value.id),
                ], limit=1)

                if parent_ptav:
                    attribute_parent_map[attribute.id] = {
                        'parent_attribute_id': attribute.sh_parent_attribute.id,
                        'parent_value_id': parent_ptav.id, # Use the PTAV ID here
                    }

        return request.env['ir.ui.view']._render_template("sale_product_configurator.optional_products_modal", {
            'product': product,
            'combination': combination,
            'add_qty': add_qty,
            'parent_name': product.name,
            'variant_values': variant_values,
            'pricelist': pricelist,
            'handle_stock': handle_stock,
            'already_configured': kw.get("already_configured", False),
            'mode': kw.get('mode', 'add'),
            'product_custom_attribute_values': kw.get('product_custom_attribute_values', None),
            'no_attribute': kw.get('no_attribute', False),
            'custom_attribute': kw.get('custom_attribute', False),
            'sh_active_model': kw.get('sh_active_model', False),
            'attribute_parent_map': json.dumps(attribute_parent_map),
        })