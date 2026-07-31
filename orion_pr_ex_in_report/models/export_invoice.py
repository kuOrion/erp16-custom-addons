# from odoo import api, models
#
#
# class ExportInvoiceReport(models.AbstractModel):
#     _name = 'report.orion_pr_ex_in_report.export_invoice'
#     _description = 'Export Invoice Report'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['sale.order'].browse(docids)
#         company = self.env.company
#         bank_info = company.bank_ids and company.bank_ids[0].bank_id or False
#
#         bank_details = {
#             "account_name": bank_info.account_name if bank_info else "",
#             "account_number": bank_info.account_number if bank_info else "",
#             "swift_code": bank_info.swift_code if bank_info else "",
#             "ifsc_code": bank_info.ifsc_code if bank_info else "",
#             "phone": bank_info.phone if bank_info else "",
#             "fax": bank_info.fax if bank_info else "",
#         }
#
#         return {
#             'doc_ids': docids,
#             'doc_model': 'sale.order',
#             'docs': docs,
#             'bank_info': bank_details,  # Pass bank details as a dictionary
#         }
# from odoo import api, models
#
#
# class ExportInvoiceReport(models.AbstractModel):
#     _name = 'report.orion_pr_ex_in_report.export_invoice'
#     _description = 'Export Invoice Report'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['sale.order'].browse(docids)
#         company = self.env.company
#         bank_info = company.bank_ids and company.bank_ids[0].bank_id or False
#
#         bank_details = {
#             "bank_name": bank_info.name if bank_info else "",
#             "bank_address": bank_info.street if bank_info else "",
#             "account_name": bank_info.account_name if bank_info else "",
#             "account_number": bank_info.account_number if bank_info else "",
#             "swift_code": bank_info.swift_code if bank_info else "",
#             "ifsc_code": bank_info.ifsc_code if bank_info else "",
#             "phone": bank_info.phone if bank_info else "",
#             "fax": bank_info.fax if bank_info else "  ",
#         }
#
#         return {
#             'doc_ids': docids,
#             'doc_model': 'sale.order',
#             'docs': docs,
#             'bank_info': bank_details,  # Pass bank details as a dictionary
#         }
from odoo import api, models

class ExportInvoiceReport(models.AbstractModel):
    _name = 'report.orion_pr_ex_in_report.export_invoice'
    _description = 'Export Invoice Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['sale.order'].browse(docids)

        # We assume you're printing only 1 at a time; get bank info from that sale order
        sale_order = docs[0] if docs else None
        bank = sale_order.bank_name if sale_order and sale_order.bank_name else None
        bank_info = {
            "bank_name": bank.name if bank and bank.name else "",
            "bank_address": bank.street if bank and bank.street else "",
            "account_name": bank.account_name if bank and bank.account_name else "",
            "account_number": bank.account_number if bank and bank.account_number else "",
            "swift_code": bank.swift_code if bank and bank.swift_code else "",
            "ifsc_code": bank.ifsc_code if bank and bank.ifsc_code else "",
            "phone": bank.phone if bank and bank.phone else "",
            "fax": bank.fax if bank and bank.fax else "",
        }

        #   bank_info = {
      #   "bank_name": bank.name if bank else "",
      #   "bank_address": bank.street if bank else "",
      #   "account_name": bank.account_name if bank else "",
      #   "account_number": bank.account_number if bank else "",
      #   "swift_code": bank.swift_code if bank else "",
      #   "ifsc_code": bank.ifsc_code if bank else "",
      #   "phone": bank.phone if bank else "",
      #   "fax": bank.fax if bank else "",
      #
      # }

        return {
            'doc_ids': docids,
            'doc_model': 'sale.order',
            'docs': docs,
            'bank_info': bank_info,
        }
