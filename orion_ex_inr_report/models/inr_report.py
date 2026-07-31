# from odoo import models, api
# from datetime import datetime
# from num2words import num2words
#
#
# class ReportDispatchNote(models.AbstractModel):
#     _name = 'report.orion_ex_inr_report.inr_ex_report'
#     _description = 'Sample Invoice Report'
#
#     def extract_invoice_number(self, invoice_name):
#         """ Extracts the numeric part of the invoice number """
#         return invoice_name.split('/')[-1] if invoice_name else ''
#
#     def amount_to_words_inr(self, amount):
#         """Convert numeric amount to words in INR with paise"""
#         if not amount:
#             return "Zero Rupees Only"
#         integer_part = int(amount)
#         decimal_part = int(round((amount - integer_part) * 100))
#         words = num2words(integer_part, lang='en_IN').title() + " Rupees"
#         if decimal_part:
#             words += " and " + num2words(decimal_part, lang='en_IN').title() + " Paise"
#         return words + " Only"
#
#     def get_usd_to_inr_rate(self, date=None):
#         """ Get USD to INR conversion rate for the given date """
#         if not date:
#             date = datetime.now().date()
#
#         # Get USD currency
#         usd_currency = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
#         # Get INR currency
#         inr_currency = self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
#
#         if not usd_currency or not inr_currency:
#             return 1.0
#
#         # Get the conversion rate from USD to INR
#         # This uses Odoo's built-in currency conversion
#         rate = usd_currency._convert(1.0, inr_currency, self.env.company, date)
#         return rate
#
#     def convert_usd_to_inr(self, usd_amount, date=None):
#         """ Convert USD amount to INR using current exchange rate """
#         if not usd_amount:
#             return 0.0
#
#         rate = self.get_usd_to_inr_rate(date)
#         return usd_amount * rate
#
#     def format_currency(self, amount):
#         """ Format amount to 2 decimal places as string """
#         return "{:,.2f}".format(amount)
#
#     def get_currency_rate_info(self, date=None):
#         """ Get detailed currency rate information """
#         if not date:
#             date = datetime.now().date()
#
#         rate = self.get_usd_to_inr_rate(date)
#         return {
#             'rate': rate,
#             'date': date,
#             'formatted_rate': f"1 USD = {rate:.2f} INR"
#         }
#
#     def convert_invoice_line_values(self, line, date=None):
#         """Convert all relevant values of an invoice line from USD to INR"""
#         if line.currency_id.name != 'USD':
#             return {
#                 'price_unit': line.price_unit,
#                 'price_subtotal': line.price_subtotal,
#                 'discount': line.discount,
#                 'price_unit_inr': line.price_unit,
#                 'price_subtotal_inr': line.price_subtotal,
#                 'discount_inr': line.discount,
#             }
#
#         return {
#             'price_unit': line.price_unit,
#             'price_subtotal': line.price_subtotal,
#             'discount': line.discount,
#             'price_unit_inr': self.convert_usd_to_inr(line.price_unit, date),
#             'price_subtotal_inr': self.convert_usd_to_inr(line.price_subtotal, date),
#             'discount_inr': line.discount,  # Discount is percentage, no conversion needed
#         }
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['account.move'].browse(docids)
#
#         # Get sale order
#         sale_order = False
#         invoice_date = None
#         converted_lines = []
#
#         if docs:
#             # Get the sale order for the first invoice
#             sale_order = self.env['sale.order'].search(
#                 [('name', '=', docs[0].invoice_origin)],
#                 limit=1
#             )
#             # Get invoice date for currency conversion
#             invoice_date = docs[0].invoice_date or docs[0].date
#
#             # Convert all invoice lines
#             for line in docs[0].invoice_line_ids:
#                 converted_lines.append(self.convert_invoice_line_values(line, invoice_date))
#
#         # Get currency conversion information
#         currency_info = self.get_currency_rate_info(invoice_date)
#
#         # Example: Convert some sample amounts (you can modify based on your needs)
#         sample_conversions = {}
#         if docs:
#             doc = docs[0]
#             # Convert invoice total if it's in USD
#             if doc.currency_id.name == 'USD':
#                 sample_conversions = {
#                     'total_usd': doc.amount_total,
#                     'total_inr': self.convert_usd_to_inr(doc.amount_total, invoice_date),
#                     'untaxed_usd': doc.amount_untaxed,
#                     'untaxed_inr': self.convert_usd_to_inr(doc.amount_untaxed, invoice_date),
#                     'tax_usd': doc.amount_tax,
#                     'tax_inr': self.convert_usd_to_inr(doc.amount_tax, invoice_date),
#                 }
#
#         return {
#             'docs': docs,
#             'sale_order': sale_order,
#             'extract_invoice_number': self.extract_invoice_number,
#             'get_usd_to_inr_rate': self.get_usd_to_inr_rate,
#             'convert_usd_to_inr': self.convert_usd_to_inr,
#             'convert_invoice_line_values': self.convert_invoice_line_values,
#             'amount_to_words_inr': self.amount_to_words_inr,
#             'currency_info': currency_info,
#             'sample_conversions': sample_conversions,
#             'converted_lines': converted_lines,
#         }
from odoo import models, api
from num2words import num2words


class ReportDispatchNote(models.AbstractModel):
    _name = 'report.orion_ex_inr_report.inr_ex_report'
    _description = 'Sample Invoice Report'

    def extract_invoice_number(self, invoice_name):
        """Extract numeric part of invoice number"""
        return invoice_name.split('/')[-1] if invoice_name else ''

    def amount_to_words_inr(self, amount):
        """Convert amount to words"""
        if not amount:
            return "Zero Rupees Only"

        integer_part = int(amount)
        decimal_part = int(round((amount - integer_part) * 100))

        words = num2words(integer_part, lang='en_IN').title() + " Rupees"

        if decimal_part:
            words += " and " + num2words(decimal_part, lang='en_IN').title() + " Paise"

        return words + " Only"

    # def convert_usd_to_inr(self, usd_amount, currency_rate):
    #     """
    #     Convert USD amount to INR using stored invoice currency rate.
    #     """
    #     if not usd_amount:
    #         return 0.0
    #
    #     return usd_amount * (currency_rate or 1.0)
    def convert_usd_to_inr(self, usd_amount, currency_rate):
        ...
        return usd_amount * (currency_rate or 1.0)

    def format_currency(self, amount):
        """Format amount with commas"""
        return "{:,.2f}".format(amount)

    def get_currency_rate_info(self, move):
        """
        Return invoice currency rate information.
        """
        rate = move.currency_rate or 1.0

        return {
            'rate': rate,
            'date': move.invoice_date or move.date,
            'formatted_rate': f"1 USD = {rate:.4f} INR",
        }

    def convert_invoice_line_values(self, line, move):
        """
        Convert invoice line values using stored invoice currency rate.
        """

        currency_rate = move.currency_rate or 1.0

        if move.currency_id.name != 'USD':
            return {
                'price_unit': line.price_unit,
                'price_subtotal': line.price_subtotal,
                'discount': line.discount,
                'price_unit_inr': line.price_unit,
                'price_subtotal_inr': line.price_subtotal,
                'discount_inr': line.discount,
            }

        return {
            'price_unit': line.price_unit,
            'price_subtotal': line.price_subtotal,
            'discount': line.discount,
            'price_unit_inr': self.convert_usd_to_inr(
                line.price_unit,
                currency_rate
            ),
            'price_subtotal_inr': self.convert_usd_to_inr(
                line.price_subtotal,
                currency_rate
            ),
            'discount_inr': line.discount,  # Percentage, no conversion
        }

    @api.model
    def _get_report_values(self, docids, data=None):

        docs = self.env['account.move'].browse(docids)

        sale_order = False
        converted_lines = []
        currency_info = {}
        sample_conversions = {}

        if docs:

            move = docs[0]

            sale_order = self.env['sale.order'].search(
                [('name', '=', move.invoice_origin)],
                limit=1
            )

            # Currency Rate Information
            currency_info = self.get_currency_rate_info(move)

            # Convert Invoice Lines
            for line in move.invoice_line_ids:
                converted_lines.append(
                    self.convert_invoice_line_values(
                        line,
                        move
                    )
                )

            # Invoice Total Conversion
            if move.currency_id.name == 'USD':

                rate = move.currency_rate or 1.0

                sample_conversions = {
                    'currency_rate': rate,

                    'total_usd': move.amount_total,
                    'total_inr': self.convert_usd_to_inr(
                        move.amount_total,
                        rate
                    ),

                    'untaxed_usd': move.amount_untaxed,
                    'untaxed_inr': self.convert_usd_to_inr(
                        move.amount_untaxed,
                        rate
                    ),

                    'tax_usd': move.amount_tax,
                    'tax_inr': self.convert_usd_to_inr(
                        move.amount_tax,
                        rate
                    ),
                }

        return {
            'docs': docs,
            'sale_order': sale_order,
            'extract_invoice_number': self.extract_invoice_number,
            'convert_usd_to_inr': self.convert_usd_to_inr,
            'convert_invoice_line_values': self.convert_invoice_line_values,
            'amount_to_words_inr': self.amount_to_words_inr,
            'currency_info': currency_info,
            'sample_conversions': sample_conversions,
            'converted_lines': converted_lines,
        }