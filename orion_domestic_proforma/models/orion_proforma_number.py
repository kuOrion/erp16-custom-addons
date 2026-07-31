from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    proforma_no = fields.Char(
        string="Proforma No",
        default='draft',
        copy=False
    )
    def get_proforma_no(self):
        for order in self:
            if order.proforma_no == 'draft':

                prefix = self.env['ir.config_parameter'].sudo().get_param(
                    'orion_domestic_proforma.proforma_prefix',
                    default='PI'
                )

                number = self.env['ir.sequence'].next_by_code(
                    'proforma.invoice'
                ) or '0001'

                order.proforma_no = f"{prefix}{number}"

        return self.proforma_no