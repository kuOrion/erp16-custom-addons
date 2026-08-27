# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, _, fields, api
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.tools.misc import OrderedSet, format_date, groupby as tools_groupby

class StockMove(models.Model):
    _inherit = 'stock.move'

    start_lot_id = fields.Many2one('stock.lot', string='Start Serial Number')
    end_lot_id = fields.Many2one('stock.lot', string='End Serial Number')
    mo_lot_ids = fields.Many2many('stock.lot', string='Serial Numbers', compute='_compute_mo_lot_ids')
    # Related only so views can hide Start/End Serial on Sale Delivery
    # (outgoing) while keeping them on Internal Transfers. Does not change
    # reservation / assign logic. sh_ prefix = Softhealer technical field.
    sh_picking_type_code = fields.Selection(
        related='picking_type_id.code',
        string='Type of Operation',
        readonly=True,
    )

    def _compute_mo_lot_ids(self):
        for record in self:
            record.mo_lot_ids = []
            if record.picking_id:
                if record.picking_id.sh_source_mo_id:
                    lot_ids = record.picking_id.sh_source_mo_id.lot_ids
                    record.mo_lot_ids = [(6, 0, lot_ids.ids)]
                elif record.picking_id.sh_internal_picking_id:
                    lot_ids = record.picking_id.sh_internal_picking_id.move_ids.mapped('move_line_ids.lot_id')
                    record.mo_lot_ids = [(6, 0, lot_ids.ids)]

    # sh_source_mo_id = fields.Many2one('sh.finished.product', string='Source Document')
    # sh_source_mo_ids = fields.Many2many('sh.finished.product', string='Source Document',
    #     compute='_compute_sh_source_mo_ids' )
    # sh_internal_picking_id = fields.Many2one('stock.picking', string='Internal Picking')
    # sh_internal_picking_ids = fields.Many2many('stock.picking', string='Internal Picking',
    #     compute='_compute_sh_internal_picking_ids' )
    # sh_select_all_move_line = fields.Boolean(string='Select All Lines', default=False)
    
    # @api.onchange('sh_select_all_move_line')
    # def _onchange_sh_select_all_move_line(self):
    #     for record in self:
    #         if record.move_line_ids and record.sh_select_all_move_line == True:
    #             for line in record.move_line_ids:
    #                 line.sh_select_record = True
    #                 line._onchange_sh_select_record()
    #         else:   
    #             for line in record.move_line_ids:
    #                 line.sh_select_record = False
    #                 line._onchange_sh_select_record()

    # def _compute_sh_source_mo_ids(self):
        # for record in self:
        #     record.sh_source_mo_ids = []
        #     mo_record = self.env['mrp.production'].search([('location_dest_id','=',record.picking_id.location_id.id),
        #                                                 ('product_id','=',record.product_id.id),
        #                                                 ('sh_main_mo', '=', True),
        #                                                 ('state','=','done')])
        #     if mo_record:
        #         finish_product = self.env['sh.finished.product'].search([('production_id','in',mo_record.ids)])
        #         record.sh_source_mo_ids = [(6, 0, finish_product.ids)]
    
    # def _compute_sh_internal_picking_ids(self):
    #     for record in self:
    #         record.sh_internal_picking_ids = []
    #         picking_record = self.env['stock.picking'].search([('location_dest_id','=',record.picking_id.location_id.id),
    #                                                     ('product_id','=',record.product_id.id),
    #                                                     ('state','=','done')])
    #         if picking_record:
    #             record.sh_internal_picking_ids = [(6, 0, picking_record.ids)]

    def sh_action_update_move_line(self):
        # UI hides this on Sale Delivery; keep a server-side guard so the
        # range filter cannot be forced on non-internal operations.
        if self.sh_picking_type_code and self.sh_picking_type_code != 'internal':
            raise UserError(_(
                "Start/End Serial Number filtering is only available on Internal Transfers."))
        start_lot = self.start_lot_id
        end_lot = self.end_lot_id
        if not start_lot or not end_lot:
            raise UserError("Both Start Lot and End Lot must be set")
        if start_lot.id > end_lot.id:
            raise UserError("Start Lot must be less than or equal to End Lot")
        for record in self.move_line_ids:

            if not (record.lot_id and start_lot.id <= record.lot_id.id <= end_lot.id):
                record.unlink()
        return True
    # @api.onchange('sh_source_mo_id')
    # def _onchange_sh_source_mo_id(self):
    #     """ This will set the serial number to the move line based on the selected source document."""
    #     print("\n\n\ncalled")
    #     for record in self:
    #         record._do_unreserve()
    #         record.picking_id.do_unreserve()
    #         if record.sh_source_mo_id.lot_ids:
                
    #             # print("\n\n\n\n\nmove_lines",record.mapped('move_line_ids'))
    #             lines = record.mapped('move_line_ids').filtered(lambda x: not x.lot_id).unlink()
    #             # print("\n\n\nlines",lines)
    #             # record.move_line_ids = False
    #             count = 1
    #             for rec in record.sh_source_mo_id.lot_ids:

    #                 if rec.quant_ids:
    #                     for quant in rec.quant_ids:
    #                         # if quant.location_id.id == record.picking_id.location_dest_id.id:
    #                         if quant.location_id.id == record.picking_id.location_id.id and quant.available_quantity > 0:
    #                             if count <= record.product_uom_qty:
    #                                 record.move_line_ids = [(0, 0, {
    #                                     'picking_id': record.picking_id.id,
    #                                     'product_id': record.product_id.id,
    #                                     'location_id': record.picking_id.location_id.id,
    #                                     'location_dest_id': record.picking_id.location_dest_id.id,
    #                                     'lot_id': rec.id,        
    #                                     'move_id': record.id,
    #                                     # 'qty_done': 1,
    #                                     'company_id': record.company_id.id,
    #                                     "package_level_id": False,
    #                                     "lot_name": False,
    #                                     "package_id": False,
    #                                     "result_package_id": False,
    #                                     })]           
    #                                 count += 1
    #                             else:
    #                                 break
                # print("\n\n\nlines 2222",lines)
                # print("\n\n\nlines 3333",record.move_line_ids)

    # @api.onchange('sh_internal_picking_id')
    # def _onchange_sh_internal_picking_id(self):
    #     print("\n\n\ncalled 1111")
    #     """ This will set the serial number to the move line based on the selected Internal Transfer."""
    #     for record in self:
    #         if record.sh_internal_picking_id:
    #             record.picking_id.do_unreserve()
    #             record.move_line_ids = False
    #             count = 1
    #             for rec in record.sh_internal_picking_id.move_ids:
    #                 for line in rec.move_line_ids:
    #                     if line.location_dest_id.id == record.picking_id.location_id.id:
    #                         if count <= record.product_uom_qty:
    #                             record.move_line_ids = [(0, 0, {
    #                                 'picking_id': record.picking_id.id,
    #                                 'product_id': record.product_id.id,
    #                                 'location_id': record.picking_id.location_id.id,
    #                                 'location_dest_id': record.picking_id.location_dest_id.id,
    #                                 'lot_id': line.lot_id.id,        
    #                                 'move_id': record.id,
    #                                 'qty_done': 1,
    #                                 'company_id': record.company_id.id,
    #                                 "package_level_id": False,
    #                                 "lot_name": False,
    #                                 "package_id": False,
    #                                 "result_package_id": False,
    #                                 })]           
    #                             count += 1
    #                         else:
    #                             break

    def _action_assign(self, force_qty=False):
        """ Reserve stock moves by creating their stock move lines. A stock move is
        considered reserved once the sum of `reserved_qty` for all its move lines is
        equal to its `product_qty`. If it is less, the stock move is considered
        partially available.
        """
        StockMove = self.env['stock.move']
        assigned_moves_ids = OrderedSet()
        partially_available_moves_ids = OrderedSet()
        # Read the `reserved_availability` field of the moves out of the loop to prevent unwanted
        # cache invalidation when actually reserving the move.
        reserved_availability = {move: move.reserved_availability for move in self}
        roundings = {move: move.product_id.uom_id.rounding for move in self}
        move_line_vals_list = []
        # Once the quantities are assigned, we want to find a better destination location thanks
        # to the putaway rules. This redirection will be applied on moves of `moves_to_redirect`.
        moves_to_redirect = OrderedSet()
        moves_to_assign = self
        if not force_qty:
            moves_to_assign = self.filtered(lambda m: m.state in ['confirmed', 'waiting', 'partially_available'])
        moves_mto = moves_to_assign.filtered(lambda m: m.move_orig_ids and not m._should_bypass_reservation())
        quants_cache = self.env['stock.quant']._get_quants_by_products_locations(moves_mto.product_id, moves_mto.location_id)
        for move in moves_to_assign:
            rounding = roundings[move]
            if not force_qty:
                missing_reserved_uom_quantity = move.product_uom_qty
            else:
                missing_reserved_uom_quantity = force_qty
            missing_reserved_uom_quantity -= reserved_availability[move]
            missing_reserved_quantity = move.product_uom._compute_quantity(missing_reserved_uom_quantity, move.product_id.uom_id, rounding_method='HALF-UP')
            if move._should_bypass_reservation():
                # create the move line(s) but do not impact quants
                if move.move_orig_ids:
                    available_move_lines = move._get_available_move_lines(assigned_moves_ids, partially_available_moves_ids)
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        qty_added = min(missing_reserved_quantity, quantity)
                        move_line_vals = move._prepare_move_line_vals(qty_added)
                        move_line_vals.update({
                            'location_id': location_id.id,
                            'lot_id': lot_id.id,
                            'lot_name': lot_id.name,
                            'owner_id': owner_id.id,
                            'package_id': package_id.id,
                        })
                        move_line_vals_list.append(move_line_vals)
                        missing_reserved_quantity -= qty_added
                        if float_is_zero(missing_reserved_quantity, precision_rounding=move.product_id.uom_id.rounding):
                            break

                if missing_reserved_quantity and move.product_id.tracking == 'serial' and (move.picking_type_id.use_create_lots or move.picking_type_id.use_existing_lots):
                    for i in range(0, int(missing_reserved_quantity)):
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=1))
                elif missing_reserved_quantity:
                    to_update = move.move_line_ids.filtered(lambda ml: ml.product_uom_id == move.product_uom and
                                                            ml.location_id == move.location_id and
                                                            ml.location_dest_id == move.location_dest_id and
                                                            ml.picking_id == move.picking_id and
                                                            not ml.lot_id and
                                                            not ml.package_id and
                                                            not ml.owner_id)
                    if to_update:
                        to_update[0].reserved_uom_qty += move.product_id.uom_id._compute_quantity(
                            missing_reserved_quantity, move.product_uom, rounding_method='HALF-UP')
                    else:
                        move_line_vals_list.append(move._prepare_move_line_vals(quantity=missing_reserved_quantity))
                assigned_moves_ids.add(move.id)
                moves_to_redirect.add(move.id)
            else:
                if float_is_zero(move.product_uom_qty, precision_rounding=move.product_uom.rounding):
                    assigned_moves_ids.add(move.id)
                elif not move.move_orig_ids:
                    
                    if move.procure_method == 'make_to_order':
                        continue
                    # If we don't need any quantity, consider the move assigned.
                    need = missing_reserved_quantity
                    if float_is_zero(need, precision_rounding=rounding):
                        assigned_moves_ids.add(move.id)
                        continue
                    # Reserve new quants and create move lines accordingly.
                    forced_package_id = move.package_level_id.package_id or None
                    available_quantity = move._get_available_quantity(move.location_id, package_id=forced_package_id)
                    if available_quantity <= 0:
                        continue
                    
                    taken_quantity = 0
                    
                    # =====================================  SHSMART CODE START =================================================
                    
                    # --------- FIND QUANT WITH LOT AND MOVE LOCATION WITH AVAILABLE QTY GRATER THAN 0 ------
                    # picking.picking_type_code == 'outgoing' or picking.picking_type_code == 'internal'
                    if move.picking_id.picking_type_code == 'outgoing' and move.picking_id.picking_type_code == 'internal':
                        if move.picking.sh_source_mo_id:
                            lot_id=False
                            quants=False
                            quants_with_diff_internal_loc=False
                            for lot in move.picking_id.sh_source_mo_id.lot_ids:
                                if not quants_with_diff_internal_loc and not quants:
                                    quants = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.id','=',lot.id),('location_id','=',move.location_id.id),('quantity','>',0)])
                                    # if not quants :
                                    #     quants_with_diff_internal_loc = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.name','=',lot.name),('location_id','!=',move.location_id.id),('location_id.available_stock','=',True),('location_id.usage','=','internal'),('quantity','>',0)])
                            if quants:
                                quants=quants[0]
                                available_quantity = move._get_available_quantity(quants.location_id, package_id=forced_package_id)
                                taken_quantity = move._update_reserved_quantity(need, available_quantity, quants.location_id, package_id=forced_package_id,lot_id=quants.lot_id, strict=False)
                            elif quants_with_diff_internal_loc:
                                quants_with_diff_internal_loc=quants_with_diff_internal_loc[0]
                                available_quantity = move._get_available_quantity(quants_with_diff_internal_loc.location_id, package_id=forced_package_id)
                                taken_quantity = move._update_reserved_quantity(need, available_quantity, quants_with_diff_internal_loc.location_id, package_id=forced_package_id,lot_id=quants_with_diff_internal_loc.lot_id, strict=False)
                            else:
                                taken_quantity = move._update_reserved_quantity(need, available_quantity, move.location_id, package_id=forced_package_id, strict=False)
                        elif move.picking.sh_internal_picking_id:
                            sh_lot_ids = move.picking.sh_internal_picking_id.move_ids.mapped('move_line_ids.lot_id')
                            lot_id=False
                            quants=False
                            quants_with_diff_internal_loc=False
                            for lot in sh_lot_ids:
                                if not quants_with_diff_internal_loc and not quants:
                                    quants = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.id','=',lot.id),('location_id','=',move.location_id.id),('quantity','>',0)])
                                    # if not quants :
                                    #     quants_with_diff_internal_loc = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.name','=',lot.name),('location_id','!=',move.location_id.id),('location_id.available_stock','=',True),('location_id.usage','=','internal'),('quantity','>',0)])
                            if quants:
                                quants=quants[0]
                                available_quantity = move._get_available_quantity(quants.location_id, package_id=forced_package_id)
                                taken_quantity = move._update_reserved_quantity(need, available_quantity, quants.location_id, package_id=forced_package_id,lot_id=quants.lot_id, strict=False)
                            elif quants_with_diff_internal_loc:
                                quants_with_diff_internal_loc=quants_with_diff_internal_loc[0]
                                available_quantity = move._get_available_quantity(quants_with_diff_internal_loc.location_id, package_id=forced_package_id)
                                taken_quantity = move._update_reserved_quantity(need, available_quantity, quants_with_diff_internal_loc.location_id, package_id=forced_package_id,lot_id=quants_with_diff_internal_loc.lot_id, strict=False)
                            else:
                                taken_quantity = move._update_reserved_quantity(need, available_quantity, move.location_id, package_id=forced_package_id, strict=False)
                        else:
                            taken_quantity = move._update_reserved_quantity(need, available_quantity, move.location_id, package_id=forced_package_id, strict=False)
                    else:
                        # Sale Delivery / any non-custom path must use standard
                        # Odoo reservation. The condition above is never true
                        # (outgoing AND internal); without this else, taken_quantity
                        # stays 0 and serials are never reserved.
                        taken_quantity = move._update_reserved_quantity(
                            need, available_quantity, move.location_id,
                            package_id=forced_package_id, strict=False)

                    # =====================================  SHSMART CODE END ====================================
                    
                    if float_is_zero(taken_quantity, precision_rounding=rounding):
                        continue
                    moves_to_redirect.add(move.id)
                    if float_compare(need, taken_quantity, precision_rounding=rounding) == 0:
                        assigned_moves_ids.add(move.id)
                    else:
                        partially_available_moves_ids.add(move.id)
                else:
                    
                    # Check what our parents brought and what our siblings took in order to
                    # determine what we can distribute.
                    # `qty_done` is in `ml.product_uom_id` and, as we will later increase
                    # the reserved quantity on the quants, convert it here in
                    # `product_id.uom_id` (the UOM of the quants is the UOM of the product).
                    available_move_lines = move._get_available_move_lines(assigned_moves_ids, partially_available_moves_ids)
                    if not available_move_lines:
                        continue
                    for move_line in move.move_line_ids.filtered(lambda m: m.reserved_qty):
                        if available_move_lines.get((move_line.location_id, move_line.lot_id, move_line.result_package_id, move_line.owner_id)):
                            available_move_lines[(move_line.location_id, move_line.lot_id, move_line.result_package_id, move_line.owner_id)] -= move_line.reserved_qty
                    for (location_id, lot_id, package_id, owner_id), quantity in available_move_lines.items():
                        need = move.product_qty - sum(move.move_line_ids.mapped('reserved_qty'))
                        # `quantity` is what is brought by chained done move lines. We double check
                        # here this quantity is available on the quants themselves. If not, this
                        # could be the result of an inventory adjustment that removed totally of
                        # partially `quantity`. When this happens, we chose to reserve the maximum
                        # still available. This situation could not happen on MTS move, because in
                        # this case `quantity` is directly the quantity on the quants themselves.
                        available_quantity = move._get_available_quantity(location_id, lot_id=lot_id, package_id=package_id, owner_id=owner_id, strict=True)
                        if float_is_zero(available_quantity, precision_rounding=rounding):
                            continue
                        
                        
                        
                        # =====================================  SHSMART CODE START =================================================
                    
                        # --------- FIND QUANT WITH LOT AND MOVE LOCATION WITH AVAILABLE QTY GRATER THAN 0 ------
                        if move.picking_id.picking_type_code == 'outgoing' and  move.picking_id.picking_type_code == 'internal':
                            if move.picking.sh_source_mo_id:
                                lot_id=False
                                quants=False
                                quants_with_diff_internal_loc=False
                                for lot in move.picking_id.sh_source_mo_id.lot_ids:
                                    if not quants_with_diff_internal_loc and not quants:
                                        quants = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.id','=',lot.id),('location_id','=',move.location_id.id),('quantity','>',0)])
                                        # if not quants :
                                        #     quants_with_diff_internal_loc = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.name','=',lot.name),('location_id','!=',move.location_id.id),('location_id.available_stock','=',True),('location_id.usage','=','internal'),('quantity','>',0)])
                            
                                if quants:
                                    quants=quants[0]
                                    available_quantity = move._get_available_quantity(quants.location_id, lot_id=quants.lot_id, package_id=package_id, owner_id=owner_id, strict=True)
                                    taken_quantity = move._update_reserved_quantity(need, min(quantity, available_quantity), quants.location_id, quants.lot_id, package_id, owner_id)
                                elif quants_with_diff_internal_loc:
                                    quants_with_diff_internal_loc=quants_with_diff_internal_loc[0]
                                    available_quantity = move._get_available_quantity(quants_with_diff_internal_loc.location_id, lot_id=quants_with_diff_internal_loc.lot_id, package_id=package_id, owner_id=owner_id, strict=True)
                                    taken_quantity = move._update_reserved_quantity(need, min(quantity, available_quantity), quants_with_diff_internal_loc.location_id, quants_with_diff_internal_loc.lot_id, package_id, owner_id)
                                else:
                                    taken_quantity = move._update_reserved_quantity(need, min(quantity, available_quantity), location_id, lot_id, package_id, owner_id)
                            elif move.picking.sh_internal_picking_id:
                                sh_lot_ids = move.picking.sh_internal_picking_id.move_ids.mapped('move_line_ids.lot_id')
                                lot_id=False
                                quants=False
                                quants_with_diff_internal_loc=False
                                for lot in sh_lot_ids:
                                    if not quants_with_diff_internal_loc and not quants:
                                        quants = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.id','=',lot.id),('location_id','=',move.location_id.id),('quantity','>',0)])
                                        # if not quants :
                                        #     quants_with_diff_internal_loc = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.name','=',lot.name),('location_id','!=',move.location_id.id),('location_id.available_stock','=',True),('location_id.usage','=','internal'),('quantity','>',0)])
                                if quants:
                                    quants=quants[0]
                                    available_quantity = move._get_available_quantity(quants.location_id, package_id=forced_package_id)
                                    taken_quantity = move._update_reserved_quantity(need, available_quantity, quants.location_id, package_id=forced_package_id,lot_id=quants.lot_id, strict=False)
                                elif quants_with_diff_internal_loc:
                                    quants_with_diff_internal_loc=quants_with_diff_internal_loc[0]
                                    available_quantity = move._get_available_quantity(quants_with_diff_internal_loc.location_id, package_id=forced_package_id)
                                    taken_quantity = move._update_reserved_quantity(need, available_quantity, quants_with_diff_internal_loc.location_id, package_id=forced_package_id,lot_id=quants_with_diff_internal_loc.lot_id, strict=False)
                                else:
                                    taken_quantity = move._update_reserved_quantity(need, available_quantity, move.location_id, package_id=forced_package_id, strict=False)
                
                        else:
                            taken_quantity = move.with_context(quants_cache=quants_cache)._update_reserved_quantity(need, min(quantity, available_quantity), location_id, lot_id, package_id, owner_id)
                    
                        # =====================================  SHSMART CODE END ====================================

                        
                        if float_is_zero(taken_quantity, precision_rounding=rounding):
                            continue
                        moves_to_redirect.add(move.id)
                        if float_is_zero(need - taken_quantity, precision_rounding=rounding):
                            assigned_moves_ids.add(move.id)
                            break
                        partially_available_moves_ids.add(move.id)
            if move.product_id.tracking == 'serial':
                move.next_serial_count = move.product_uom_qty

        self.env['stock.move.line'].create(move_line_vals_list)
        StockMove.browse(partially_available_moves_ids).write({'state': 'partially_available'})
        StockMove.browse(assigned_moves_ids).write({'state': 'assigned'})
        if not self.env.context.get('bypass_entire_pack'):
            self.picking_id._check_entire_pack()
        StockMove.browse(moves_to_redirect).move_line_ids._apply_putaway_strategy()
        