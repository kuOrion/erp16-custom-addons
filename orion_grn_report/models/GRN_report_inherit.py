from odoo import models


class ReportStockPicking(models.AbstractModel):
    _name = 'report.orion_grn_report.testing_grn'

    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)

        # Process move lines with indexes
        processed_docs = []
        for doc in docs:
            move_lines = []
            for index, move in enumerate(doc.move_ids_without_package, 1):
                move_lines.append({
                    'index': index,
                    # 'description': move.description_picking or move.product_id.name,
                    'specification': move.product_id.default_code or '',
                    'unit': move.product_uom.name or '',
                    'po_qty': move.product_uom_qty or 0.0,
                    'received_qty': move.quantity_done or 0.0,
                    'accepted_qty': move.quantity_done or 0.0,  # Or use your logic here
                    'rejected_qty': 0.0,  # Or use your logic here
                    'rejection_reason': '',  # Or use your logic here
                })

            processed_docs.append({
                'picking': doc,
                'move_lines': move_lines,
            })

        return {
            'docs': docs,
            'processed_docs': processed_docs,
            # 'description_picking': docs.mapped('description_picking'),
            'supplier_challan_date': docs.mapped('supplier_challan_date'),
            'supplier_challan_no': docs.mapped('supplier_challan_no'),
            'get_grn_no': docs.get_grn_no,
        }
