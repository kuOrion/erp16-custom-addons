from odoo import models, api, _
from odoo.exceptions import ValidationError


class MrpBomLine(models.Model):
    _inherit = "mrp.bom.line"

    @api.onchange('product_id')
    def _onchange_product_id_check_duplicate_for_same_product(self):
        if not self.product_id or not self.bom_id or not self.bom_id.product_tmpl_id:
            return

        # Finished product of this BOM
        finished_product = self.bom_id.product_tmpl_id

        # Search for the same component in BOMs of the SAME finished product
        domain = [
            ('product_id', '=', self.product_id.id),
            ('bom_id.product_tmpl_id', '=', finished_product.id),
        ]

        # Exclude current line (and current BOM if already saved)
        if self.id:
            domain.append(('id', '!=', self.id))
        if self.bom_id.id:
            domain.append(('bom_id', '!=', self.bom_id.id))

        existing_line = self.env['mrp.bom.line'].search(domain, limit=1)

        if existing_line:
            product_name = self.product_id.display_name
            self.product_id = False
            return {
                'warning': {
                    'title': _('Duplicate Component'),
                    'message': _(
                        "The product '%s' is already used in a BOM of this finished product. "
                        "You can't add it again."
                    ) % product_name,
                }
            }

    # def action_duplicate_bom(self):
    #     """Action to duplicate BOM with confirmation"""
    #     self.ensure_one()
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Confirm BOM Duplication'),
    #         'res_model': 'mrp.bom.duplicate.wizard',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': {
    #             'default_bom_id': self.id,
    #             'default_product_name': self.product_tmpl_id.display_name,
    #         }
    #     }
