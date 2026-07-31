from odoo import models, fields, api
from num2words import num2words
import math

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    freight_tax = fields.Many2many('account.tax', relation='account_tax_freight_purchase_tax_rel',string='Freight Taxes')

    def action_generate_py3o_report(self):
        report_action = self.env.ref('orion_reports.report_purchase_order')
        return report_action.report_action(self)



    def get_total_cgst(self):
        total_cgst = 0.0
        for line in self.order_line:
            total_cgst += (line.price_subtotal * line.cgst) / 100
        return total_cgst
    def get_total_sgst(self):
        total_sgst = 0.0
        for line in self.order_line:
            total_sgst += (line.price_subtotal * line.sgst) / 100
        return total_sgst

    def get_total_igst(self):
        total_igst = 0.0
        for line in self.order_line:
            total_igst += (line.price_subtotal * line.igst) / 100
        return total_igst

    def get_total(self):
        total = 0.0
        for line in self.order_line:
            total += line.price_subtotal
        return total

    def get_grand_total(self):
        total = self.get_total()
        decimal_part = total - int(total)  # Get decimal part

        if decimal_part >= 0.50:
            return int(total) + 1
        return int(total)

    def get_round_off(self):
        return self.get_grand_total() - self.get_total()

    def get_grand_total_in_words(self):
        grand_total = self.get_grand_total()
        # Convert to words using num2words
        total_in_words = num2words(grand_total, lang='en').capitalize()
        return total_in_words




    def get_freight_cgst(self):
        for tax in self.freight_tax:
            if "CGST" in tax.name:
                return tax.amount
        return 0

    def get_freight_sgst(self):
        for i in self.freight_tax:
            if "SGST" in i.name:
                return i.amount
            return 0

    def get_freight_igst(self):
        for i in self.freight_tax:
            if "IGST" in i.name:
                return i.amount
        return 0





