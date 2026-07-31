from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class MfgDoneReport(models.AbstractModel):
    _name = "report.orion_manufacturing_done_report.mfgdone_report"
    _description = "Manufacturing Done Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['mrp.production'].browse(docids)
        result = []
        for mo in docs:
            # Only include produced lines with serials
            done_lines = mo.move_line_ids.filtered(lambda l: l.state == 'done' and l.lot_id)

            serial_numbers = sorted(done_lines.mapped('lot_id.name'))
            total_qty = sum(done_lines.mapped('qty_done'))

            if len(serial_numbers) > 1:
                serial_range = f"{serial_numbers[0]} TO {serial_numbers[-1]}"
            elif serial_numbers:
                serial_range = serial_numbers[0]
            else:
                serial_range = ""

            _logger.info(
                "MO %s | Serials: %s | Qty: %s",
                mo.name, serial_numbers, total_qty
            )

            result.append({
                'mo_name': mo.name,
                'product': mo.product_id.display_name,
                'serial_range': serial_range,
                'serial_list': serial_numbers,
                'qty_done': total_qty,
                'sale_order': mo.origin,
            })

        return {
            'doc_ids': docids,
            'doc_model': 'mrp.production',
            'docs': result,
        }
