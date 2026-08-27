from odoo import models, api, fields
from odoo.exceptions import ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'


    def _action_assign(self, force_qty=False):
        """
        Override to allow partial assignment when stock is less.
        Now respects existing reservations (no auto-unreserve).
        Works for multiple products in the same picking.
        """

        # First run the normal Odoo reservation
        res = super(StockMove, self)._action_assign(force_qty=force_qty)

        # Then apply custom partial reservation logic
        for move in self:
            if move.picking_id and move.picking_id.sale_id:

                if move.product_id.tracking == 'serial' and move.product_uom_qty > move.reserved_availability:
                    self._force_partial_reservation(move)

        return res

    def _force_partial_reservation(self, move):
        """
        Force reservation of available serials but never exceed demand quantity.
        Only reserve what is available in the move's source location.
        """
        available_quants = self.env['stock.quant'].search([
            ('product_id', '=', move.product_id.id),
            ('location_id', '=', move.location_id.id),  # restrict to source location
            ('lot_id', '!=', False),
            ('quantity', '>', 0),
        ])

        already_reserved = move.move_line_ids.mapped('lot_id.id')
        free_quants = available_quants.filtered(lambda q: q.lot_id.id not in already_reserved)

        already_reserved_qty = sum(move.move_line_ids.mapped('reserved_uom_qty'))
        qty_needed = max(move.product_uom_qty - already_reserved_qty, 0)

        for quant in free_quants:
            if qty_needed <= 0:
                break

            # Find or create a move line without lot_id
            move_line = move.move_line_ids.filtered(lambda ml: not ml.lot_id)[:1]
            if not move_line:
                move_line = self.env['stock.move.line'].create({
                    'move_id': move.id,
                    'product_id': move.product_id.id,
                    'product_uom_id': move.product_uom.id,
                    'location_id': move.location_id.id,
                    'location_dest_id': move.location_dest_id.id,
                    'picking_id': move.picking_id.id,
                    'reserved_uom_qty': 0,
                    'qty_done': 0,
                })

            move_line.lot_id = quant.lot_id.id
            move_line.reserved_uom_qty = 1
            qty_needed -= 1

        # Safety check: do not exceed demand
        total_reserved = sum(move.move_line_ids.mapped('reserved_uom_qty'))
        if total_reserved > move.product_uom_qty:
            excess = total_reserved - move.product_uom_qty
            for ml in reversed(move.move_line_ids.sorted('id')):
                if excess <= 0:
                    break
                if ml.reserved_uom_qty > 0:
                    reduce_qty = min(excess, ml.reserved_uom_qty)
                    ml.reserved_uom_qty -= reduce_qty
                    excess -= reduce_qty

    @api.model
    def _action_done(self, cancel_backorder=False):
        """
        Auto-fill qty_done = reserved_uom_qty ONLY when user has not set qty_done manually.
        """
        for move in self:
            manual_qty_done = sum(move.move_line_ids.mapped('qty_done'))
            if manual_qty_done == 0:
                for ml in move.move_line_ids:
                    if ml.reserved_uom_qty:
                        ml.qty_done = ml.reserved_uom_qty
        return super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)

    # ---------------------------
    # MANUAL PRIORITIZATION LOGIC
    # ---------------------------
    def action_check_availability_priority(self):
        """
        Check availability and prioritize current serial number.
        Unreserves other moves for the same product and reserves selected serial for this move.
        This is called when "Check Availability" button is clicked in the form.
        """
        for move in self:
            if not move.product_id or move.product_id.tracking != 'serial':
                continue

            # Get all move lines with selected serials for this move
            selected_move_lines = move.move_line_ids.filtered(lambda ml: ml.lot_id)

            if not selected_move_lines:
                continue

            # Get all other moves for the same product that have reserved stock
            conflicting_moves = self.env['stock.move'].search([
                ('product_id', '=', move.product_id.id),
                ('state', 'in', ['assigned', 'partially_available']),
                ('id', '!=', move.id),
            ])

            # Unreserve all conflicting moves
            for conf_move in conflicting_moves:
                conf_move._do_unreserve()

            # Clear and rebuild reservations for current move with selected serials
            move.move_line_ids.filtered(lambda ml: not ml.lot_id).unlink()

            # Re-assign stock for current move - this will now get the selected serials
            move._action_assign(force_qty=True)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    @api.onchange('product_id', 'location_id')
    def _onchange_product_id_lot_domain(self):
        """
        Show all lot/serials of the product in the source location that have quantity > 0.
        This includes all old and new serials available in stock.
        """
        if self.product_id and self.location_id:
            # Get all quants for this product in this location
            available_quants = self.env['stock.quant'].search([
                ('product_id', '=', self.product_id.id),
                ('location_id', '=', self.location_id.id),
                ('lot_id', '!=', False),
            ])

            # Get all lot IDs that have quantity > 0 (both old and new)
            valid_lots = available_quants.filtered(lambda q: q.quantity > 0).mapped('lot_id').ids

            return {'domain': {'lot_id': [('id', 'in', valid_lots)]}}
        else:
            return {'domain': {'lot_id': []}}

    @api.onchange('lot_id')
    def _onchange_lot_id(self):
        """
        Allow manual change of serial number (lot_id).
        Ensure qty_done = 1 when a serial is selected.
        Accept ANY serial that exists in stock.
        """
        if self.lot_id and self.qty_done == 0:
            self.qty_done = 1

    @api.onchange('qty_done')
    def _onchange_qty_done(self):
        """
        When qty_done is updated manually, manage move lines based on the done quantity.
        """
        if self.move_id.product_id.tracking != 'serial':
            return

        move = self.move_id

        # Calculate total qty_done across all move lines
        total_qty_done = sum(move.move_line_ids.mapped('qty_done'))

        # If total qty_done exceeds demand, truncate
        if total_qty_done > move.product_uom_qty:
            return

        # Update reserved_uom_qty based on qty_done
        if self.qty_done > 0:
            self.reserved_uom_qty = self.qty_done
        else:
            self.reserved_uom_qty = 0

    def _synchronize_lines(self):
        """
        Synchronize move lines so only done quantity lines are kept.
        Called before confirming delivery.
        """
        move = self.move_id

        if move.product_id.tracking != 'serial':
            return

        total_qty_done = sum(move.move_line_ids.mapped('qty_done'))

        # Remove lines with qty_done = 0
        lines_to_delete = move.move_line_ids.filtered(lambda ml: ml.qty_done == 0)
        lines_to_delete.unlink()

        # Update reserved_uom_qty to match qty_done for remaining lines
        for line in move.move_line_ids:
            if line.qty_done > 0:
                line.reserved_uom_qty = line.qty_done

    @api.constrains('qty_done')
    def _check_qty_done_limit(self):
        """
        Ensure qty_done doesn't exceed the move demand.
        Allow ANY serial that exists in stock.
        """
        for line in self:
            move = line.move_id
            if move.product_id.tracking == 'serial':
                # Check total quantity doesn't exceed demand
                total_done = sum(move.move_line_ids.mapped('qty_done'))
                if total_done > move.product_uom_qty:
                    raise ValidationError(
                        f"Total done quantity ({total_done}) cannot exceed "
                        f"demand quantity ({move.product_uom_qty})"
                    )

    def _is_serial_available_in_stock(self):
        """
        Check if the selected serial number exists in the source location with quantity > 0.
        Returns True if the serial is in stock, False otherwise.
        This allows ANY serial (old or new) to be delivered if it exists in stock.
        """
        if not self.lot_id or not self.product_id:
            return False

        # Get the source location
        location_id = self.location_id.id if self.location_id else (
            self.move_id.location_id.id if self.move_id else False)

        if not location_id:
            return False

        # Check if this serial exists in the source location with quantity > 0
        available_quant = self.env['stock.quant'].search([
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', location_id),
            ('lot_id', '=', self.lot_id.id),
        ], limit=1)

        # Return True if serial exists and has quantity in stock
        if available_quant and available_quant.quantity > 0:
            return True

        return False