# from odoo import models, api
#
# class ReportDispatchNote(models.AbstractModel):
#     _name = 'report.orion_invoice_report.export_dispatch_note.odt'
#     _description = 'orion Export Dispatch Note Report'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['account.move'].browse(docids)
#         # Since we're processing a single document at a time in the template,
#         # we can pass the sale_order directly like in the working version
#         sale_order = False
#         if docs:
#             # Get the sale order for the first invoice
#             sale_order = self.env['sale.order'].search(
#                 [('name', '=', docs[0].invoice_origin)],
#                 limit=1
#             )
#
#         return {
#             'docs': docs,
#             'sale_order': sale_order,  # Pass single sale_order instead of dictionary
#         }

from odoo import models, api


class ReportDispatchNote(models.AbstractModel):
    _name = 'report.orion_invoice_report.export_dispatch_note'  # Remove .odt extension
    _description = 'orion Export Dispatch Note Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        sale_order = False

        if docs and docs[0].invoice_origin:
            # Get the sale order for the first invoice
            sale_order = self.env['sale.order'].search(
                [('name', '=', docs[0].invoice_origin)],
                limit=1
            )

        if not sale_order:
            sale_order = self.env['sale.order'].new({})

        return {
            'doc_ids': docids,
            'doc_model': 'account.move',
            'docs': docs,
            'sale_order': sale_order,
            'data': data,
        }