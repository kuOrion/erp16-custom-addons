# from odoo import api, fields, models, _
# import logging
# from operator import itemgetter
#
# _logger = logging.getLogger(__name__)
#
#
# class InvoiceWise(models.TransientModel):
#     _name = "orion_mis_invoice.invoicewise"
#     _description = "Invoicewise Reports"
#
#     from_date = fields.Date(string="From", default=fields.Date.context_today)
#     to_date = fields.Date(string="To", default=fields.Date.context_today)
#     partner_id = fields.Many2one('res.partner', string='Customer')
#     product_id = fields.Many2one('product.product', string='Product')
#
#     list_invoice_ids = fields.Many2many('account.move', string="Invoices")
#     company_id = fields.Many2one('res.company', string='Company',
#                                  default=lambda self: self.env.company)
#     amount_total = fields.Monetary(string="Total Amount", compute="_compute_amount_total")
#     currency_id = fields.Many2one('res.currency', string='Currency',
#                                   related='company_id.currency_id', readonly=True)
#     invoice_type = fields.Selection([
#         ('all', 'All Invoices'),
#         ('domestic', 'Domestic'),
#         ('export', 'Export')
#     ], string="Invoice Type", default='all', required=True)
#
#     @api.depends('list_invoice_ids')
#     def _compute_amount_total(self):
#         for record in self:
#             record.amount_total = sum(inv.amount_total for inv in record.list_invoice_ids)
#
#     @api.model
#     def _get_invoicewise(self):
#         domain = [
#             ('invoice_date', '>=', self.from_date),
#             ('invoice_date', '<=', self.to_date),
#             ('state', '=', 'posted'),
#             ('move_type', '=', 'out_invoice'),
#             ('company_id', '=', self.company_id.id)
#         ]
#
#         if self.partner_id:
#             domain.append(('partner_id', '=', self.partner_id.id))
#         if self.product_id:
#             domain.append(('invoice_line_ids.product_id', '=', self.product_id.id))
#
#         # Get the India country ID
#         india = self.env['res.country'].search([('code', '=', 'IN')], limit=1)
#
#         # Filter based on invoice type (domestic/export)
#         if self.invoice_type == 'domestic':
#             domain.append(('partner_id.country_id', '=', india.id))
#         elif self.invoice_type == 'export':
#             domain.append(('partner_id.country_id', '!=', india.id))
#
#         invoice_ids = self.env['account.move'].search(domain, order='invoice_date')
#
#         for inv in invoice_ids:
#             _logger.info("Processing Invoice: %s, Date: %s, Amount: %s",
#                          inv.name, inv.invoice_date, inv.amount_total)
#
#         self.list_invoice_ids = invoice_ids
#         return invoice_ids
#
#     def get_total_amount(self):
#         """Calculate total amount without tax, considering currency rate"""
#         amount = 0
#         for invoice in self.list_invoice_ids:
#             # Use currency_rate for the calculation
#             amount += invoice.amount_untaxed * invoice.currency_rate
#             _logger.info("Invoice: %s, Amount: %s, Rate: %s",
#                          invoice.name, invoice.amount_untaxed, invoice.currency_rate)
#         return amount
#
#     def get_total_amount_with_tax(self):
#         """Calculate total amount with tax, considering currency rate"""
#         amount_with_tax = 0
#         for invoice in self.list_invoice_ids:
#             # Use currency_rate for the calculation
#             amount_with_tax += invoice.amount_total * invoice.currency_rate
#         return amount_with_tax
#
#     def get_total_tax_amount(self):
#         """Calculate total tax amount, considering currency rate"""
#         tax_amount = 0
#         for invoice in self.list_invoice_ids:
#             # Use currency_rate for the calculation
#             tax_amount += invoice.amount_tax * invoice.currency_rate
#         return tax_amount
#
#     def create_invoicewise_report(self):
#         """Generate the invoice report"""
#         self._get_invoicewise()  # Ensure invoices are loaded
#         return self.env.ref('orion_mis_invoice.invoice_report').report_action(self, config=None)
#
#     def _get_report_data(self):
#         """Get formatted data for the report"""
#         return {
#             'doc_ids': self.ids,
#             'doc_model': 'orion_mis_invoice.invoicewise',
#             'docs': self,
#             'invoices': self.list_invoice_ids,
#             'total_amount': self.get_total_amount(),
#             'total_tax': self.get_total_tax_amount(),
#             'total_with_tax': self.get_total_amount_with_tax(),
#             'amount_total': self.get_total_amount_with_tax(),
#             'currency_id': self.company_id.currency_id,
#         }
#
#
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     currency_rate = fields.Float(string='Currency Rate', compute='_compute_currency_rate', store=True,
#                                  help="Rate used to convert the currency to the company currency")
#
#     @api.depends('currency_id', 'company_id', 'invoice_date')
#     def _compute_currency_rate(self):
#         """Compute the currency rate for the invoice"""
#         for invoice in self:
#             date = invoice.invoice_date or fields.Date.context_today(invoice)
#             company = invoice.company_id
#             if invoice.currency_id and company and invoice.currency_id != company.currency_id:
#                 # Get currency rate from the invoice date
#                 currency_rate = invoice.currency_id._get_conversion_rate(
#                     invoice.currency_id, company.currency_id, company, date)
#                 invoice.currency_rate = currency_rate
#             else:
#                 # If same currency as company or no company, rate is 1
#                 invoice.currency_rate = 1.0
#
#     def get_invoice_details(self):
#         """Get formatted invoice details for reporting"""
#         self.ensure_one()
#         return {
#             'number': self.name,
#             'date': self.invoice_date,
#             'partner': self.partner_id.name,
#             'amount_untaxed': self.amount_untaxed,
#             'amount_tax': self.amount_tax,
#             'amount_total': self.amount_total,
#             'currency': self.currency_id.symbol,
#             'currency_rate': self.currency_rate
#         }


# from odoo import api, fields, models, _
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class InvoiceWise(models.TransientModel):
#             _name = "orion_mis_invoice.invoicewise"
#             _description = "Invoicewise Reports"
#
#             from_date = fields.Date(string="From", default=fields.Date.context_today)
#             to_date = fields.Date(string="To", default=fields.Date.context_today)
#             partner_id = fields.Many2one('res.partner', string='Customer')
#             product_id = fields.Many2one('product.product', string='Product')
#
#             list_invoice_ids = fields.Many2many('account.move', string="Invoices")
#             company_id = fields.Many2one('res.company', string='Company',
#                                          default=lambda self: self.env.company)
#             amount_total = fields.Monetary(string="Total Amount", compute="_compute_amount_total")
#             currency_id = fields.Many2one('res.currency', string='Currency',
#                                           related='company_id.currency_id', readonly=True)
#             invoice_type = fields.Selection([
#                 ('all', 'All Invoices'),
#                 ('domestic', 'Domestic'),
#                 ('export', 'Export')
#             ], string="Invoice Type", default='all', required=True)
#
#             @api.depends('list_invoice_ids')
#             def _compute_amount_total(self):
#                 for record in self:
#                     record.amount_total = sum(inv.amount_total for inv in record.list_invoice_ids)
#
#             @api.model
#             def _get_invoicewise(self):
#                 domain = [
#                     ('invoice_date', '>=', self.from_date),
#                     ('invoice_date', '<=', self.to_date),
#                     ('state', '=', 'posted'),
#                     ('move_type', '=', 'out_invoice'),
#                     ('company_id', '=', self.company_id.id)
#                 ]
#
#                 if self.partner_id:
#                     domain.append(('partner_id', '=', self.partner_id.id))
#                 if self.product_id:
#                     domain.append(('invoice_line_ids.product_id', '=', self.product_id.id))
#
#                 # Get the India country ID
#                 india = self.env['res.country'].search([('code', '=', 'IN')], limit=1)
#
#                 # Filter based on invoice type (domestic/export)
#                 if self.invoice_type == 'domestic':
#                     domain.append(('partner_id.country_id', '=', india.id))
#                 elif self.invoice_type == 'export':
#                     domain.append(('partner_id.country_id', '!=', india.id))
#
#                 invoice_ids = self.env['account.move'].search(domain, order='invoice_date')
#
#                 for inv in invoice_ids:
#                     _logger.info("Processing Invoice: %s, Date: %s, Amount: %s",
#                                  inv.name, inv.invoice_date, inv.amount_total)
#
#                 self.list_invoice_ids = invoice_ids
#                 return invoice_ids
#
#             def get_total_amount(self):
#                 """Calculate total amount without tax, considering currency rate"""
#                 return sum(inv.amount_untaxed * inv.currency_rate for inv in self.list_invoice_ids)
#
#             def get_total_amount_with_tax(self):
#                 """Calculate total amount with tax, considering currency rate"""
#                 return sum(inv.amount_total * inv.currency_rate for inv in self.list_invoice_ids)
#
#             def get_total_tax_amount(self):
#                 """Calculate total tax amount, considering currency rate"""
#                 return sum(inv.amount_tax * inv.currency_rate for inv in self.list_invoice_ids)
#
#             def create_invoicewise_report(self):
#                 """Generate the invoice report"""
#                 self._get_invoicewise()  # Ensure invoices are loaded
#                 return self.env.ref('orion_mis_invoice.invoice_report').report_action(self, config=None)
#
#
#
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     currency_rate = fields.Float(string='Currency Rate', compute='_compute_currency_rate', store=True,
#                                  help="Rate used to convert the currency to the company currency")
#
#     @api.depends('currency_id', 'company_id', 'invoice_date')
#     def _compute_currency_rate(self):
#         """Compute the currency rate for the invoice"""
#         for invoice in self:
#             date = invoice.invoice_date or fields.Date.context_today(invoice)
#             company = invoice.company_id
#             if invoice.currency_id and company and invoice.currency_id != company.currency_id:
#                 currency_rate = invoice.currency_id._get_conversion_rate(
#                     invoice.currency_id, company.currency_id, company, date)
#                 invoice.currency_rate = currency_rate
#             else:
#                 invoice.currency_rate = 1.0
#
#     def get_invoice_details(self):
#         """Get formatted invoice details for reporting"""
#         self.ensure_one()
#         return {
#             'number': self.name,
#             'date': self.invoice_date,
#             'partner': self.partner_id.name,
#             'amount_untaxed': self.amount_untaxed,
#             'amount_tax': self.amount_tax,
#             'amount_total': self.amount_total,
#             'currency': self.currency_id.symbol,
#             'currency_rate': self.currency_rate
#         }


from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class InvoiceWise(models.TransientModel):
    _name = "orion_mis_invoice.invoicewise"
    _description = "Invoicewise Reports"

    from_date = fields.Date(string="From", default=fields.Date.context_today)
    to_date = fields.Date(string="To", default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')

    list_invoice_ids = fields.Many2many('account.move', string="Invoices")
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company
    )
    amount_total = fields.Monetary(
        string="Total Amount",
        compute="_compute_amount_total"
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='company_id.currency_id',
        readonly=True
    )
    invoice_type = fields.Selection([
        ('all', 'All Invoices'),
        ('domestic', 'Domestic'),
        ('export', 'Export')
    ], string="Invoice Type", default='all', required=True)

    # -------------------------
    # Compute total amount
    # -------------------------
    @api.depends('list_invoice_ids')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = sum(inv.amount_total for inv in record.list_invoice_ids)

    # -------------------------
    # Fetch filtered invoices
    # -------------------------
    @api.model
    def _get_invoicewise(self):
        domain = [
            ('invoice_date', '>=', self.from_date),
            ('invoice_date', '<=', self.to_date),
            ('state', '=', 'posted'),
            ('move_type', '=', 'out_invoice'),
            ('company_id', '=', self.company_id.id)
        ]

        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        if self.product_id:
            domain.append(('invoice_line_ids.product_id', '=', self.product_id.id))

        # Get India country for domestic/export filter
        india = self.env['res.country'].search([('code', '=', 'IN')], limit=1)

        if self.invoice_type == 'domestic':
            domain.append(('partner_id.country_id', '=', india.id))
        elif self.invoice_type == 'export':
            domain.append(('partner_id.country_id', '!=', india.id))

        invoice_ids = self.env['account.move'].search(domain, order='invoice_date')

        for inv in invoice_ids:
            _logger.info("Processing Invoice: %s, Date: %s, Amount: %s",
                         inv.name, inv.invoice_date, inv.amount_total)

        self.list_invoice_ids = invoice_ids
        return invoice_ids

    # -------------------------
    # Amount Calculations
    # -------------------------
    def get_total_amount(self):
        """Calculate total amount without tax, considering currency rate"""
        return sum(inv.amount_untaxed * inv.currency_rate for inv in self.list_invoice_ids)

    def get_total_amount_with_tax(self):
        """Calculate total amount with tax, considering currency rate"""
        return sum(inv.amount_total * inv.currency_rate for inv in self.list_invoice_ids)

    def get_total_tax_amount(self):
        """Calculate total tax amount, considering currency rate"""
        return sum(inv.amount_tax * inv.currency_rate for inv in self.list_invoice_ids)

    def get_product_wise_total_amount(self):
        """Return total amount only for the selected product"""
        total = 0.0
        for inv in self.list_invoice_ids:
            for line in inv.invoice_line_ids:
                if self.product_id and line.product_id.id == self.product_id.id:
                    total += line.price_subtotal * inv.currency_rate
        return total

    def get_product_wise_total_amount_with_tax(self):
        """Return total amount WITH tax only for the selected product"""
        total = 0.0

        for inv in self.list_invoice_ids:
            for line in inv.invoice_line_ids:

                # Skip lines not matching the selected product
                if self.product_id and line.product_id.id != self.product_id.id:
                    continue

                # Compute taxes for the line
                taxes = line.tax_ids.compute_all(
                    line.price_unit,
                    inv.currency_id,
                    line.quantity,
                    product=line.product_id,
                    partner=inv.partner_id
                )

                subtotal = taxes.get('total_excluded', 0.0)
                total_with_tax = taxes.get('total_included', 0.0)

                # Correct tax amount
                tax_amount = total_with_tax - subtotal

                # Add (subtotal + tax) × currency rate
                total += (subtotal + tax_amount) * inv.currency_rate

        return total

    # -------------------------
    # Get filtered invoice lines
    # -------------------------
    def get_filtered_invoice_lines(self, invoice):
        """Return only lines that match the selected product (if any)"""
        if self.product_id:
            return invoice.invoice_line_ids.filtered(lambda l: l.product_id == self.product_id)
        return invoice.invoice_line_ids

    # -------------------------
    # Create Py3O Report
    # -------------------------
    def create_invoicewise_report(self):
        """Generate the invoice report"""
        self._get_invoicewise()  # Ensure invoices are loaded
        return self.env.ref('orion_mis_invoice.invoice_report').report_action(self, config=None)


# --------------------------------------------------------------------------
# EXTENSION OF ACCOUNT MOVE (for currency conversion and details)
# --------------------------------------------------------------------------
class AccountMove(models.Model):
    _inherit = 'account.move'

    currency_rate = fields.Float(
        string='Currency Rate',
        compute='_compute_currency_rate',
        store=True,
        help="Rate used to convert the currency to the company currency"
    )

    @api.depends('currency_id', 'company_id', 'invoice_date')
    def _compute_currency_rate(self):
        """Compute the currency rate for the invoice"""
        for invoice in self:
            date = invoice.invoice_date or fields.Date.context_today(invoice)
            company = invoice.company_id
            if invoice.currency_id and company and invoice.currency_id != company.currency_id:
                currency_rate = invoice.currency_id._get_conversion_rate(
                    invoice.currency_id, company.currency_id, company, date)
                invoice.currency_rate = currency_rate
            else:
                invoice.currency_rate = 1.0

    def get_invoice_details(self):
        """Get formatted invoice details for reporting"""
        self.ensure_one()
        return {
            'number': self.name,
            'date': self.invoice_date,
            'partner': self.partner_id.name,
            'amount_untaxed': self.amount_untaxed,
            'amount_tax': self.amount_tax,
            'amount_total': self.amount_total,
            'currency': self.currency_id.symbol,
            'currency_rate': self.currency_rate
        }
