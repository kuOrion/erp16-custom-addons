# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, _, fields, api
from ast import literal_eval
import re

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.display_name

        default_immediate_tranfer = True
        if self.env['ir.config_parameter'].sudo().get_param('stock.no_default_immediate_tranfer'):
            default_immediate_tranfer = False

        context = {
            'search_default_picking_type_id': [self.id],
            'default_picking_type_id': self.id,
            'default_immediate_transfer': False,
            'default_company_id': self.company_id.id,
        }

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        return action

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    mo_count = fields.Integer(string='MO Count', compute='_compute_mo_count')
    internal_transfer_count = fields.Integer(string='Internal Transfer Count', compute='_compute_internal_transfer_count')

    sh_source_mo_id = fields.Many2one('sh.finished.product', string='MO')
    sh_source_mo_ids = fields.Many2many('sh.finished.product', string='Source Document',
        compute='_compute_sh_source_mo_ids' )
    sh_internal_picking_id = fields.Many2one('stock.picking', string='Internal Picking',domain="[('picking_type_id.code', '=', 'internal')]")
    sh_internal_picking_ids = fields.Many2many('stock.picking', string='Internal Picking',
        compute='_compute_sh_internal_picking_ids' )
    
    def _compute_sh_source_mo_ids(self):
        for record in self:
            record.sh_source_mo_ids = []
            move_ids = []
            for move in record.move_ids_without_package:
                
                mo_record = self.env['mrp.production'].search([('location_dest_id','=',record.location_id.id),
                                                            ('product_id','=',move.product_id.id),
                                                            ('sh_main_mo', '=', True),
                                                            ('state','=','done')])
                if mo_record:
                    for mo in mo_record:
                        finished_products = self.env['sh.finished.product'].search([
                                ('production_id', '=', mo.id)
                            ])
                        for finished_product in finished_products:
                            # Get the lot_ids from the finished product
                            lot_ids = finished_product.lot_ids

                        if move.product_id.tracking == 'serial' and lot_ids:
                            serial_numbers_in_stock = self.env['stock.quant'].search([
                            ('product_id', '=', move.product_id.id),
                            ('location_id', '=', record.location_id.id),
                            ('lot_id', 'in', lot_ids.ids),
                            ('quantity', '>', 0)
                            ])
                            if serial_numbers_in_stock:
                                move_ids.append(mo.id)
            if move_ids:
                finish_product = self.env['sh.finished.product'].search([('production_id','in',move_ids)])
                record.sh_source_mo_ids = [(6, 0, finish_product.ids)]

    def _compute_sh_internal_picking_ids(self):
        for record in self:
            record.sh_internal_picking_ids = []
            picking_id = []
            for move in record.move_ids_without_package:   
                picking_record = self.env['stock.picking'].search([
                    ('location_dest_id', '=', record.location_id.id),
                    ('product_id', '=', move.product_id.id),
                    ('state', '=', 'done')
                ])

                lot_ids = [] 
                for pick in picking_record:
                    for move_line in pick.move_line_ids:
                        if move_line.lot_id:  
                            lot_ids.append(move_line.lot_id.id)  
                
                    if lot_ids:
                        serial_numbers_in_stock = self.env['stock.quant'].search([
                            ('product_id', '=', move.product_id.id),
                            ('location_id', '=', record.location_id.id),
                            ('lot_id', 'in', lot_ids),
                            ('quantity', '>', 0)
                        ])

                        if serial_numbers_in_stock:
                            picking_id.append(pick.id)

            if picking_id:
                record.sh_internal_picking_ids = [(6, 0, picking_id)]

    @api.onchange('sh_source_mo_id')
    def _onchange_sh_source_mo_id(self):
        for record in self:
            if record.sh_source_mo_id:
                record.sh_internal_picking_id = False

    @api.onchange('sh_internal_picking_id')
    def _onchange_sh_internal_picking_id(self):
        for record in self:
            if record.sh_internal_picking_id:
                record.sh_source_mo_id = False


    def _compute_mo_count(self):
        for record in self:
            record.mo_count = 0
            for move in record:
                if move.sh_source_mo_id:
                    record.mo_count += len(move.sh_source_mo_id)
    
    def action_mo_records(self):
        self.ensure_one()
        mo_ids = []
        for rec in self:
            if rec.sh_source_mo_id:
                mo_ids.append(rec.sh_source_mo_id.production_id.id)
        action = self.env["ir.actions.actions"]._for_xml_id("mrp.mrp_production_action")
        action['domain'] = [('id', 'in', mo_ids)]
        action['context'] = dict(self._context, create=False)
        return action
    
    def _compute_internal_transfer_count(self):
        for record in self:
            record.internal_transfer_count = 0
            for move in record:
                if move.sh_internal_picking_id:
                    record.internal_transfer_count += len(move.sh_internal_picking_id)

    def action_internal_transfer_records(self):
        self.ensure_one()
        picking_ids = []
        for rec in self:
            if rec.sh_internal_picking_id:
                picking_ids.append(rec.sh_internal_picking_id.id)
        action = self.env["ir.actions.actions"]._for_xml_id("stock.stock_picking_action_picking_type")
        action['domain'] = [('id', 'in', picking_ids)]
        action['context'] = dict(self._context, create=False)
        return action
    
    # def button_validate(self):
    #     if self.move_ids:
    #         move_line_ids = self.move_ids.mapped('move_line_ids').filtered(lambda x: not x.sh_select_record)
    #         move_line_ids.unlink()                
    #     return super(StockPicking, self).button_validate()
    
    # @api.model
    # def create(self, values):
    
    #     result = super(StockPicking, self).create(values)
    #     print('===========result========>',result)
    #     print('==========self._context=========>',self._context)
    #     print('===========self.env.context========>',self.env.context)
    #     return result
    
    # def write(self, values):
    #     if 'sh_source_mo_id' in values and 'operation_type_view' in self.env.context and self.env.context.get('operation_type_view'):
    #         for rec in self:
    #             rec.do_unreserve()
    #     result = super(StockPicking, self).write(values)
    #     for rec in self:
    #         rec.action_assign()

    #     return result


    # UPDATE STANARD METHOD LOGIC WHEN GETITNG MOVE LINES 

    def action_assign(self):
        for picking in self:
            res = super(StockPicking,picking).action_assign()
            
            # MO / Internal Picking lot reservation is Internal Transfer only.
            # Sale Delivery stays standard Odoo (super() above).
            if picking.picking_type_code == 'internal':
             
                if picking.sh_source_mo_id:
                    
                    picking.do_unreserve()

                    for move in picking.move_ids_without_package:
                        demand_qty = move.product_uom_qty
                        # for lot in picking.lot_ids:
                        for lot in picking.sh_source_mo_id.lot_ids:




                            quants = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id','=',lot.id),('location_id','=',picking.location_id.id),('quantity','>',0)])
                            # quants = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.name','=',lot.name),('location_id','=',picking.location_id.id),('location_id.usage','=','internal'),('quantity','>',0)])
                            quants_with_diff_internal_loc = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id','=',lot.id),('location_id','=',picking.location_id.id),('quantity','>',0)])
                            # quants_with_diff_internal_loc = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.name','=',lot.name),('location_id','!=',picking.location_id.id),('location_id','!=',picking.picking_type_id.warehouse_id.wh_input_stock_loc_id.id),('location_id.usage','=','internal'),('quantity','>',0)])
                            # quants._compute_available_quantity()
                            quants_with_diff_internal_loc._compute_available_quantity()
                            
                            
                            if demand_qty != 0 and quants and quants[0].available_quantity > 0:

                                if quants[0].available_quantity >= demand_qty:
                                    
                                    self.env['stock.move.line'].create({
                                        'picking_id' : picking.id,
                                        'product_id':move.product_id.id,
                                        'product_uom_id':move.product_uom.id,
                                        'location_id' : move.location_id.id,
                                        'location_dest_id':move.location_dest_id.id,
                                        'reserved_uom_qty' : demand_qty,
                                        'lot_id' : quants[0].lot_id.id,
                                        'move_id' : move.id,
                                        'date' : move.date,
                                        'reference':move.reference,
                                        'origin':move.origin,
                                        'company_id' : move.company_id.id,
                                    })

                                    self.env['stock.quant']._update_reserved_quantity(
                                        move.product_id, move.location_id, demand_qty, lot_id=quants[0].lot_id
                                    )
                                    demand_qty = 0
                                
                                else:

                                    self.env['stock.move.line'].create({

                                        'picking_id' : picking.id,
                                        'product_id':move.product_id.id,
                                        'product_uom_id':move.product_uom.id,
                                        'location_id' : move.location_id.id,
                                        'location_dest_id':move.location_dest_id.id,
                                        'reserved_uom_qty' : quants[0].available_quantity,
                                        'lot_id' : quants[0].lot_id.id,
                                        'move_id' : move.id,
                                        'date' : move.date,
                                        'reference':move.reference,
                                        'origin':move.origin,
                                        'company_id' : move.company_id.id,

                                    })
                                    demand_qty = demand_qty - quants[0].available_quantity
                                    self.env['stock.quant']._update_reserved_quantity(
                                        move.product_id, move.location_id, quants[0].available_quantity, lot_id=quants[0].lot_id
                                    )
                                
                                    
                            if demand_qty != 0 and quants_with_diff_internal_loc and quants_with_diff_internal_loc[0].available_quantity > 0:
                                if quants_with_diff_internal_loc[0].available_quantity >= demand_qty:
                                    
                                    
                                    self.env['stock.move.line'].create({
                                        'picking_id' : picking.id,
                                        'product_id':move.product_id.id,
                                        'product_uom_id':move.product_uom.id,
                                        'location_id' : quants_with_diff_internal_loc[0].location_id.id,
                                        'location_dest_id':move.location_dest_id.id,
                                        'reserved_uom_qty' : demand_qty,
                                        'lot_id' : quants_with_diff_internal_loc[0].lot_id.id,
                                        'move_id' : move.id,
                                        'date' : move.date,
                                        'reference':move.reference,
                                        'origin':move.origin,
                                        'company_id' : move.company_id.id,
                                        
                                    })
                                    self.env['stock.quant']._update_reserved_quantity(
                                        move.product_id, quants_with_diff_internal_loc[0].location_id, demand_qty, lot_id=quants_with_diff_internal_loc[0].lot_id
                                    )
                                    demand_qty = 0
                                
                                else:
                                    self.env['stock.move.line'].create({

                                        'picking_id' : picking.id,
                                        'product_id':move.product_id.id,
                                        'product_uom_id':move.product_uom.id,
                                        'location_id' : quants_with_diff_internal_loc[0].location_id.id,
                                        'location_dest_id':move.location_dest_id.id,
                                        'reserved_uom_qty' : quants_with_diff_internal_loc[0].available_quantity,
                                        'lot_id' : quants_with_diff_internal_loc[0].lot_id.id,
                                        'move_id' : move.id,
                                        'date' : move.date,
                                        'reference':move.reference,
                                        'origin':move.origin,
                                        'company_id' : move.company_id.id,

                                    })
                                    reserve_qty =  quants_with_diff_internal_loc[0].available_quantity
                                    self.env['stock.quant']._update_reserved_quantity(
                                        move.product_id, quants_with_diff_internal_loc[0].location_id, reserve_qty, lot_id=quants_with_diff_internal_loc[0].lot_id
                                    )
                                    demand_qty = demand_qty - reserve_qty                                    
                                        
                    for move in picking.move_ids_without_package:
                        if move.product_uom_qty == sum(move.move_line_ids.mapped('reserved_uom_qty')):
                            move.write({
                                'state' : 'assigned'
                            })
                        
                        elif move.product_uom_qty != sum(move.move_line_ids.mapped('reserved_uom_qty')) and sum(move.move_line_ids.mapped('reserved_uom_qty')) != 0:
                            move.write({
                                'state' : 'partially_available'
                            })
                        
                        else:
                            move.write({
                                'state' : 'confirmed'
                            })

                if picking.sh_internal_picking_id:
                    
                    picking.do_unreserve()

                    for move in picking.move_ids_without_package:
                        demand_qty = move.product_uom_qty
                        # for lot in picking.lot_ids:
                        sh_lot_ids = picking.sh_internal_picking_id.move_ids.mapped('move_line_ids.lot_id')
                        for lot in sh_lot_ids:

                            quants = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.name','=',lot.name),('location_id','=',picking.location_id.id),('location_id.usage','=','internal'),('quantity','>',0)])
                            quants_with_diff_internal_loc = self.env['stock.quant'].sudo().search([('product_id','=',move.product_id.id),('lot_id.name','=',lot.name),('location_id','!=',picking.location_id.id),('location_id','!=',picking.picking_type_id.warehouse_id.wh_input_stock_loc_id.id),('location_id.usage','=','internal'),('quantity','>',0)])
                            quants._compute_available_quantity()
                            quants_with_diff_internal_loc._compute_available_quantity()
                            
                            
                            if demand_qty != 0 and quants and quants[0].available_quantity > 0:

                                if quants[0].available_quantity >= demand_qty:
                                    
                                    self.env['stock.move.line'].create({
                                        'picking_id' : picking.id,
                                        'product_id':move.product_id.id,
                                        'product_uom_id':move.product_uom.id,
                                        'location_id' : move.location_id.id,
                                        'location_dest_id':move.location_dest_id.id,
                                        'reserved_uom_qty' : demand_qty,
                                        'lot_id' : quants[0].lot_id.id,
                                        'move_id' : move.id,
                                        'date' : move.date,
                                        'reference':move.reference,
                                        'origin':move.origin,
                                        'company_id' : move.company_id.id,

                                    })

                                    self.env['stock.quant']._update_reserved_quantity(
                                        move.product_id, move.location_id, demand_qty, lot_id=quants[0].lot_id
                                    )
                                    demand_qty = 0
                                
                                else:

                                    self.env['stock.move.line'].create({

                                        'picking_id' : picking.id,
                                        'product_id':move.product_id.id,
                                        'product_uom_id':move.product_uom.id,
                                        'location_id' : move.location_id.id,
                                        'location_dest_id':move.location_dest_id.id,
                                        'reserved_uom_qty' : quants[0].available_quantity,
                                        'lot_id' : quants[0].lot_id.id,
                                        'move_id' : move.id,
                                        'date' : move.date,
                                        'reference':move.reference,
                                        'origin':move.origin,
                                        'company_id' : move.company_id.id,

                                        
                                    })
                                    demand_qty = demand_qty - quants[0].available_quantity
                                    self.env['stock.quant']._update_reserved_quantity(
                                        move.product_id, move.location_id, quants[0].available_quantity, lot_id=quants[0].lot_id
                                    )
                                
                                    
                            if demand_qty != 0 and quants_with_diff_internal_loc and quants_with_diff_internal_loc[0].available_quantity > 0:
                                if quants_with_diff_internal_loc[0].available_quantity >= demand_qty:
                                    
                                    
                                    self.env['stock.move.line'].create({
                                        'picking_id' : picking.id,
                                        'product_id':move.product_id.id,
                                        'product_uom_id':move.product_uom.id,
                                        'location_id' : quants_with_diff_internal_loc[0].location_id.id,
                                        'location_dest_id':move.location_dest_id.id,
                                        'reserved_uom_qty' : demand_qty,
                                        'lot_id' : quants_with_diff_internal_loc[0].lot_id.id,
                                        'move_id' : move.id,
                                        'date' : move.date,
                                        'reference':move.reference,
                                        'origin':move.origin,
                                        'company_id' : move.company_id.id,

                                        
                                    })
                                    self.env['stock.quant']._update_reserved_quantity(
                                        move.product_id, quants_with_diff_internal_loc[0].location_id, demand_qty, lot_id=quants_with_diff_internal_loc[0].lot_id
                                    )
                                    demand_qty = 0
                                
                                else:
                                    self.env['stock.move.line'].create({

                                        'picking_id' : picking.id,
                                        'product_id':move.product_id.id,
                                        'product_uom_id':move.product_uom.id,
                                        'location_id' : quants_with_diff_internal_loc[0].location_id.id,
                                        'location_dest_id':move.location_dest_id.id,
                                        'reserved_uom_qty' : quants_with_diff_internal_loc[0].available_quantity,
                                        'lot_id' : quants_with_diff_internal_loc[0].lot_id.id,
                                        'move_id' : move.id,
                                        'date' : move.date,
                                        'reference':move.reference,
                                        'origin':move.origin,
                                        'company_id' : move.company_id.id,

                                    })
                                    reserve_qty =  quants_with_diff_internal_loc[0].available_quantity
                                    self.env['stock.quant']._update_reserved_quantity(
                                        move.product_id, quants_with_diff_internal_loc[0].location_id, reserve_qty, lot_id=quants_with_diff_internal_loc[0].lot_id
                                    )
                                    demand_qty = demand_qty - reserve_qty
                                        
                    for move in picking.move_ids_without_package:
                        if move.product_uom_qty == sum(move.move_line_ids.mapped('reserved_uom_qty')):
                            move.write({
                                'state' : 'assigned'
                            })
                        
                        elif move.product_uom_qty != sum(move.move_line_ids.mapped('reserved_uom_qty')) and sum(move.move_line_ids.mapped('reserved_uom_qty')) != 0:
                            move.write({
                                'state' : 'partially_available'
                            })
                        
                        else:
                            move.write({
                                'state' : 'confirmed'
                            })


        return res
    
    def button_validate(self):
        res = super(StockPicking,self).button_validate()
        if self.picking_type_id.code == 'internal' and self.move_ids:
            total_qty = sum(line.quantity_done for line in self.move_ids)
            base = re.sub(r'\s*\(\s*[\d\.]+\s*\)\s*$', '', self.name or '')
            if float(total_qty).is_integer():
                qty_str = str(int(total_qty))
            else:
                qty_str = str(total_qty)
            # build the new name
            new_name = f"{base} ({qty_str})" if total_qty else base
            # update only if changed
            if self.name != new_name:
                self.name = new_name
        return res
    
    @api.model
    def sh_update_internal_transfer_name(self):
        pickings = self.search([
            ('picking_type_id.code', '=', 'internal'),
        ])

        for pick in pickings:
            if pick.move_ids:
                # sum of all done quantities on the move lines
                total_qty = sum(line.quantity_done for line in pick.move_ids)
                # remove any existing " (number)" suffix
                base = re.sub(r'\s*\(\s*[\d\.]+\s*\)\s*$', '', pick.name or '')
                # format qty: int if whole number, else float
                if float(total_qty).is_integer():
                    qty_str = str(int(total_qty))
                else:
                    qty_str = str(total_qty)
                # build the new name
                new_name = f"{base} ({qty_str})" if total_qty else base
                # update only if changed
                if pick.name != new_name:
                    pick.name = new_name