# from odoo import models, api
#
#
# class ReportDeliveryNote(models.AbstractModel):
#     _name = 'report.orion_delivery_challan_report.delivery_challan'
#     _description = 'Orion Delivery Challan Report'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['stock.picking'].browse(docids)
#         doc = docs and docs[0] or False
#         sale_order = False
#
#         if doc and doc.origin:
#             sale_order = self.env['sale.order'].search(
#                 [('name', '=', doc.origin)],
#                 limit=1
#             )
#
#         if not sale_order:
#             sale_order = self.env['sale.order'].new({
#                 'customer_po_number': '',
#                 'client_order_ref': '',
#                 'partner_id': False,
#                 'date_order': False,
#             })
#
#         move_lines = []
#         if doc:
#             for move_line in doc.move_line_ids:
#                 move_lines.append({
#                     'product': move_line.product_id,
#                     'quantity': move_line.qty_done,
#                     'uom': move_line.product_uom_id,
#                     'lot': move_line.lot_id.name if move_line.lot_id else '',
#                     'raw': move_line,  # include raw record for advanced usage
#                 })
#
#         return {
#             'doc_ids': docids,
#             'doc_model': 'stock.picking',
#             'docs': docs,
#             'doc': doc,
#             'sale_order': sale_order,
#             'move_lines': move_lines,
#             'get_serial_range': self.get_serial_range,  #  Expose the function here
#             'data': data,
#         }
#
#     def get_serial_range(self, move_lines):
#         """Return start to end serial number for move_lines."""
#         # Handle both recordsets and dicts (if needed)
#         lines = move_lines
#         if isinstance(move_lines, list) and isinstance(move_lines[0], dict) and 'raw' in move_lines[0]:
#             lines = [ml['raw'] for ml in move_lines]
#
#         serials = sorted(ml.lot_id.name for ml in lines if ml.lot_id)
#         if serials:
#             return f"{serials[0]} to {serials[-1]}" if len(serials) > 1 else serials[0]
#         return ''
from odoo import models, api


def format_serial_numbers(slist):
    numberlist = []

    # Convert serial numbers to tuples of (prefix, number part)
    for serial in slist:
        if not serial or len(serial) < 2:
            continue
        prefix = serial[0]
        try:
            number = int(serial[1:])
            numberlist.append((prefix, number))
        except ValueError:
            continue  # Skip if not a valid number

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

    return ', '.join([' TO '.join(block) for block in pagelist])


class ReportDeliveryNote(models.AbstractModel):
    _name = 'report.orion_delivery_challan_report.delivery_challan'
    _description = 'Orion Delivery Challan Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        doc = docs and docs[0] or False
        sale_order = False

        if doc and doc.origin:
            sale_order = self.env['sale.order'].search(
                [('name', '=', doc.origin)],
                limit=1
            )

        if not sale_order:
            sale_order = self.env['sale.order'].new({
                'customer_po_number': '',
                'client_order_ref': '',
                'partner_id': False,
                'date_order': False,
            })

        move_lines = []
        if doc:
            for move_line in doc.move_line_ids:
                move_lines.append({
                    'product': move_line.product_id,
                    'quantity': move_line.qty_done,
                    'uom': move_line.product_uom_id,
                    'lot': move_line.lot_id.name if move_line.lot_id else '',
                    'raw': move_line,  # include raw record for access in helper function
                })

        return {
            'doc_ids': docids,
            'doc_model': 'stock.picking',
            'docs': docs,
            'doc': doc,
            'sale_order': sale_order,
            'move_lines': move_lines,
            'data': data,
            'get_serial_range': self.get_serial_range,  # expose function to Py3O
        }

    def get_serial_range(self, move_lines):
        """Return formatted serial number range string."""
        lines = move_lines
        if isinstance(move_lines, list) and isinstance(move_lines[0], dict) and 'raw' in move_lines[0]:
            lines = [ml['raw'] for ml in move_lines]

        serials = [ml.lot_id.name for ml in lines if ml.lot_id and ml.lot_id.name]
        return format_serial_numbers(serials)
