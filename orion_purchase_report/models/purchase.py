from odoo import api, fields, models


class ReportPurchaseOrder(models.AbstractModel):
    _name = 'report.orion_reports.report_purchase_order'
    _description = 'Purchase Order Report Template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['purchase.order'].browse(docids)


        return {
            'doc_ids': docids,
            'doc_model': 'purchase.order',
            'docs': docs,
            'get_total_cgst': docs.get_total_cgst,
            'get_total_sgst': docs.get_total_sgst,
            'get_total_igst': docs.get_total_igst,
            'get_round_off': docs.get_round_off,
            'get_total': docs.get_total,
            'get_grand_total': docs.get_grand_total,
            'get_grand_total_in_words': docs.get_grand_total_in_words,
            'get_freight_cgst': docs.get_freight_cgst,
            'get_freight_sgst': docs.get_freight_sgst,
            'get_freight_igst': docs.get_freight_igst,

            # 'get_index': lambda line: list(line.order_id.order_line).index(line) + 1,
            'compute_total_tax': self._compute_total_tax

        }
    #
    # def _compute_total_tax(self, line):
    #     return line.cgst_amount + line.sgst_amount + line.igst_amount
