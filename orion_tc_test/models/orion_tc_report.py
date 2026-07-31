# import re
# from odoo import models, fields, api
#
# def formatSerialNumbers(slist):
#     numberlist = []
#     for i in slist:
#         sno = int(re.sub('[^0-9]', '', i))  # Keep only digits
#         numberlist.append(sno)
#
#     pagelist = []
#     prev_number = None
#
#     for number, xnumber in zip(sorted(numberlist), sorted(slist)):
#         if prev_number is None or number != prev_number + 1:
#             pagelist.append([xnumber])
#         elif len(pagelist[-1]) > 1:
#             pagelist[-1][-1] = xnumber
#         else:
#             pagelist[-1].append(xnumber)
#         prev_number = number
#
#     return ', '.join([' TO '.join(page) for page in pagelist])
#
#
#
# class StockPicking(models.Model):
#     _inherit = 'stock.picking'
#
#     def action_print_test_certificate(self):
#         """Action to print test certificate"""
#         return self.env.ref('orion_tc_test.test_certificate_report').report_action(self)
#
#     # def get_serial_number_range(self):
#         # slist = []
#         # for move_line in self.move_line_ids:
#         #     for lot in move_line.lot_id:
#         #         if lot.name:
#         #             slist.append(lot.name)
#         # return formatSerialNumbers(slist) if slist else ''
#     def get_serial_number_range(self):
#         product_serials = {}
#
#         for move_line in self.move_line_ids:
#             product = move_line.product_id
#             lot = move_line.lot_id
#             if product and lot and lot.name:
#                 product_serials.setdefault(product, []).append(lot.name)
#
#         result_lines = []
#         for product, serial_list in product_serials.items():
#             formatted_range = formatSerialNumbers(serial_list)
#             result_lines.append(f"{product.display_name}: {formatted_range}")
#
#         return '\n'.join(result_lines) if result_lines else ''
#
#
# class TestCertificateReport(models.AbstractModel):
#     _name = 'report.orion_tc_test.report_test_certificate'
#     _description = 'Test Certificate Report'
#
#     @api.model
#     def _get_report_values(self, docids, data=None):
#         docs = self.env['stock.picking'].browse(docids)
#         return {
#             'doc_ids': docids,
#             'doc_model': 'stock.picking',
#             'docs': docs,
#             'company': self.env.company,
#             'get_serial_number_range':self.get_serial_number_range
#         }

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
    _name = 'report.orion_tc_test.testing'
    _description = 'Test Certificate Report'

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
