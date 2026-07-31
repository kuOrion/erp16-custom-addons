from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    sample_invoice_no = fields.Char(string="Sample Invoice No", default='draft')

    def get_sample_invoice_no(self):
        """Generate sequential sample invoice number with configurable prefix if invoice type is 'Sample Invoice'."""
        for rec in self:
            if rec.sample_invoice_no != 'draft':
                continue

            # Get related sale order
            sale_order = self.env['sale.order'].search([('name', '=', rec.invoice_origin)], limit=1)
            if not sale_order or sale_order.invoice_types != 'Sample Invoice':
                logger.info("Invoice type is not 'Sample Invoice', skipping sample_invoice_no generation.")
                continue

            # Get the prefix from configuration settings
            config_prefix = self.env['ir.config_parameter'].sudo().get_param(
                'orion_sample_invoice_report.sample_invoice_prefix', 'SI/'
            )

            # Manual sequence generation approach
            domain = [
                ('sample_invoice_no', '!=', 'draft'),
                ('sample_invoice_no', '!=', False),
                ('move_type', '=', 'out_invoice')
            ]
            existing_records = self.env['account.move'].search(domain)

            max_number = 0
            for record in existing_records:
                if record.sample_invoice_no and record.sample_invoice_no.startswith(config_prefix):
                    try:
                        number_part = record.sample_invoice_no.replace(config_prefix, '').strip()
                        current_number = int(number_part)
                        if current_number > max_number:
                            max_number = current_number
                    except ValueError:
                        continue

            # Generate next number
            next_number = max_number + 1
            rec.sample_invoice_no = config_prefix + str(next_number).zfill(4)
            logger.info("Generated sample_invoice_no = %s", rec.sample_invoice_no)

        return self.sample_invoice_no


