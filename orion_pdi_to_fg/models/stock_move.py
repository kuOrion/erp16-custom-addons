from odoo import models
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

class StockMove(models.Model):
    _inherit = 'stock.move'

    def get_serial_numbers(self):
        """Get serial numbers for this move and return compressed range string."""

        lots = []
        for move_line in self.move_line_ids:
            if move_line.lot_id and move_line.lot_id.name:
                lots.append(move_line.lot_id.name)

        return format_serial_numbers(lots)