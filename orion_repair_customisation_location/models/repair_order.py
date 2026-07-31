#
# # -*- coding: utf-8 -*-
# from odoo import models, fields, api
# from odoo.exceptions import UserError
#
#
# class RepairOrder(models.Model):
#     _inherit = 'repair.order'
#
#     # Dispatch location tracking
#     dispatch_location_id = fields.Many2one(
#         'stock.location',
#         string='Dispatch Location',
#         help='Location from where the product is dispatched'
#     )
#     dispatch_date = fields.Datetime(
#         string='Dispatch Date',
#         help='Date when product was dispatched'
#     )
#
#     # Warehouse location tracking
#     warehouse_location_id = fields.Many2one(
#         'stock.location',
#         string='Warehouse Location',
#         help='Location where the product is received in warehouse'
#     )
#     warehouse_received_date = fields.Datetime(
#         string='Warehouse Received Date',
#         help='Date when product was received in warehouse'
#     )
#
#     # Return to dispatch tracking
#     return_dispatch_date = fields.Datetime(
#         string='Return to Dispatch Date',
#         help='Date when product was returned to dispatch location after repair'
#     )
#
#     # Status field to track movement
#     location_status = fields.Selection([
#         ('draft', 'Draft'),
#         ('dispatched', 'Dispatched'),
#         ('received', 'Received in Warehouse'),
#         ('returned', 'Returned to Dispatch'),
#     ], string='Location Status', default='draft', tracking=True)
#
#     def action_set_dispatched(self):
#         """Mark the product as dispatched"""
#         for repair in self:
#             if not repair.dispatch_location_id:
#                 raise UserError('Please set the Dispatch Location first!')
#
#             repair.write({
#                 'dispatch_date': fields.Datetime.now(),
#                 'location_status': 'dispatched'
#             })
#
#         return True
#
#     def action_receive_in_warehouse(self):
#         """Mark the product as received in warehouse"""
#         for repair in self:
#             if repair.location_status != 'dispatched':
#                 raise UserError('Product must be dispatched first!')
#             if not repair.warehouse_location_id:
#                 raise UserError('Please set the Warehouse Location first!')
#
#             # Create stock move for the transfer
#             stock_move_vals = {
#                 'name': f'Repair Transfer: {repair.name}',
#                 'product_id': repair.product_id.id,
#                 'product_uom': repair.product_uom.id,
#                 'product_uom_qty': repair.product_qty,
#                 'location_id': repair.dispatch_location_id.id,
#                 'location_dest_id': repair.warehouse_location_id.id,
#                 'repair_id': repair.id,
#             }
#
#             stock_move = self.env['stock.move'].create(stock_move_vals)
#             stock_move._action_confirm()
#             stock_move._action_assign()
#
#             # Set quantities and validate
#             for move_line in stock_move.move_line_ids:
#                 move_line.qty_done = move_line.reserved_uom_qty
#
#             stock_move._action_done()
#
#             # Update repair order fields - only set warehouse received date
#             repair.write({
#                 'warehouse_received_date': fields.Datetime.now(),
#                 'location_status': 'received'
#             })
#
#         return True
#
#     def action_transfer_to_dispatch(self):
#         """Transfer repaired product back to dispatch location and create invoice"""
#         for repair in self:
#             # Check if repair is completed
#             if repair.state not in ['done', 'ready']:
#                 raise UserError('Repair must be completed before transferring back to dispatch!')
#
#             if repair.location_status != 'received':
#                 raise UserError('Product must be received in warehouse first!')
#
#             if not repair.warehouse_location_id:
#                 raise UserError('Warehouse Location is not set!')
#
#             if not repair.dispatch_location_id:
#                 raise UserError('Dispatch Location is not set!')
#
#             # Check if already transferred
#             if repair.return_dispatch_date:
#                 raise UserError('Product has already been transferred to dispatch!')
#
#             # Create stock move for return transfer
#             stock_move_vals = {
#                 'name': f'Repair Return Transfer: {repair.name}',
#                 'product_id': repair.product_id.id,
#                 'product_uom': repair.product_uom.id,
#                 'product_uom_qty': repair.product_qty,
#                 'location_id': repair.warehouse_location_id.id,
#                 'location_dest_id': repair.dispatch_location_id.id,
#                 'repair_id': repair.id,
#             }
#
#             stock_move = self.env['stock.move'].create(stock_move_vals)
#             stock_move._action_confirm()
#             stock_move._action_assign()
#
#             # Set quantities and validate
#             for move_line in stock_move.move_line_ids:
#                 move_line.qty_done = move_line.reserved_uom_qty
#
#             stock_move._action_done()
#
#             # Update repair order fields FIRST
#             repair.write({
#                 'return_dispatch_date': fields.Datetime.now(),
#                 'location_status': 'returned'
#             })
#
#             # Force update to ensure changes are committed
#             self.env.cr.commit()
#
#             # Create invoice if not already invoiced
#             if repair.invoice_method != 'none' and not repair.invoice_id:
#                 try:
#                     repair.action_repair_invoice_create()
#                     invoice_created = True
#                     invoice_msg = 'Product transferred and invoice created successfully.'
#                 except Exception as e:
#                     invoice_created = False
#                     invoice_msg = f'Product transferred successfully but invoice creation failed: {str(e)}'
#             else:
#                 invoice_created = False
#                 if repair.invoice_id:
#                     invoice_msg = 'Product transferred successfully. Invoice already exists.'
#                 else:
#                     invoice_msg = 'Product transferred successfully. No invoice method configured.'
#
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'display_notification',
#             'params': {
#                 'title': 'Success',
#                 'message': invoice_msg,
#                 'type': 'success' if invoice_created or repair.invoice_id else 'warning',
#                 'sticky': False,
#                 'next': {'type': 'ir.actions.act_window_close'},
#             }
#         }
#
#
# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     repair_id = fields.Many2one(
#         'repair.order',
#         string='Repair Order',
#         help='Related repair order for this stock move'
#     )


# from odoo import models, fields, api
# from odoo.exceptions import UserError
#
#
# class RepairOrder(models.Model):
#     _inherit = 'repair.order'
#
#     dispatch_location_id = fields.Many2one(
#         'stock.location',
#         string='Dispatch Location',
#         default=lambda self: self.env['stock.location'].search(
#             [('complete_name', '=', 'WH/Dispatch')], limit=1
#         ),
#         help='Location from where the product is dispatched'
#     )
#
#     dispatch_date = fields.Datetime(string='Dispatch Date')
#
#     warehouse_location_id = fields.Many2one(
#         'stock.location',
#         string='Warehouse Location',
#         default=lambda self: self.env['stock.location'].search(
#             [('complete_name', '=', 'WH/Workshop')], limit=1
#         ),
#         help='Location where the product is received in warehouse'
#     )
#
#     warehouse_received_date = fields.Datetime(string='Warehouse Received Date')
#
#     # Return to dispatch tracking
#     return_dispatch_date = fields.Datetime(string='Return to Dispatch Date')
#
#     # Receive in dispatch tracking
#     received_in_dispatch_date = fields.Datetime(string='Received in Dispatch Date')
#
#     # Status field to track movement
#     location_status = fields.Selection([
#         ('draft', 'Draft'),
#         ('dispatched', 'Dispatched to Warehouse'),
#         ('received', 'Received in Warehouse'),
#         ('returned', 'In Transit to Dispatch'),
#         ('received_dispatch', 'Received in Dispatch'),
#         ('completed', 'Invoice Created'),
#     ], string='Location Status', default='draft', tracking=True)
#
#     def _reload_view(self):
#         """Helper method to reload the current view"""
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'reload',
#         }
#
#     def action_set_dispatched(self):
#         """Step 1: Mark the product as dispatched"""
#         for repair in self:
#             if not repair.dispatch_location_id:
#                 raise UserError('Please set the Dispatch Location first!')
#
#             repair.write({
#                 'dispatch_date': fields.Datetime.now(),
#                 'location_status': 'dispatched'
#             })
#
#         # Return reload action
#         return self._reload_view()
#
#     def action_receive_in_warehouse(self):
#         """Step 2: Mark the product as received in warehouse"""
#         for repair in self:
#             if repair.location_status != 'dispatched':
#                 raise UserError('Product must be dispatched first!')
#             if not repair.warehouse_location_id:
#                 raise UserError('Please set the Warehouse Location first!')
#
#             # Create stock move
#             stock_move = self.env['stock.move'].create({
#                 'name': f'Repair Transfer: {repair.name}',
#                 'product_id': repair.product_id.id,
#                 'product_uom': repair.product_uom.id,
#                 'product_uom_qty': repair.product_qty,
#                 'location_id': repair.dispatch_location_id.id,
#                 'location_dest_id': repair.warehouse_location_id.id,
#                 'repair_id': repair.id,
#             })
#             stock_move._action_confirm()
#             stock_move._action_assign()
#             for move_line in stock_move.move_line_ids:
#                 move_line.qty_done = move_line.reserved_uom_qty
#             stock_move._action_done()
#
#             repair.write({
#                 'warehouse_received_date': fields.Datetime.now(),
#                 'location_status': 'received'
#             })
#
#         # Return reload action
#         return self._reload_view()
#
#     def action_transfer_to_dispatch(self):
#         """Step 3: Transfer repaired product back to dispatch location"""
#         for repair in self:
#             if repair.location_status != 'received':
#                 raise UserError('Product must be received in warehouse first!')
#             if not repair.warehouse_location_id:
#                 raise UserError('Warehouse Location is not set!')
#             if not repair.dispatch_location_id:
#                 raise UserError('Dispatch Location is not set!')
#             if repair.return_dispatch_date:
#                 raise UserError('Product has already been transferred to dispatch!')
#
#             # Create stock move for return
#             stock_move = self.env['stock.move'].create({
#                 'name': f'Repair Return: {repair.name}',
#                 'product_id': repair.product_id.id,
#                 'product_uom': repair.product_uom.id,
#                 'product_uom_qty': repair.product_qty,
#                 'location_id': repair.warehouse_location_id.id,
#                 'location_dest_id': repair.dispatch_location_id.id,
#                 'repair_id': repair.id,
#             })
#             stock_move._action_confirm()
#             stock_move._action_assign()
#             for move_line in stock_move.move_line_ids:
#                 move_line.qty_done = move_line.reserved_uom_qty
#             stock_move._action_done()
#
#             repair.write({
#                 'return_dispatch_date': fields.Datetime.now(),
#                 'location_status': 'returned'
#             })
#
#         # Return reload action instead of just notification
#         return self._reload_view()
#
#     def action_receive_in_dispatch(self):
#         """Step 4: Receive product at dispatch"""
#         for repair in self:
#             if repair.location_status != 'returned':
#                 raise UserError('Product must be transferred to dispatch first!')
#             if repair.received_in_dispatch_date:
#                 raise UserError('Product already received in dispatch!')
#
#             # Update status - don't create invoice yet
#             repair.write({
#                 'received_in_dispatch_date': fields.Datetime.now(),
#                 'location_status': 'received_dispatch'
#             })
#
#         # Return reload action
#         return self._reload_view()
#
#     def action_create_invoice(self):
#         """Step 5: Create invoice after receiving in dispatch"""
#         for repair in self:
#             if repair.location_status != 'received_dispatch':
#                 raise UserError('Product must be received in dispatch first!')
#             if repair.invoice_id:
#                 raise UserError('Invoice already exists!')
#
#             # Create invoice
#             try:
#                 # Save original invoice method
#                 original_method = repair.invoice_method
#                 if repair.invoice_method == 'none':
#                     repair.invoice_method = 'after_repair'
#
#                 # Create invoice
#                 repair.action_repair_invoice_create()
#
#                 # Restore original method
#                 if original_method == 'none':
#                     repair.invoice_method = original_method
#
#                 # Update status to completed
#                 repair.write({
#                     'location_status': 'completed'
#                 })
#
#             except Exception as e:
#                 raise UserError(f'Invoice creation failed: {str(e)}')
#
#         # Return reload action
#         return self._reload_view()
#
#
# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     repair_id = fields.Many2one('repair.order', string='Repair Order')



from odoo import models, fields, api
from odoo.exceptions import UserError


class RepairOrder(models.Model):
    _inherit = 'repair.order'

    # -------------------------
    # Locations & Dates
    # -------------------------
    dispatch_location_id = fields.Many2one(
        'stock.location',
        string='Dispatch Location',
        default=lambda self: self.env['stock.location'].search(
            [('complete_name', '=', 'WH/Dispatch')], limit=1
        ),
    )

    warehouse_location_id = fields.Many2one(
        'stock.location',
        string='Warehouse Location',
        default=lambda self: self.env['stock.location'].search(
            [('complete_name', '=', 'WH/Workshop')], limit=1
        ),
    )

    dispatch_date = fields.Datetime()
    warehouse_received_date = fields.Datetime()
    return_dispatch_date = fields.Datetime()
    received_in_dispatch_date = fields.Datetime()

    # -------------------------
    # Default Repair Location
    # -------------------------
    location_id = fields.Many2one(
        'stock.location',
        default=lambda self: self.env['stock.location'].search(
            [('complete_name', '=', 'WH/Dispatch')], limit=1
        ),
    )

    # -------------------------
    # Status Tracking
    # -------------------------
    location_status = fields.Selection([
        ('draft', 'Draft'),
        ('dispatched', 'Dispatched to Warehouse'),
        ('received', 'Received in Warehouse'),
        ('returned', 'Returned to Dispatch'),
        ('received_dispatch', 'Received in Dispatch'),
        ('completed', 'Invoice Created'),
    ], default='draft', tracking=True)

    # =========================================================
    # HELPERS
    # =========================================================
    def _reload_view(self):
        return {'type': 'ir.actions.client', 'tag': 'reload'}

    def _get_internal_picking_type(self):
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'internal')
        ], limit=1)

        if not picking_type:
            raise UserError('Internal Picking Type not found!')
        return picking_type

    # def _create_internal_transfer(self, source, dest):
    #     self.ensure_one()
    #
    #     picking_type = self._get_internal_picking_type()
    #
    #     picking = self.env['stock.picking'].create({
    #         'picking_type_id': picking_type.id,
    #         'location_id': source.id,
    #         'location_dest_id': dest.id,
    #         'origin': self.name,
    #     })
    #
    #     move = self.env['stock.move'].create({
    #         'name': self.product_id.display_name,
    #         'product_id': self.product_id.id,
    #         'product_uom': self.product_uom.id,
    #         'product_uom_qty': self.product_qty,
    #         'location_id': source.id,
    #         'location_dest_id': dest.id,
    #         'picking_id': picking.id,
    #         'repair_id': self.id,
    #     })
    #
    #     picking.action_confirm()
    #     picking.action_assign()
    #
    #     for line in picking.move_line_ids:
    #         line.qty_done = line.reserved_uom_qty
    #
    #         # LOT / SERIAL HANDLING
    #         if self.product_id.tracking != 'none':
    #             if not self.lot_id:
    #                 raise UserError('This product requires a Lot/Serial Number!')
    #             line.lot_id = self.lot_id
    #
    #     picking.button_validate()
    def _create_internal_transfer(self, source, dest):
        self.ensure_one()

        picking_type = self._get_internal_picking_type()

        picking = self.env['stock.picking'].create({
            'picking_type_id': picking_type.id,
            'location_id': source.id,
            'location_dest_id': dest.id,
            'origin': self.name,
        })

        move = self.env['stock.move'].create({
            'name': self.product_id.display_name,
            'product_id': self.product_id.id,
            'product_uom': self.product_uom.id,
            'product_uom_qty': self.product_qty,
            'location_id': source.id,
            'location_dest_id': dest.id,
            'picking_id': picking.id,
            'repair_id': self.id,
        })

        picking.action_confirm()

        # 🔑 CREATE MOVE LINE WITH DONE QTY
        move_line_vals = {
            'move_id': move.id,
            'picking_id': picking.id,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'qty_done': self.product_qty,
            'location_id': source.id,
            'location_dest_id': dest.id,
        }

        # LOT / SERIAL HANDLING
        if self.product_id.tracking != 'none':
            if not self.lot_id:
                raise UserError('This product requires a Lot/Serial Number!')
            move_line_vals['lot_id'] = self.lot_id.id

        self.env['stock.move.line'].create(move_line_vals)

        picking.button_validate()

    # =========================================================
    # BUTTON ACTIONS
    # =========================================================
    def action_set_dispatched(self):
        for rec in self:
            rec.write({
                'dispatch_date': fields.Datetime.now(),
                'location_status': 'dispatched',
            })
        return self._reload_view()

    def action_receive_in_warehouse(self):
        for rec in self:
            if rec.location_status != 'dispatched':
                raise UserError('Product must be dispatched first!')

            rec._create_internal_transfer(
                rec.dispatch_location_id,
                rec.warehouse_location_id
            )

            rec.write({
                'warehouse_received_date': fields.Datetime.now(),
                'location_status': 'received',
                'location_id': rec.warehouse_location_id.id,
            })
        return self._reload_view()

    def action_transfer_to_dispatch(self):
        for rec in self:
            if rec.location_status != 'received':
                raise UserError('Product must be received in warehouse first!')

            rec._create_internal_transfer(
                rec.warehouse_location_id,
                rec.dispatch_location_id
            )

            rec.write({
                'return_dispatch_date': fields.Datetime.now(),
                'location_status': 'returned',
            })
        return self._reload_view()

    def action_receive_in_dispatch(self):
        for rec in self:
            if rec.location_status != 'returned':
                raise UserError('Product must be returned to dispatch first!')

            rec.write({
                'received_in_dispatch_date': fields.Datetime.now(),
                'location_status': 'received_dispatch',
                'location_id': rec.dispatch_location_id.id,
            })
        return self._reload_view()

    def action_create_invoice(self):
        for rec in self:
            if rec.location_status != 'received_dispatch':
                raise UserError('Product must be received in dispatch first!')
            if rec.invoice_id:
                raise UserError('Invoice already exists!')

            original_method = rec.invoice_method
            if rec.invoice_method == 'none':
                rec.invoice_method = 'after_repair'

            rec.action_repair_invoice_create()

            if original_method == 'none':
                rec.invoice_method = original_method

            rec.write({'location_status': 'completed'})

        return self._reload_view()


class StockMove(models.Model):
    _inherit = 'stock.move'

    repair_id = fields.Many2one('repair.order', string='Repair Order')
