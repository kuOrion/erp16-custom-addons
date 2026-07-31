# from odoo import models, api
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class ReportTaxInvoice(models.AbstractModel):
#     _name = 'report.orion_invoice_report.tax_invoice'
#     _description = 'Orion Tax Invoice Report'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['account.move'].browse(docids)
#         sale_orders = {}
#
#         try:
#             for invoice in docs:
#                 # Search for corresponding sale order
#                 sale_order = self.env['sale.order'].search([
#                     ('name', '=', invoice.invoice_origin)
#                 ], limit=1)
#
#                 if sale_order:
#                     sale_orders[invoice.id] = sale_order
#                 else:
#                     _logger.warning(
#                         f"No sale order found for invoice {invoice.name} "
#                         f"with origin {invoice.invoice_origin}"
#                     )
#                     sale_orders[invoice.id] = False
#
#             # Get the first sale order for backward compatibility
#             first_sale_order = next(iter(sale_orders.values())) if sale_orders else False
#
#             return {
#                 'doc_ids': docids,
#                 'doc_model': 'account.move',
#                 'docs': docs,
#                 'sale_orders': sale_orders,  # Dictionary of sale orders indexed by invoice ID
#                 'sale_order': first_sale_order,  # Single sale order for backward compatibility
#                 'get_sale_order': lambda invoice_id: sale_orders.get(invoice_id, False),  # Helper function
#             }
#
#         except Exception as e:
#             _logger.error(f"Error generating tax invoice report: {str(e)}")
#             raise

from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class ReportTaxInvoice(models.AbstractModel):
    _name = 'report.orion_invoice_report.tax_invoice'
    _description = 'Orion Tax Invoice Report'

    def extract_invoice_number(self, invoice_name):
        """ Extracts the numeric part of the invoice number """
        return invoice_name.split('/')[-1] if invoice_name else ''

    def get_bank_details(self):
        """Returns bank details directly from res.bank"""
        bank = self.env['res.bank'].search([], limit=1)
        return {
            'bank_name': bank.name or '',
            'account_name': bank.account_name or '',
            'account_number': bank.account_number or '',
            'swift_code': bank.swift_code or '',
            'ifsc_code': bank.ifsc_code or '',
            'phone': bank.phone or '',
            'fax': bank.fax or ''
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        sale_orders = {}

        try:
            for invoice in docs:
                # Search for corresponding sale order
                sale_order = self.env['sale.order'].search([
                    ('name', '=', invoice.invoice_origin)
                ], limit=1)

                if sale_order:
                    sale_orders[invoice.id] = sale_order
                else:
                    _logger.warning(
                        f"No sale order found for invoice {invoice.name} "
                        f"with origin {invoice.invoice_origin}"
                    )
                    sale_orders[invoice.id] = False

            # Get the first sale order for backward compatibility
            first_sale_order = next(iter(sale_orders.values())) if sale_orders else False

            # Get bank details as a dictionary
            bank_info = self.get_bank_details()

            return {
                'doc_ids': docids,
                'doc_model': 'account.move',
                'docs': docs,
                'sale_orders': sale_orders,
                'sale_order': first_sale_order,
                'get_sale_order': lambda invoice_id: sale_orders.get(invoice_id, False),
                'extract_invoice_number': self.extract_invoice_number,
                'bank_info': bank_info,  # Dictionary with bank details
            }

        except Exception as e:
            _logger.error(f"Error generating tax invoice report: {str(e)}")
            raise