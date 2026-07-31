# from odoo import api, models
# from num2words import num2words
#
# class ExportInvoiceReport(models.AbstractModel):
#     _name = 'report.orion_invoice_report.export_invoice'
#     _description = 'Export Invoice Report'
#
#     def extract_invoice_number(self, invoice_name):
#         """ Extracts the numeric part of the invoice number """
#         return invoice_name.split('/')[-1] if invoice_name else ''
#
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['account.move'].browse(docids)
#
#         # Fetch related sale order (assuming 1:1)
#         related_sale_order = None
#         if docs and docs[0].invoice_origin:
#             related_sale_order = self.env['sale.order'].search([('name', '=', docs[0].invoice_origin)], limit=1)
#
#         # Fetch bank information
#         sale_order = related_sale_order  # you need to use related_sale_order here
#         bank = sale_order.bank_name if sale_order and sale_order.bank_name else None
#
#         bank_info = {
#             "bank_name": bank.name if bank and bank.name else "",
#             "bank_address": bank.street if bank and bank.street else "",
#             "account_name": bank.account_name if bank and bank.account_name else "",
#             "account_number": bank.account_number if bank and bank.account_number else "",
#             "swift_code": bank.swift_code if bank and bank.swift_code else "",
#             "ifsc_code": bank.ifsc_code if bank and bank.ifsc_code else "",
#             "phone": bank.phone if bank and bank.phone else "",
#             "fax": bank.fax if bank and bank.fax else "",
#         }
#
#         return {
#             'doc_ids': docids,
#             'doc_model': 'account.move',
#             'docs': docs,
#             'sale_order': related_sale_order,
#             'extract_invoice_number': self.extract_invoice_number,
#             'bank_info': bank_info,
#
#         }
from odoo import api, models
from num2words import num2words

class ExportInvoiceReport(models.AbstractModel):
    _name = 'report.orion_invoice_report.export_invoice'
    _description = 'Export Invoice Report'

    def extract_invoice_number(self, invoice_name):
        """ Extracts the numeric part of the invoice number """
        return invoice_name.split('/')[-1] if invoice_name else ''

    def amount_to_words(self, amount):
        if amount:
            return num2words(amount, lang='en_IN').title() + " Only"
        return ''

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)

        # Fetch related sale order (assuming 1:1)
        related_sale_order = None
        if docs and docs[0].invoice_origin:
            related_sale_order = self.env['sale.order'].search([('name', '=', docs[0].invoice_origin)], limit=1)

        # Fetch bank information
        sale_order = related_sale_order
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

        return {
            'doc_ids': docids,
            'amount_to_words': self.amount_to_words,  # <-- fixed
            'doc_model': 'account.move',
            'docs': docs,
            'sale_order': related_sale_order,
            'extract_invoice_number': self.extract_invoice_number,
            'bank_info': bank_info,
        }
