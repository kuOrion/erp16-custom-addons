from odoo import models, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_create_new_mo(self):
        """Custom button to create new MO"""
        # Example: open a new empty manufacturing order
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Manufacturing Order',
            'res_model': 'mrp.production',
            'view_mode': 'form',
            'target': 'current',
            'context': {'default_product_qty': 1.0},
        }
