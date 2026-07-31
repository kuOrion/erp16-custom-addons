from odoo import models, api

class ReportDispatchNote(models.AbstractModel):
    _name = 'report.orion_invoice_report.packing_list'
    _description = 'Export Dispatch Note Report'

    def extract_invoice_number(self, invoice_name):
        """ Extracts the numeric part of the invoice number """
        return invoice_name.split('/')[-1] if invoice_name else ''

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        # Since we're processing a single document at a time in the template,
        # we can pass the sale_order directly like in the working version
        sale_order = False
        if docs:
            # Get the sale order for the first invoice
            sale_order = self.env['sale.order'].search(
                [('name', '=', docs[0].invoice_origin)],
                limit=1
            )

        return {
            'docs': docs,
            'sale_order': sale_order,  # Pass single sale_order instead of dictionary
            'extract_invoice_number': self.extract_invoice_number,  # Pass function to template
            'get_serial_ranges': self.get_serial_ranges,

        }

    def get_serial_ranges(self, line):
        serials = sorted(
            line.sale_line_ids.move_ids.move_line_ids.mapped('lot_id.name')
        )

        if not serials:
            return ''

        ranges = []
        start = serials[0]
        prev = serials[0]

        for serial in serials[1:]:
            prev_num = int(prev[1:])
            curr_num = int(serial[1:])

            if curr_num == prev_num + 1:
                prev = serial
            else:
                if start == prev:
                    ranges.append(start)
                else:
                    ranges.append(f"{start} TO {prev}")
                start = prev = serial

        if start == prev:
            ranges.append(start)
        else:
            ranges.append(f"{start} TO {prev}")

        return ', '.join(ranges)