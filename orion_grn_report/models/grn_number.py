from odoo import models, fields, api
import logging

logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    grn_number = fields.Char(string="GRN Number", default=' ', readonly=True)

    def get_grn_number(self):
        """Generate sequential GRN number with configurable prefix for purchase receipts."""
        for rec in self:
            if rec.grn_number != ' ':
                continue

            # Only generate GRN for incoming shipments (purchase receipts)
            if rec.picking_type_id.code != 'incoming':
                logger.info("Picking type is not 'incoming', skipping GRN number generation.")
                continue

            # Get the prefix from configuration settings
            config_prefix = self.env['ir.config_parameter'].sudo().get_param(
                'purchase_grn_numbering.grn_prefix', 'GRN/'
            )

            # Manual sequence generation approach
            domain = [
                ('grn_number', '!=', ' '),
                ('grn_number', '!=', False),
                ('picking_type_id.code', '=', 'incoming')
            ]
            existing_records = self.env['stock.picking'].search(domain)

            max_number = 0
            for record in existing_records:
                if record.grn_number and record.grn_number.startswith(config_prefix):
                    try:
                        number_part = record.grn_number.replace(config_prefix, '').strip()
                        current_number = int(number_part)
                        if current_number > max_number:
                            max_number = current_number
                    except ValueError:
                        continue

            # Generate next number
            next_number = max_number + 1
            rec.grn_number = config_prefix + str(next_number).zfill(4)
            logger.info("Generated grn_number = %s", rec.grn_number)

        return self.grn_number

    def button_validate(self):
        """Override to generate GRN number when validating receipt."""
        result = super(StockPicking, self).button_validate()

        # Generate GRN number after validation for incoming pickings
        for picking in self:
            if picking.picking_type_id.code == 'incoming' and picking.grn_number == ' ':
                picking.get_grn_number()

        return result