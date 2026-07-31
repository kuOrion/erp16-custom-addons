from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    grn_prefix = fields.Char(
        string="GRN Prefix",
        config_parameter='purchase_grn_numbering.grn_prefix',
        default='GRN',
        help="Prefix for GRN numbers"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            grn_prefix=params.get_param(
                'purchase_grn_numbering.grn_prefix', 'GRN'
            ),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param(
            'purchase_grn_numbering.grn_prefix',
            self.grn_prefix or 'GRN'
        )
