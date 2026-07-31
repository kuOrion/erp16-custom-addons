# from odoo import api, fields, models, _
# from datetime import datetime
# from odoo.exceptions import UserError
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class PditofgReport(models.TransientModel):
#     _name = "pditofg.report"
#     _description = "PDI to FG Report"
#
#     from_date = fields.Date('From', default=fields.Date.context_today)
#     to_date = fields.Date('To', default=fields.Date.context_today)
#     product_id = fields.Many2one('product.product', string='Product')
#
#     def get_pditofg(self):
#         IrConfigParam = self.env['ir.config_parameter'].sudo()
#         td_manufactured_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_manufactured_location_id')
#         td_fg_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_fg_location_id')
#
#         if not td_manufactured_location_id:
#             raise UserError(_('Please configure "Route Transfer Locations" from inventory > setting menu!'))
#         if not td_fg_location_id:
#             raise UserError(_('Please configure "Route Transfer Locations" from inventory > setting menu!'))
#
#         # Converting string IDs to integers
#         td_manufactured_location_id = int(td_manufactured_location_id)
#         td_fg_location_id = int(td_fg_location_id)
#
#         # Search for stock pickings matching our criteria
#         # pickings = self.env['stock.picking'].search([
#         #     ('date_done', '>=', self.from_date),
#         #     ('date_done', '<=', self.to_date),
#         #     ('location_id', '=', td_manufactured_location_id),
#         #     ('location_dest_id', '=', td_fg_location_id),
#         #     ('state', '=', 'done')
#         # ])
#         all_pickings = self.env['stock.picking'].search([('state', '=', 'done')])
#         _logger.info(f"Total done pickings in system: {len(all_pickings)}")
#         for loc in [(td_manufactured_location_id, 'manufactured'), (td_fg_location_id, 'fg')]:
#             loc_pickings = self.env['stock.picking'].search([
#                 ('date_done', '>=', self.from_date),
#                 ('date_done', '<=', self.to_date),
#                 ('location_id', '=', loc[0]),
#                 ('state', '=', 'done')
#             ])
#             _logger.info(f"Pickings from {self.from_date} location: {self.to_date}")
#
#         # If product_id is set, filter by that product
#         if self.product_id:
#             pickings = all_pickings.filtered(lambda p: self.product_id in p.move_lines.mapped('product_id'))
#             return pickings
#
#         return loc_pickings
#
#     def get_serial_numbers(self):
#         """Get serial numbers from matching pickings and return compressed range string."""
#         pickings = self.get_pditofg()
#         lots = []
#
#         for picking in pickings:
#             for move_line in picking.move_line_ids:
#                 if move_line.lot_id and move_line.lot_id.name:
#                     lots.append(move_line.lot_id.name)
#
#         return format_serial_numbers(lots)
#
#     def create_pditofg_report(self):
#         if not self.get_pditofg():
#             raise UserError(_('No transfers found for the selected criteria.'))
#         return self.env.ref('orion_pdi_to_fg.action_report_pditofg').report_action(self)
#
#
#
from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class PditofgReport(models.TransientModel):
    _name = "pditofg.report"
    _description = "PDI to FG Report"

    from_date = fields.Date('From', default=fields.Date.context_today)
    to_date = fields.Date('To', default=fields.Date.context_today)
    product_id = fields.Many2one('product.product', string='Product')

    def get_pditofg(self):
        IrConfigParam = self.env['ir.config_parameter'].sudo()

        td_manufactured_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_manufactured_location_id')
        td_fg_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_fg_location_id')

        if not td_manufactured_location_id:
            raise UserError(_('Please configure "Manufactured (PDI) Location" in inventory settings.'))
        if not td_fg_location_id:
            raise UserError(_('Please configure "FG Location" in inventory settings.'))

        # Convert string to integer
        td_manufactured_location_id = int(td_manufactured_location_id)
        td_fg_location_id = int(td_fg_location_id)

        # ✅ Search only transfers from PDI ➝ FG
        pickings = self.env['stock.picking'].search([
            ('date_done', '>=', self.from_date),
            ('date_done', '<=', self.to_date),
            ('location_id', '=', td_manufactured_location_id),
            ('location_dest_id', '=', td_fg_location_id),
            ('state', '=', 'done')
        ])

        _logger.info(f"Found {len(pickings)} pickings from PDI to FG between {self.from_date} and {self.to_date}")

        # If a specific product is selected, filter pickings to only include that product
        if self.product_id:
            pickings = pickings.filtered(lambda p: self.product_id in p.move_lines.mapped('product_id'))
            _logger.info(f"Filtered pickings by product: {self.product_id.display_name}, found {len(pickings)} pickings.")

        return pickings

    def get_serial_numbers(self):
        """Get serial numbers from matching pickings and return a formatted string (e.g., 1001-1005,1007)."""
        pickings = self.get_pditofg()
        lots = []

        for picking in pickings:
            for move_line in picking.move_line_ids:
                if move_line.lot_id and move_line.lot_id.name:
                    lots.append(move_line.lot_id.name)

        return format_serial_numbers(lots)

    def create_pditofg_report(self):
        pickings = self.get_pditofg()
        if not pickings:
            raise UserError(_('No transfers found for the selected criteria.'))

        return self.env.ref('orion_pdi_to_fg.action_report_pditofg').report_action(self)
