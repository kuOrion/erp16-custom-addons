# from odoo import models, fields, api, _
# from odoo.exceptions import UserError
#
#
# class StockQuantTransfer(models.Model):
#     _inherit = 'stock.quant'
#
#     @api.model
#     def action_pdi_to_fg_transfer(self):
#         """
#         Action method to open PDI to FG transfer wizard for selected quants
#         """
#         # Get the current active IDs (selected quants)
#         active_ids = self.env.context.get('active_ids', [])
#
#         # Ensure quants are selected
#         if not active_ids:
#             raise UserError(_('Please select at least one product to transfer.'))
#
#         # Create context with active IDs to pass to the transfer wizard
#         ctx = dict(self.env.context, active_ids=active_ids)
#
#         # Return action to open PDI to FG transfer wizard
#         return {
#             'name': 'PDI to FG Transfer',
#             'type': 'ir.actions.act_window',
#             'res_model': 'pdi.to.fg',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': ctx
#         }

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class StockQuantTransfer(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def action_pdi_to_fg_transfer(self):
        """
        Action method to open PDI to FG transfer wizard for selected quants
        """
        # Get the current active IDs (selected quants)
        active_ids = self.env.context.get('active_ids', [])

        # Ensure quants are selected
        if not active_ids:
            raise UserError(_('Please select at least one product to transfer.'))

        # Create context with active IDs to pass to the transfer wizard
        ctx = dict(self.env.context, active_ids=active_ids)

        # Return action to open PDI to FG transfer wizard
        return {
            'name': 'PDI to FG Transfer',
            'type': 'ir.actions.act_window',
            'res_model': 'pdi.to.fg.transfer',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx
        }

    # @api.model
    # def action_fg_to_stock_transfer(self):
    #     """
    #     Action method to open FG to Stock transfer wizard for selected quants
    #     """
    #     # Get the current active IDs (selected quants)
    #     active_ids = self.env.context.get('active_ids', [])
    #
    #     # Ensure quants are selected
    #     if not active_ids:
    #         raise UserError(_('Please select at least one product to transfer.'))
    #
    #     # Create context with active IDs to pass to the transfer wizard
    #     ctx = dict(self.env.context, active_ids=active_ids)
    #
    #     # Return action to open FG to Stock transfer wizard
    #     return {
    #         'name': 'FG to Stock Transfer',
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'fg.to.stock',
    #         'view_mode': 'form',
    #         'target': 'new',
    #         'context': ctx
    #     }
    def action_fg_to_stock_transfer(self):
        """
        Action method to open FG to Stock transfer wizard for selected quants
        """
        # Get the current active IDs (selected quants)
        active_ids = self.env.context.get('active_ids', [])

        # Ensure quants are selected
        if not active_ids:
            raise UserError(_('Please select at least one product to transfer.'))

        # Create context with active IDs to pass to the transfer wizard
        ctx = dict(self.env.context, active_ids=active_ids)

        # Return action to open FG to Stock transfer wizard
        return {
            'name': 'FG to Stock Transfer',
            'type': 'ir.actions.act_window',
            'res_model': 'fg.to.stock.transfer',
            'view_mode': 'form',
            'target': 'new',
            'context': ctx
        }
