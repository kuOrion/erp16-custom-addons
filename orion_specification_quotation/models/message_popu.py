# from odoo import models, fields, api, _
# from odoo.exceptions import UserError
#
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     model_enhancements = fields.Text(
#         string="N Specification",
#         related="product_id.model_enhancements",
#         store=False,
#         readonly=True
#     )
#
#     @api.onchange('product_id')
#     def _onchange_product_id_show_enhancement(self):
#         if self.product_id and self.product_id.model_enhancements:
#             return {
#                 'type': 'ir.actions.act_window',
#                 'name': _('Model Enhancements'),
#                 'res_model': 'model.enhancement.confirm.wizard',
#                 'view_mode': 'form',
#                 'target': 'new',
#                 'context': {
#                     'default_message': self.product_id.model_enhancements,
#                     'default_order_line_id': self.id,
#                 }
#             }
#
#
# class ModelEnhancementConfirmWizard(models.TransientModel):
#     _name = "model.enhancement.confirm.wizard"
#     _description = "Confirm Model Enhancement"
#
#     message = fields.Text(string="Model Enhancement", readonly=True)
#     order_line_id = fields.Many2one("sale.order.line")
#
#     def action_confirm(self):
#         # Just close the popup and accept the product
#         return {'type': 'ir.actions.act_window_close'}
#
#     def action_cancel(self):
#         # Reset product_id if user cancels
#         if self.order_line_id:
#             self.order_line_id.product_id = False
#         return {'type': 'ir.actions.act_window_close'}
#


from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    n_specification = fields.Text(
        string="N Specification",
        compute="_compute_n_specification",
        store=False,
        readonly=True
    )

    @api.depends('product_id')
    def _compute_n_specification(self):
        for line in self:
            if line.product_id:
                # Search for the N Specification in sh.product.variant.extra.line
                extra_line = self.env['sh.product.variant.extra.line'].search([
                    ('sh_product_id', '=', line.product_id.id),
                    ('sh_name', '=', 'N Specification')
                ], limit=1)
                line.n_specification = extra_line.sh_value if extra_line else False
            else:
                line.n_specification = False

    @api.onchange('product_id')
    def _onchange_product_id_show_enhancement(self):
        if self.product_id:
            # Search for the N Specification
            extra_line = self.env['sh.product.variant.extra.line'].search([
                ('sh_product_id', '=', self.product_id.id),
                ('sh_name', '=', 'N Specification')
            ], limit=1)

            if extra_line and extra_line.sh_value:
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('N Specification'),
                    'res_model': 'model.enhancement.confirm.wizard',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_message': extra_line.sh_value,
                        'default_order_line_id': self.id,
                    }
                }


class ModelEnhancementConfirmWizard(models.TransientModel):
    _name = "model.enhancement.confirm.wizard"
    _description = "Confirm N Specification"

    message = fields.Text(string="N Specification", readonly=True)
    order_line_id = fields.Many2one("sale.order.line")

    def action_confirm(self):
        # Just close the popup and accept the product
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        # Reset product_id if user cancels
        if self.order_line_id:
            self.order_line_id.product_id = False
        return {'type': 'ir.actions.act_window_close'}