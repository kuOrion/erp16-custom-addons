
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class QuotationReportWizard(models.TransientModel):
    _name = "quotation.report.wizard"
    _description = "Quotation Reports"

    from_date = fields.Date(string="From", default=fields.Date.today)
    to_date = fields.Date(string="To", default=fields.Date.today)
    partner_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')
    quotation_type = fields.Selection([
        ('all', 'All Quotations'),
        ('domestic', 'Domestic'),
        ('export', 'Export')
    ], string="Quotation Type", default='all', required=True)

    def _get_quotation(self):
        # Standard Odoo uses 'state' to determine if it's a quotation or confirmed order
        # For quotations, typically state is 'draft' or 'sent'
        domain = [
            ('date_order', '>=', self.from_date),
            ('date_order', '<=', self.to_date),
            ('state', 'in', ['draft', 'sent'])  # Replace 'is_order' with standard Odoo states
        ]

        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))
        if self.product_id:  # Changed from elif to if to allow both filters simultaneously
            domain.append(('order_line.product_id', '=', self.product_id.id))

        # Get India country ID
        india = self.env['res.country'].search([('code', '=', 'IN')], limit=1)

        # Filter based on quotation type (domestic/export)
        if self.quotation_type == 'domestic':
            domain.append(('partner_id.country_id', '=', india.id))
        elif self.quotation_type == 'export':
            domain.append(('partner_id.country_id', '!=', india.id))

        sale_order_ids = self.env['sale.order'].search(domain)
        _logger.info("Found %d sale orders", len(sale_order_ids))
        return sale_order_ids

    def create_quotation_report(self):
        return self.env.ref('orion_mis_quotation.py3o_mis_quotation').report_action(self)

    def get_total_amount(self):
        return sum(order.amount_untaxed for order in self._get_quotation())

    def get_total_amount_with_tax(self):
        return sum(order.amount_total for order in self._get_quotation())

    def get_total_product_quantity(self):
        """
        Calculate the total quantity of products in the quotations.
        If a specific product is selected, it returns the total quantity of that product.
        If no specific product is selected, it returns the total quantity across all products.
        """
        quotations = self._get_quotation()

        if self.product_id:
            # If a specific product is selected, sum only that product's quantities
            return sum(
                line.product_uom_qty
                for order in quotations
                for line in order.order_line
                if line.product_id.id == self.product_id.id
            )
        else:
            # If no specific product is selected, sum quantities of all products
            return sum(
                line.product_uom_qty
                for order in quotations
                for line in order.order_line
            )

    def get_quotation_type_label(self):
        """Return the label for the selected quotation type"""
        selection_dict = dict(self._fields['quotation_type'].selection)
        return selection_dict.get(self.quotation_type, 'All Quotations')