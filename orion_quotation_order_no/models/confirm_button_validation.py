from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """Override the default confirm action to show validation dialog first"""
        # Check if we're coming from the wizard confirmation
        if self._context.get('skip_validation'):
            # Call the original action_confirm method
            return super(SaleOrder, self).action_confirm()

        # Show validation dialog
        return {
            'name': 'Confirm Quotation To Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.confirm.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('orion_quotation_order_no.view_sale_order_confirm_wizard_form').id,
            'target': 'new',
            'context': {
                'default_sale_order_id': self.id,
                'default_message': 'Once confirmed, this quotation will become a sales order and will not get to see as a quotation. Please verify all information before confirming.'
            }
        }


class SaleOrderConfirmWizard(models.TransientModel):
    _name = 'sale.order.confirm.wizard'
    _description = 'Sale Order Confirmation Wizard'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order', required=True)
    message = fields.Char(string='Message', readonly=True)

    def action_confirm_order(self):
        """Confirm the sale order"""
        if self.sale_order_id:
            # Use context to skip validation and call original confirm
            self.sale_order_id.with_context(skip_validation=True).action_confirm()
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        """Cancel the confirmation"""
        return {'type': 'ir.actions.act_window_close'}