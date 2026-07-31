from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    x_orion_reference = fields.Char(string="Orion Reference")
    x_orion_description = fields.Text(string="Orion Description")
    # x_gross_weight = fields.Float(string="Gross Weight (kg)")
    # x_net_weight = fields.Float(string="Net Weight (kg)")
    # x_invoice_issue_date = fields.Date(string="Date of Issue of Invoice")
    # x_invoice_removal_date = fields.Date(string="Date of Removal of Invoice")
    x_mcci_report = fields.Boolean(string="MCCI-Report by Buyer")
    x_docket_number = fields.Char(string="Docket Number")
    x_cash_on_delivery = fields.Char(string="Cash On Delivery")
    # Transport and Reference Details
    x_vessel_flight_no = fields.Char(string="Vessel/Flight No")
    x_final_destination = fields.Char(string="Final Destination")
    x_other_reference = fields.Char(string="Other Reference (if any)")

    # Tax and Currency Details
    x_apply_igst = fields.Boolean(string="Apply IGST")
    x_igst_percentage = fields.Float(string="IGST %")
    x_port_of_loading = fields.Char(string="Port of Loading")


    round_off = fields.Float(string='Round Off', compute='_compute_round_off', store=True)
    total_rounded = fields.Float(string='Total (Rounded)', compute='_compute_round_off', store=True)

    x_invoice_issue_date = fields.Date(
        string="Date of Issue of Invoice",
        readonly=True
    )
    x_invoice_removal_date = fields.Date(
        string="Date of Removal of Invoice",
        readonly=True
    )

    @api.model
    def create(self, vals):
        """Set x_invoice_issue_date automatically on creation."""
        if 'x_invoice_issue_date' not in vals:
            vals['x_invoice_issue_date'] = fields.Date.context_today(self)
        return super(AccountMove, self).create(vals)

    def action_post(self):
        """Set x_invoice_removal_date automatically when invoice is posted."""
        res = super(AccountMove, self).action_post()
        for move in self:
            if not move.x_invoice_removal_date:
                move.x_invoice_removal_date = fields.Date.context_today(self)
        return res

    @api.depends('amount_total')
    def _compute_round_off(self):
        for record in self:
            rounded_amount = round(record.amount_total)
            record.round_off = rounded_amount - record.amount_total
            record.total_rounded = rounded_amount


    currency_rate = fields.Float(
        string="Currency Rate",
        compute='_compute_currency_rate',
        store=True,
        readonly=True
    )


    x_currency_rate = fields.Float(
        string="Inverse Company Rate (INR per Unit)",
        compute='_compute_currency_rate',
        store=True,
        readonly=True,
        digits=(12, 6),
        help="Rate showing how many company currency units (INR) per 1 unit of foreign currency"
    )

    @api.depends('currency_id', 'date', 'company_currency_id')
    def _compute_currency_rate(self):
        for record in self:
            # Only compute rates if currency is different from company currency
            if (record.currency_id and
                    record.company_currency_id and
                    record.currency_id != record.company_currency_id and
                    record.date):

                try:
                    # Method 1: Get the actual rate from currency rates table
                    rate_record = self.env['res.currency.rate'].search([
                        ('currency_id', '=', record.currency_id.id),
                        ('company_id', '=', record.company_id.id),
                        ('name', '<=', record.date)
                    ], order='name DESC', limit=1)

                    if rate_record:
                        # Use the inverse company rate directly from the rate record
                        record.x_currency_rate = rate_record.inverse_company_rate
                        record.currency_rate = rate_record.rate
                        _logger.info(f"Found rate: {rate_record.rate}, Inverse: {rate_record.inverse_company_rate}")
                    else:
                        # Fallback: Use conversion rate method
                        # Get standard rate (foreign currency to company currency)
                        standard_rate = record.currency_id._get_conversion_rate(
                            record.currency_id,
                            record.company_currency_id,
                            record.company_id,
                            record.date
                        )
                        record.currency_rate = standard_rate
                        record.x_currency_rate = 1.0 / standard_rate if standard_rate != 0 else 0.0

                except Exception as e:
                    _logger.error(f"Error computing currency rates: {e}")
                    # Fallback calculation
                    standard_rate = record.currency_id._get_conversion_rate(
                        record.currency_id,
                        record.company_currency_id,
                        record.company_id,
                        record.date
                    )
                    record.currency_rate = standard_rate
                    record.x_currency_rate = 1.0 / standard_rate if standard_rate != 0 else 0.0

            else:
                # Same currency as company currency or missing data
                record.currency_rate = 1.0
                record.x_currency_rate = 1.0
