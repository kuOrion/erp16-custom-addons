from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sample_invoice_prefix = fields.Char(
        string="Sample Invoice Prefix",
        config_parameter='orion_sample_invoice_report.sample_invoice_prefix',
        default='SI/',
        help="Prefix for sample invoice numbers"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            sample_invoice_prefix=params.get_param(
                'orion_sample_invoice_report.sample_invoice_prefix', 'SI/'
            ),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param(
            'orion_sample_invoice_report.sample_invoice_prefix',
            self.sample_invoice_prefix or 'SI/'
        )
