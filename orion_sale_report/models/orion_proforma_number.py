from odoo import models, fields, api
from datetime import datetime

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    proforma_no = fields.Char(string="Proforma No", default='draft')

    def get_proforma_no(self):
        for order in self:
            if order.proforma_no == 'draft':
                year_suffix = datetime.now().strftime('%y')  # '25' for 2025
                number = self.env['ir.sequence'].next_by_code('proforma.invoice') or '0000'
                order.proforma_no = f"PI{year_suffix}/{number}"
        return order.proforma_no



class ReportProforma(models.AbstractModel):
    _name = 'report.orion_sale_report.report_proforma'
    _description = 'Orion Proforma Report'

    def _get_report_values(self, docids, data=None):
        orders = self.env['sale.order'].browse(docids)
        for order in orders:
            order.get_proforma_no()
        return {
            'docs': orders,
        }



