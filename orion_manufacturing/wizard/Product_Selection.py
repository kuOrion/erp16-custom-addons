from odoo import models, fields, api
from odoo.exceptions import UserError


class OrionSelectProductWizard(models.TransientModel):
    _name = 'orion.select.product.wizard'
    _description = 'Select product from order'

    production_id = fields.Many2one('mrp.production', string="Manufacturing Order")
    available_product_ids = fields.Many2many('product.product', string="Available Products")
    product_id = fields.Many2one('product.product', string="Product", required=True,
                                 domain="[('id', 'in', available_product_ids)]")

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id or not self.production_id or not self.production_id.order_id:
            return

        order_id = self.production_id.order_id
        order_line = order_id.order_line.filtered(
            lambda l: l.product_id.id == self.product_id.id
        )

        if not order_line:
            return {
                'warning': {
                    'title': 'Product Not Found',
                    'message': 'Selected product not found in the sale order lines.'
                }
            }

    def action_confirm(self):
        """Update MO with selected product"""
        self.ensure_one()

        if not self.product_id or not self.production_id:
            raise UserError("Please select a product.")

        # Update the MO with the selected product
        mo = self.production_id
        mo.with_context(skip_onchange=True).write({
            'product_oa_id': self.product_id.id,
            'product_id': self.product_id.id
        })

        # Trigger onchange manually
        mo.onchange_product_oa_id()

        return {'type': 'ir.actions.act_window_close'}