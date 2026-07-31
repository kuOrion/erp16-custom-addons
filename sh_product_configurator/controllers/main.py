from odoo import http
from odoo.http import request
import json

class ProductConfiguratorController(http.Controller):
    @http.route(['/unlink/product_variant'], type='json', auth="user", methods=['POST'])
    def unlink_product_variant(self, **kw):
        if kw.get('product_data'):
            product_variant_to_unlink = request.env['product.product'].sudo().browse(kw.get('product_data'))
            if product_variant_to_unlink.exists():
                # Always allow cleanup for temporary/unsaved variants created by
                # configurator side effects, even if marked manual.
                if (not product_variant_to_unlink.sh_is_created_manually) or (not product_variant_to_unlink.sh_is_record_saved):
                    return product_variant_to_unlink.unlink()
        return True

    @http.route(['/update_product_variant'], type='json', auth="user", methods=['POST'])
    def update_product_variant(self, sh_product_id, product_template_id, product_template_attribute_value_ids, **kwargs):
        product = request.env['product.product'].sudo().browse(sh_product_id)
        attribute_value_ids = json.loads(product_template_attribute_value_ids)
        
        # Use (6, 0, [ids]) to replace all existing attributes with the new list.
        # This is an atomic operation and will prevent partial updates.
        product.sudo().write({'product_template_attribute_value_ids': [(6, 0, attribute_value_ids)]})
        
        return True
