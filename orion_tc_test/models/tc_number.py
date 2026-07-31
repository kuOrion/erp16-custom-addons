
from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    tc_no = fields.Char(string="Test Certificate No", default='draft')

    def get_test_certi_no(self):
        if (self.tc_no == 'draft'):
            # Get the prefix from configuration settings
            config_prefix = self.env['ir.config_parameter'].sudo().get_param(
                'orion_tc_test.test_certificate_prefix', 'TC/'
            )

            # Manual sequence generation approach
            # Get the highest number from existing records
            domain = [('tc_no', '!=', 'draft'), ('tc_no', '!=', False)]
            existing_records = self.env['stock.picking'].search(domain)

            max_number = 0
            for record in existing_records:
                if record.tc_no and record.tc_no.startswith(config_prefix):
                    try:
                        # Extract number part after prefix
                        number_part = record.tc_no.replace(config_prefix, '').strip()
                        current_number = int(number_part)
                        if current_number > max_number:
                            max_number = current_number
                    except ValueError:
                        continue

            # Generate next number
            next_number = max_number + 1
            self.tc_no = config_prefix + str(next_number).zfill(4)

        logger.info("Generated tc_no = %s", self.tc_no)
        return self.tc_no