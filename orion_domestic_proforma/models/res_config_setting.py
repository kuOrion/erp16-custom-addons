# from odoo import models, fields
#
# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     proforma_prefix = fields.Char(
#         string="Proforma Prefix",
#         config_parameter='orion_domestic_proforma.proforma_prefix',
#         default='PI'
#     )


from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    proforma_prefix = fields.Char(
        string="Proforma Prefix",
        config_parameter='orion_domestic_proforma.proforma_prefix',
        default='PI'
    )

    def set_values(self):
        old_prefix = self.env['ir.config_parameter'].sudo().get_param(
            'orion_domestic_proforma.proforma_prefix'
        )

        super().set_values()

        if old_prefix != self.proforma_prefix:
            sequence = self.env['ir.sequence'].search([
                ('code', '=', 'proforma.invoice')
            ], limit=1)

            if sequence:
                sequence.number_next_actual = 1