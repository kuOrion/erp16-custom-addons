from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    rfq_prefix = fields.Char(string="RFQ Prefix")
    po_prefix = fields.Char(string="PO Prefix")

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'purchase.rfq_prefix', self.rfq_prefix or ''
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'purchase.po_prefix', self.po_prefix or ''
        )

    def get_values(self):
        res = super().get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            rfq_prefix=params.get_param('purchase.rfq_prefix', default='RFQ'),
            po_prefix=params.get_param('purchase.po_prefix', default='PO'),
        )
        return res