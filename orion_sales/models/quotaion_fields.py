from email.policy import default

from odoo import models, fields, api
from datetime import date



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    customer_po_number = fields.Char(string="Customer PO Number")
    customer_po_date = fields.Date(string="Customer PO Date")
    transporter = fields.Many2one(
        'sale.transporter.option',
        string="Transporter"
    )

    terms_and_conditions = fields.Many2one(
        'sale.terms.conditions.option',
        string="Terms and Conditions"
    )

    reference_type = fields.Selection(
        [('sale order', 'sale order'),
         ('sample order', 'sample order'),
         ('Export order', 'Export order'),
         ('Service order', 'Service order')],
        string="Reference Type"
    )
    invoice_types = fields.Selection(
        [('Invoice Domestic', 'Invoice Domestic'),
         ('GST Invoice', 'GST Invoice'),
         ('Invoice Export (Trading)', 'Invoice Export (Trading)'),
         ('Invoice Rejection', 'Invoice Rejection'),
         ('Invoice Rejection Material', 'Invoice Rejection material'),
         ('Sales Rejection cum credit note', 'Sales Rejection cum credit note'),
         ('Sample Invoice', 'Sample Invoice'),
         ('Service Invoice', 'Service Invoice'),
         ('Dispatch Invoice', 'Dispatch Invoice')],
        string="Invoice Types"
    )
    insurance_terms = fields.Selection(
        [('By us', 'By us'),
         ('By you', 'By you '),
         ('Not Required', 'Not Required')],
        string="Insurance terms"
    )
    test_certificate = fields.Boolean(string="Test Certificate")
    dispatch_instructions = fields.Text(string="Dispatch Instructions")
    # quotation_subject = fields.Char(string="Quotation Subject", default="Orion Instruments' Pressure & Temperature Switches")
    quotation_subject = fields.Char(
        string="Quotation Subject",
        default="Orion Instruments' Pressure & Temperature Switches"
    )

    bid_details = fields.Text(string="BID Details")
    your_reference = fields.Char(string="Your Reference")
    # our_reference = fields.Char(string="Our Reference")
    freight = fields.Float(string="Freight")
    _note = fields.Char(string="note")
    freight_tax_id = fields.Many2one('account.tax', string="Freight Tax", domain="[('type_tax_use', '=', 'sale')]")
    insurance_tax_id = fields.Many2one('account.tax', string="Insurance Tax", domain="[('type_tax_use', '=', 'sale')]")
    packaging_tax_id = fields.Many2one('account.tax', string="Packaging Tax", domain="[('type_tax_use', '=', 'sale')]")

    # Computed Fields for taxes
    freight_taxes = fields.Float(string="Freight Taxes", compute="_compute_freight_taxes", store=True)
    insurance_taxes = fields.Float(string="Insurance Taxes", compute="_compute_insurance_taxes", store=True)
    packaging_taxes = fields.Float(string="Packaging Taxes", compute="_compute_packaging_taxes", store=True)

    discount_percent = fields.Float(string="Discount %")
    insurance = fields.Float(string="Insurance")
    packaging_percent = fields.Float(string="Packaging %")


    @api.depends('freight_tax_id')
    def _compute_freight_taxes(self):
        for order in self:
            if order.freight_tax_id:
                order.freight_taxes = order.freight_tax_id.amount

    @api.depends('insurance_tax_id')
    def _compute_insurance_taxes(self):
        for order in self:
            if order.insurance_tax_id:
                order.insurance_taxes = order.insurance_tax_id.amount

    @api.depends('packaging_tax_id')
    def _compute_packaging_taxes(self):
        for order in self:
            if order.packaging_tax_id:
                order.packaging_taxes = order.packaging_tax_id.amount


#  fields for "Orion-Tax Terms"
    price_terms = fields.Many2one(
        'sale.price.term.option',
        string="Price Terms"
    )

    delivery = fields.Many2one(
        'sale.delivery.option',
        string="Delivery"
    )

    third_party_inspection = fields.Many2one(
        'sale.third.party.inspection.option',
        string="Third Party Inspection"
    )

    bank_charges = fields.Many2one(
        'sale.bank.charges.option',
        string="Bank Charges"
    )

    mode_of_transport = fields.Many2one(
        'sale.mode.transport.option',
        string="Mode of Transport"
    )
    other_term = fields.Many2one(
        'sale.other.term.option',
        string="Other Term"
    )

    bank_name = fields.Many2one('res.bank', string="Bank Name", create=True)


    no_of_packages = fields.Integer(string="Number of Packages")
    validity = fields.Many2one(
        'sale.validity.option',
        string="Validity",
        help="Select or create a validity option."
    )

    accessories = fields.Many2one(
        'sale.accessories.option',
        string="Accessories"
    )

    p_and_f = fields.Many2one(
        'sale.pandf.option',
        string="P & F"
    )

    warranty = fields.Many2one(
        'sale.warranty.option',
        string="Warranty"
    )

    freight_terms = fields.Selection([
        ('On Your Account', 'On Your Account'),
        ('To be born by you', 'To be borne by you'),
        ('To be born by us', 'To be borne by us'),
        ('Inclusive', 'Inclusive'),
        ('Included in the product price', 'Included in the product price'),
        ('3%', '3%'),
        ('1%', '1%'),
    ], string="Freight Terms")

    pre_carriage = fields.Many2one(
        'sale.pre.carriage.option',
        string="Pre Carriage"
    )

    port_of_discharge = fields.Char(string="Port of Discharge")



    our_reference = fields.Char(string="Our Reference", readonly=True, copy=False)

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)

        # Initial value when quotation is created
        quotation_number = order.name or ''
        today_date = date.today().strftime("%Y-%m-%d")
        order.our_reference = f"{quotation_number} - {today_date}"

        return order

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for order in self:
            # Update the reference once order is confirmed
            order_number = order.name or ''
            today_date = date.today().strftime("%Y-%m-%d")
            order.our_reference = f"{order_number} - {today_date}"

        return res
