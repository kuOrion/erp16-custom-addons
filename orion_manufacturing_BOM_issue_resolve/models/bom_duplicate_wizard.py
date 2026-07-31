# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class MrpBomDuplicateWizard(models.TransientModel):
    _name = 'mrp.bom.duplicate.wizard'
    _description = 'BOM Duplicate Confirmation Wizard'

    bom_id = fields.Many2one('mrp.bom', string='BOM to Duplicate', required=True)
    product_name = fields.Char(string='Product', readonly=True)
    message = fields.Html(string='Message', compute='_compute_message')

    @api.depends('product_name')
    def _compute_message(self):
        for wizard in self:
            wizard.message = _(
                '<p>Do you want to create a duplicate BOM for this product?</p>'
                '<p><strong>Product:</strong> %s</p>'
            ) % (wizard.product_name or '')

    # def action_confirm_duplicate(self):
    #     """Confirm and create duplicate BOM"""
    #     self.ensure_one()
    #
    #     # Create duplicate with context to bypass the confirmation check
    #     new_bom = self.bom_id.with_context(confirm_duplicate=True).copy()
    #
    #     # Show the newly created BOM
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Bill of Materials'),
    #         'res_model': 'mrp.bom',
    #         'res_id': new_bom.id,
    #         'view_mode': 'form',
    #         'target': 'current',
    #     }
    def action_confirm_duplicate(self):
        self.ensure_one()

        new_bom = self.bom_id.with_context(
            bom_duplicate_confirmed=True
        ).copy()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.bom',
            'res_id': new_bom.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        """Cancel the duplication"""
        return {'type': 'ir.actions.act_window_close'}