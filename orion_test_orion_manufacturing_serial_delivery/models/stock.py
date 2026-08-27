from odoo import models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        """
        Fix over-reservations before validating older sale orders.
        """
        for picking in self:
            for move in picking.move_ids_without_package:
                # Clean up reservations that no longer exist in stock
                self._sync_reservations(move)

        return super(StockPicking, self).button_validate()

    def _sync_reservations(self, move):
        """
        Ensure reserved qty and stock availability match.
        Remove over-reservations or ghost move lines.
        """
        Quant = self.env['stock.quant']

        for ml in move.move_line_ids:
            available = Quant._get_available_quantity(
                ml.product_id,
                ml.location_id,
                lot_id=ml.lot_id
            )

            # If reserved but nothing left in stock for that lot, unreserve it
            if ml.reserved_uom_qty > available:
                ml.unlink()

        # Re-reserve cleanly what is available
        move._do_unreserve()
        move._action_assign()
