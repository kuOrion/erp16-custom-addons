# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError


class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    # def copy(self, default=None):
    #     """Override copy method to show confirmation before duplicating BOM"""
    #     self.ensure_one()
    #
    #     # Check if this is being called from the UI duplicate action
    #     # If called programmatically, it will proceed without confirmation
    #     if self.env.context.get('confirm_duplicate'):
    #         return super(MrpBom, self).copy(default=default)
    #
    #     # Raise a user error that will show as a dialog
    #     # This won't actually duplicate - it's just for the message
    #     raise UserError(_(
    #         'Please use the "Duplicate with Confirmation" action from the Action menu '
    #         'to duplicate this BOM for product: %s'
    #     ) % self.product_tmpl_id.display_name)

    def copy(self, default=None):
        self.ensure_one()

        # If already confirmed → allow duplication
        if self.env.context.get('bom_duplicate_confirmed'):
            return super().copy(default=default)

        # Open wizard instead of duplicating
        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirm BOM Duplication'),
            'res_model': 'mrp.bom.duplicate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_bom_id': self.id,
                'default_product_name': self.product_tmpl_id.display_name,
            }
        }

    def action_duplicate_bom(self):
        """Action to duplicate BOM with confirmation"""
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': _('Confirm BOM Duplication'),
            'res_model': 'mrp.bom.duplicate.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_bom_id': self.id,
                'default_product_name': self.product_tmpl_id.display_name,
            }
        }