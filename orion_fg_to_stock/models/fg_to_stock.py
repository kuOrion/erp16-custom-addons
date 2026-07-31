from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)
def format_serial_numbers(slist):
    """Convert a list of serial numbers into compressed ranges like A2508001 TO A2508004."""
    numberlist = []
    for serial in slist:
        if not serial or len(serial) < 2:
            continue
        prefix = serial[0]
        try:
            number = int(serial[1:])
            numberlist.append((prefix, number))
        except ValueError:
            continue

    pagelist = []
    prev_number = None
    prev_prefix = None
    for prefix, number in sorted(numberlist, key=lambda x: x[1]):
        full_serial = f"{prefix}{number}"
        if prev_number is None or number != prev_number + 1 or prefix != prev_prefix:
            pagelist.append([full_serial])
        elif len(pagelist[-1]) > 1:
            pagelist[-1][-1] = full_serial
        else:
            pagelist[-1].append(full_serial)
        prev_number = number
        prev_prefix = prefix

    return ', '.join([' TO '.join(rng) for rng in pagelist])


class FGToStockReport(models.TransientModel):
    _name = "fgtostock.report"
    _description = "FG to Stock Report"

    from_date = fields.Date('From', default=fields.Date.today)
    to_date = fields.Date('To', default=fields.Date.today)
    product_id = fields.Many2one('product.product', string='Product')

    def get_fgtostock(self):
        IrConfigParam = self.env['ir.config_parameter'].sudo()
        td_fg_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_fg_location_id')
        td_stock_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_stock_location_id')

        if not td_fg_location_id or not td_stock_location_id:
            raise UserError(_('Please configure "Route Transfer Locations" from Inventory > Settings menu!'))

        move_ids = self.env['stock.picking'].search([
            ('date_done', '>=', self.from_date),
            ('date_done', '<=', self.to_date),
            ('location_id', '=', int(td_fg_location_id)),
            ('location_dest_id', '=', int(td_stock_location_id)),
            ('state', '=', 'done')
        ])

        return move_ids

    def get_serial_numbers(self):
        """Get serial numbers from pickings and return compressed string."""
        pickings = self.get_fgtostock()
        lots = []
        for picking in pickings:
            for move_line in picking.move_line_ids:
                if move_line.lot_id and move_line.lot_id.name:
                    lots.append(move_line.lot_id.name)
        return format_serial_numbers(lots)

    def create_fgtostock_report(self):
        return self.env.ref('orion_fg_to_stock.action_report_fgtostock').report_action(self)
