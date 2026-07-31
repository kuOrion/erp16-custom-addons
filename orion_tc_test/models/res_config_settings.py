# models/res_config_settings.py
from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    test_certificate_prefix = fields.Char(
        string="Test Certificate Prefix",
        config_parameter='orion_tc_test.test_certificate_prefix',
        default='TC/',
        help="Prefix for test certificate numbers"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            test_certificate_prefix=params.get_param(
                'orion_tc_test.test_certificate_prefix', 'TC/'
            ),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        params.set_param(
            'orion_tc_test.test_certificate_prefix',
            self.test_certificate_prefix or 'TC/'
        )