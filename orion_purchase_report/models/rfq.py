from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def get_report_data(self):
        """Prepare data for the Py3O report"""
        report_data = []
        for order in self:
            for line in order.order_line:
                report_data.append({
                    'product_name': line.product_id.display_name or '',
                    'description': line.name or '',
                    'quantity': line.product_qty or 0.0,
                    'expected_date': line.date_planned.strftime('%Y-%m-%d') if line.date_planned else '',
                    'price_unit': line.price_unit or 0.0,
                    'subtotal': line.price_subtotal or 0.0,
                })
        _logger.info("Report Data: %s", report_data)
        return report_data