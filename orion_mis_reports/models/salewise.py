from odoo import api, fields, models
import logging
from operator import itemgetter

_logger = logging.getLogger(__name__)


class SaleWise(models.TransientModel):
    _name = "orion_mis_reports.salewise"
    _description = "Salewise Reports"

    from_date = fields.Date('From', default=fields.Date.context_today)
    to_date = fields.Date('To', default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')

    tmp_oa_pending = fields.Float(default=0.0)
    tmp_oa_basic = fields.Float(default=0.0)
    tmp_pg_oa_pending = fields.Float(default=0.0)
    tmp_pg_oa_basic = fields.Float(default=0.0)

    sale_order_ids = fields.Many2many('sale.order', string="Sale Orders")
    cnt = fields.Integer(default=0)
    sale_type = fields.Selection([
        ('all', 'All Sales'),
        ('domestic', 'Domestic'),
        ('export', 'Export')
    ], string="Sale Type", default='all', required=True)

    # --------------------------
    # CURRENCY CONVERSION HELPER
    # --------------------------
    def _convert_to_inr(self, amount, currency_id, date=None):
        """Convert amount from given currency to INR"""
        if not currency_id:
            return amount

        inr_currency = self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
        if not inr_currency or currency_id == inr_currency:
            return amount

        # Use date_order or today's date for conversion
        conversion_date = date or fields.Date.context_today(self)

        # Convert from source currency to INR
        converted_amount = currency_id._convert(
            amount,
            inr_currency,
            self.env.company,
            conversion_date
        )

        return converted_amount

    # --------------------------
    # MAIN FILTER FUNCTION
    # --------------------------
    @api.model
    def _get_salewise(self):
        domain = [
            ('date_order', '>=', self.from_date),
            ('date_order', '<=', self.to_date),
            ('invoice_status', '!=', 'invoiced'),
            ('state', '=', 'sale')
        ]

        # Get India country ID
        india = self.env['res.country'].search([('code', '=', 'IN')], limit=1)

        # Filter based on sale type
        if self.sale_type == 'domestic':
            domain.append(('partner_id.country_id', '=', india.id))
        elif self.sale_type == 'export':
            domain.append(('partner_id.country_id', '!=', india.id))

        tmp_sale_order_ids = self.env['sale.order'].search(domain)

        # Filter by customer
        if self.partner_id:
            tmp_sale_order_ids = tmp_sale_order_ids.filtered(lambda so: so.partner_id == self.partner_id)

        # Filter by product (only orders containing this product)
        if self.product_id:
            tmp_sale_order_ids = tmp_sale_order_ids.filtered(lambda so: any(
                line.product_id == self.product_id for line in so.order_line))

        # Filter for partially delivered orders
        so_list = [{'sale_id': so, 'name': so.partner_id.name, 'oa_number': so.oa_number}
                   for so in tmp_sale_order_ids if any(
                line.qty_delivered < line.product_uom_qty for line in so.order_line)]

        # Sort by partner name
        sorted_so_list = sorted(so_list, key=itemgetter('name'))

        # Assign sale orders to wizard
        self.sale_order_ids = [(6, 0, [item['sale_id'].id for item in sorted_so_list])]
        return self.sale_order_ids

    def get_sale_type_label(self):
        selection_dict = dict(self._fields['sale_type'].selection)
        return selection_dict.get(self.sale_type, 'All Sales')

    def total_get_oa_pending(self):
        oa_pending = sum(
            self._convert_to_inr(
                ((line.product_uom_qty - line.qty_delivered) * line.price_unit),
                order.currency_id,
                order.date_order
            )
            for order in self.sale_order_ids
            for line in order.get_filtered_order_lines(self.product_id)
            if line.qty_delivered < line.product_uom_qty
        )
        _logger.info("Total OA Pending (INR) = %s", oa_pending)
        return oa_pending

    def total_get_oa_pending_with_tax(self):
        oa_pending_with_tax = sum(
            line.get_pending_amount_with_tax()
            for order in self.sale_order_ids
            for line in order.get_filtered_order_lines(self.product_id)
            if line.qty_delivered < line.product_uom_qty
        )
        _logger.info("Total OA Pending with Tax = %s", oa_pending_with_tax)
        return oa_pending_with_tax


    # --------------------------
    # REPORT GENERATION FUNCTION
    # --------------------------
    def create_salewise_report(self):
        """Generate Py3O report for filtered sales orders"""
        self._get_salewise()
        return self.env.ref('orion_mis_reports.py3o_salewise').report_action(self)


# ------------------------------------------
# EXTENSION OF SALE ORDER MODEL
# ------------------------------------------
class SaleOrderWise(models.Model):
    _inherit = 'sale.order'

    oa_number = fields.Char(string="OA Number")

    def get_oa_date(self):
        return self.date_order.strftime('%d-%m-%Y') if self.date_order else ''

    def get_oa_pending(self, product_id=False):
        """Return OA pending converted to INR"""
        lines = self.get_filtered_order_lines(product_id)
        pending_amount = sum(
            ((line.product_uom_qty - line.qty_delivered) * line.price_unit)
            for line in lines if line.qty_delivered < line.product_uom_qty
        )

        # Convert to INR
        inr_currency = self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
        if self.currency_id and self.currency_id != inr_currency and inr_currency:
            pending_amount = self.currency_id._convert(
                pending_amount,
                inr_currency,
                self.env.company,
                self.date_order or fields.Date.context_today(self)
            )

        return pending_amount

    def get_oa_basic(self, product_id=False):
        """Return OA basic converted to INR"""
        lines = self.get_filtered_order_lines(product_id)
        basic_amount = sum(
            (line.product_uom_qty * line.price_unit)
            for line in lines if line.qty_delivered < line.product_uom_qty
        )

        # Convert to INR
        inr_currency = self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
        if self.currency_id and self.currency_id != inr_currency and inr_currency:
            basic_amount = self.currency_id._convert(
                basic_amount,
                inr_currency,
                self.env.company,
                self.date_order or fields.Date.context_today(self)
            )

        return basic_amount

    def get_filtered_order_lines(self, product_id=False):
        """Return only those order lines for the selected product"""
        if not product_id:
            return self.order_line
        return self.order_line.filtered(lambda l: l.product_id.id == product_id.id)


# ------------------------------------------
# EXTENSION OF SALE ORDER LINE MODEL
# ------------------------------------------
class SaleOrderLineWise(models.Model):
    _inherit = 'sale.order.line'

    def get_total_tax_percent(self):
        """Get total tax percentage from tax_id field"""
        if self.tax_id:
            return sum(self.tax_id.mapped('amount'))
        return 0.0

    def get_pending_amount_with_tax(self):
        """Get pending amount (after discount, with tax applied) - converted to INR"""
        pending_qty = self.product_uom_qty - self.qty_delivered
        if pending_qty <= 0:
            return 0.0

        # Base amount after discount
        base_amount = pending_qty * self.price_unit * (1 - (self.discount / 100))

        # Get total tax percentage
        total_tax = self.get_total_tax_percent()

        # Apply tax
        amount_with_tax = base_amount * (1 + total_tax / 100)

        # Convert to INR
        inr_currency = self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
        if self.order_id.currency_id and self.order_id.currency_id != inr_currency and inr_currency:
            amount_with_tax = self.order_id.currency_id._convert(
                amount_with_tax,
                inr_currency,
                self.env.company,
                self.order_id.date_order or fields.Date.context_today(self)
            )

        return amount_with_tax

    def get_total_amount_with_tax(self):
        """Get total line amount (after discount, with tax applied) - converted to INR"""
        # Base amount after discount
        base_amount = self.product_uom_qty * self.price_unit * (1 - (self.discount / 100))

        # Get total tax percentage
        total_tax = self.get_total_tax_percent()

        # Apply tax
        amount_with_tax = base_amount * (1 + total_tax / 100)

        # Convert to INR
        inr_currency = self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
        if self.order_id.currency_id and self.order_id.currency_id != inr_currency and inr_currency:
            amount_with_tax = self.order_id.currency_id._convert(
                amount_with_tax,
                inr_currency,
                self.env.company,
                self.order_id.date_order or fields.Date.context_today(self)
            )

        return amount_with_tax

    def get_line_subtotal_with_tax(self):
        """Get line subtotal with tax converted to INR"""
        amount = self.price_total

        # Convert to INR
        inr_currency = self.env['res.currency'].search([('name', '=', 'INR')], limit=1)
        if self.order_id.currency_id and self.order_id.currency_id != inr_currency and inr_currency:
            amount = self.order_id.currency_id._convert(
                amount,
                inr_currency,
                self.env.company,
                self.order_id.date_order or fields.Date.context_today(self)
            )

        return amount



