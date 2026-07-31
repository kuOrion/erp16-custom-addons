from odoo import fields, models, api
# from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    now = fields.Datetime.now()

    grn_date = fields.Date(string="GRN Date", default=fields.Date.context_today)

    supplier_challan_no = fields.Char(string="Supplier Challan No")
    supplier_challan_date = fields.Date(string="Supplier Challan Date")
    grn_no = fields.Char(default='draft')
    #
    # def get_grn_no(self):
    #     if (self.grn_no == 'draft'):
    #         Seq = self.env['ir.sequence']
    #         self.grn_no = Seq.next_by_code('grn.report') or '  '
    #         _logger.info("grn_no = %s", self.grn_no)
    #     return self.grn_no
    def get_grn_no(self):
        for rec in self:
            if rec.grn_no == 'draft':
                Seq = self.env['ir.sequence']
                rec.grn_no = Seq.next_by_code('grn.report') or '  '
                _logger.info("GRN No = %s", rec.grn_no)
        return self.grn_no


