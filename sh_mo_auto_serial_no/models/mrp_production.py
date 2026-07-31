# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import models, _, fields, api
from odoo.exceptions import UserError, ValidationError
import re
from odoo.tools import float_compare, float_is_zero

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    sh_serial_no_type = fields.Selection(
        string='Serial No Type',
        selection=[('type1', 'Type 1'), ('type2', 'Type 2')],
        default='type1'
    )
    sh_finished_product_ids = fields.One2many('sh.finished.product', 'production_id', string='Finished Product')
    sh_produce_qty = fields.Float('Produce Quantity')
    sh_auto_assign_serial_no = fields.Boolean(related='product_id.sh_auto_assign_serial_no', string='Auto Assign Serial Number')
    sh_main_mo = fields.Boolean(
        compute='_compute_sh_main_mo',store=True )
    # count_assign_serial_button_click = fields.Integer(string='Count Assign Serial Button Click', default=0)
    sh_total_qty = fields.Integer(string='Total Quantity')
    sh_remaining_qty = fields.Integer(string='Remaining Produce Quantity')
    # sh_count_finished_product = fields.Integer(string='Count Finished Product', compute='_compute_sh_count_finished_product')
    sh_is_serial_btn_invisible = fields.Boolean(string='Hide Serial No Button', compute='_compute_serial_btn_visibility')
    sh_partially_done = fields.Boolean(
        string='Partially Done',
        store=True)
    # state = fields.Selection(
    #     selection_add=[('partially_done', 'Partially Done')]
    # )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('to_close', 'To Close'),
        ('partially_done', 'Partially Done'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        compute='_compute_state', copy=False, index=True, readonly=True,
        store=True, tracking=True,
        help=" * Draft: The MO is not confirmed yet.\n"
             " * Confirmed: The MO is confirmed, the stock rules and the reordering of the components are trigerred.\n"
             " * In Progress: The production has started (on the MO or on the WO).\n"
             " * To Close: The production is done, the MO has to be closed.\n"
             " * Done: The MO is closed, the stock moves are posted. \n"
             " * Cancelled: The MO has been cancelled, can't be confirmed anymore.")
    # def _compute_sh_count_finished_product(self):
    #     for record in self:
    #         if record.sh_finished_product_ids:
    #             record.sh_count_finished_product = record.sh_finished_product_ids[0].sh_product_qty
    #         else:
    #             record.sh_count_finished_product = 0  

    # @api.constrains('sh_produce_qty', 'product_id')
    # def _check_produce_qty(self):
    #     for rec in self:
    #         if rec.product_id.sh_auto_assign_serial_no and rec.sh_produce_qty <= 0:
    #             raise ValidationError(_("Produce Quantity must be greater than 0."))

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if rec.sh_main_mo and rec.product_qty > 0:
                rec.sh_total_qty = rec.product_qty
        return res

            
    @api.depends('sh_total_qty', 'sh_finished_product_ids')
    def _compute_serial_btn_visibility(self):
        for record in self:
            if record.sh_finished_product_ids and record.sh_total_qty == record.sh_finished_product_ids[0].sh_product_qty:
                record.sh_is_serial_btn_invisible = True
            else:
                record.sh_is_serial_btn_invisible = False

    @api.depends('sh_serial_no_type')
    def _compute_sh_main_mo(self):
        for record in self:
            record.sh_main_mo = True
            if self.procurement_group_id and self.procurement_group_id.mrp_production_ids:
                sorted_production = sorted(self.procurement_group_id.mrp_production_ids, key=lambda x: x.id)
                for production in sorted_production:
                    production.sh_main_mo = False
                sorted_production[0].sh_main_mo = True



    @api.onchange('product_qty')
    def _onchange_product_qty(self):
        if self.product_qty > 0:
            self.sh_total_qty = self.product_qty
        else:
            self.sh_total_qty = 0


    @api.onchange('product_id','sh_serial_no_type')
    def _onchange_sh_serial_no_type(self):
        company = self.company_id
        if self.sh_serial_no_type == 'type1' and self.product_id.sh_auto_assign_serial_no:

            message = company.sh_confirirmation_message_type1
            if message:
                return {
                    'warning': {
                        'title': _("Type 1 Confirmation"),
                        'message': message,
                    }
                }
        elif self.sh_serial_no_type == 'type2' and self.product_id.sh_auto_assign_serial_no:
            message = company.sh_confirirmation_message_type2
            if message:
                return {
                    'warning': {
                        'title': _("Type 2 Confirmation"),
                        'message': message,
                    }
                }
    
    def write(self, vals):
        """A prefix has been added to the lot to identify the previous lot number by type."""
        res = super(MrpProduction, self).write(vals)
        if vals.get('lot_producing_id'):
            for rec in self:
                if rec.sh_serial_no_type == 'type1' and self.company_id.sh_prefix_type1 and rec.sh_auto_assign_serial_no:
                    rec.lot_producing_id.write({
                       'sh_config_prifix_type':self.company_id.sh_prefix_type1
                    })
                elif rec.sh_serial_no_type == 'type2' and self.company_id.sh_prefix_type2 and rec.sh_auto_assign_serial_no:
                    rec.lot_producing_id.write({
                       'sh_config_prifix_type': self.company_id.sh_prefix_type2
                   })
                  
                else:
                   return res
        return res
    
    @api.depends(
        'move_raw_ids.state', 'move_raw_ids.quantity_done', 'move_finished_ids.state',
        'workorder_ids.state', 'product_qty', 'qty_producing','sh_partially_done')
    def _compute_state(self):
        """ Compute the production state. This uses a similar process to stock
        picking, but has been adapted to support having no moves. This adaption
        includes some state changes outside of this compute.

        There exist 3 extra steps for production:
        - progress: At least one item is produced or consumed.
        - to_close: The quantity produced is greater than the quantity to
        produce and all work orders has been finished.
        """
        for production in self:

            if production.sh_main_mo and production.sh_total_qty != len(production.sh_finished_product_ids) and production.sh_partially_done:
                production.state = 'partially_done'
            else:
                if not production.state or not production.product_uom_id:
                    production.state = 'draft'
                elif production.state == 'cancel' or (production.move_finished_ids and all(move.state == 'cancel' for move in production.move_finished_ids)):
                    production.state = 'cancel'
                elif (
                    production.state == 'done'
                    or (production.move_raw_ids and all(move.state in ('cancel', 'done') for move in production.move_raw_ids))
                    and all(move.state in ('cancel', 'done') for move in production.move_finished_ids)
                ):
                    production.state = 'done'
                elif production.workorder_ids and all(wo_state in ('done', 'cancel') for wo_state in production.workorder_ids.mapped('state')):
                    production.state = 'to_close'
                elif not production.workorder_ids and float_compare(production.qty_producing, production.product_qty, precision_rounding=production.product_uom_id.rounding) >= 0:
                    production.state = 'to_close'
                elif any(wo_state in ('progress', 'done') for wo_state in production.workorder_ids.mapped('state')):
                    production.state = 'progress'
                elif production.product_uom_id and not float_is_zero(production.qty_producing, precision_rounding=production.product_uom_id.rounding):
                    production.state = 'progress'
                elif any(not float_is_zero(move.quantity_done, precision_rounding=move.product_uom.rounding or move.product_id.uom_id.rounding) for move in production.move_raw_ids if move.product_id):
                    production.state = 'progress'
 
    def action_assign_serial_number(self):
        company = self.company_id
        assign_serial = self.env['stock.assign.serial']
        # if self.count_assign_serial_button_click >= 0:
        #     self.count_assign_serial_button_click = 1
        if self.product_id.sh_auto_assign_serial_no and self.sh_produce_qty <= 0:
            raise ValidationError(_("Produce Quantity must be greater than 0."))
        
        if self.sh_serial_no_type == 'type1':
            if not company.sh_prefix_type1:
                raise ValidationError('Please First Add Prefix for Type 1')
            
            number_of_degit = company.sh_number_of_degit_type1
            prefix = company.sh_prefix_type1
            serial_type = 'type1'

            exist_lot = self.env['stock.lot'].search([
                ('sh_config_prifix_type', '=', prefix),
                ('company_id', '=', self.company_id.id),
            ], order='id DESC', limit=1)
            exist_serial = False
            if exist_lot:
                exist_serial = self.env['stock.lot'].sh_get_next_serial(company, self.product_id,prefix,serial_type)
            
            # self.env.cr.execute("""
            #     SELECT id FROM stock_lot
            #     WHERE sh_config_prifix_type = %s AND company_id = %s
            #     ORDER BY id DESC LIMIT 1
            # """, (prefix, company.id))
            # lot_res = self.env.cr.fetchone()
            # if lot_res:
            #     # Get the record using browse, then call the existing helper function.
            #     exist_lot = self.env['stock.lot'].browse(lot_res[0])
            #     exist_serial = exist_lot.sh_get_next_serial(company, self.product_id, prefix, serial_type)
            # else:
            #     exist_serial = False

            if not exist_serial:
                sequence = self.env['ir.sequence'].sudo().create({
                    'name': 'MRP Serial Sequence',
                    'code': 'mrp_serial_assign.serial.type1',
                    'prefix': prefix,
                    'padding': number_of_degit,
                    'number_next': 1,
                    'number_increment': 1,
                })
                # self.env.cr.execute("""
                # INSERT INTO ir_sequence (name, code, prefix, padding, number_next, number_increment)
                # VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                # """, ('MRP Serial Sequence', 'mrp_serial_assign.serial.type1', prefix, number_of_degit, 1, 1))
                # seq_id = self.env.cr.fetchone()[0]
                # sequence = self.env['ir.sequence'].browse(seq_id)
                serial = sequence.next_by_id()
            
                next_serial_number = serial
            else:
                next_serial_number = exist_serial
                
        elif self.sh_serial_no_type == 'type2':
            if not company.sh_prefix_type2:
                raise ValidationError('Please First Add Prefix for Type 2')
            
            number_of_degit = company.sh_number_of_degit_type2
            prefix = company.sh_prefix_type2
            serial_type = 'type2'
            exist_lot = self.env['stock.lot'].search([
                ('sh_config_prifix_type', '=', prefix),
                ('company_id', '=', self.company_id.id),
            ], order='id DESC', limit=1)
            exist_serial = False
            if exist_lot:
                exist_serial = self.env['stock.lot'].sh_get_next_serial(company, self.product_id,prefix,serial_type)
            # self.env.cr.execute("""
            # SELECT id FROM stock_lot
            # WHERE sh_config_prifix_type = %s AND company_id = %s
            # ORDER BY id DESC LIMIT 1
            # """, (prefix, company.id))
            # lot_res = self.env.cr.fetchone()
            # if lot_res:
            #     exist_lot = self.env['stock.lot'].browse(lot_res[0])
            #     exist_serial = exist_lot.sh_get_next_serial(company, self.product_id, prefix, serial_type)
            # else:
            #     exist_serial = False
            if not exist_serial:
                sequence = self.env['ir.sequence'].sudo().create({
                    'name': 'MRP Serial Sequence',
                    'code': 'mrp_serial_assign.serial.type2',
                    'prefix': prefix,
                    'padding': number_of_degit,
                    'number_next': 1,
                    'number_increment': 1,
                })
                # self.env.cr.execute("""
                # INSERT INTO ir_sequence (name, code, prefix, padding, number_next, number_increment)
                # VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                # """, ('MRP Serial Sequence', 'mrp_serial_assign.serial.type2', prefix, number_of_degit, 1, 1))
                # seq_id = self.env.cr.fetchone()[0]
                # sequence = self.env['ir.sequence'].browse(seq_id)
                serial = sequence.next_by_id()
            
                next_serial_number = serial
            else:
                next_serial_number = exist_serial
        else:
            return False
        # apply_serial = assign_serial.create({
        # 'production_id': self.id,
        # 'next_serial_count': self.product_qty,
        # 'produced_qty': self.product_qty,
        # 'expected_qty': self.product_qty,
        # 'next_serial_number': next_serial_number,
        # })
        record_id = self.id
        if self.procurement_group_id.mrp_production_ids:
            to_confirmed_productions = self.procurement_group_id.mrp_production_ids.filtered(
                lambda production: production.state == 'confirmed'
            )

            # record_id = to_confirmed_productions[0].id
            if to_confirmed_productions:
                record_id = to_confirmed_productions[0].id
            else:
                record_id = self.id
    
        self.env.cr.execute("""
        INSERT INTO stock_assign_serial (production_id, next_serial_count, produced_qty, expected_qty, next_serial_number)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
        """, (record_id, self.sh_produce_qty, self.sh_produce_qty, self.sh_produce_qty, next_serial_number))
        assign_serial_id = self.env.cr.fetchone()[0]
        apply_serial = self.env['stock.assign.serial'].browse(assign_serial_id)
        apply_serial.generate_serial_numbers_production()
        apply_serial.apply()
        if self.sh_produce_qty > 0 and self.procurement_group_id:
            done_production = 1
            mrp_production_ids = self.procurement_group_id.mrp_production_ids.filtered(
                lambda production: production.state not in  ['partially_done','done']
            )
            for production in mrp_production_ids:
               

                if done_production <= self.sh_produce_qty:
                    production.button_mark_done()
                    done_production += 1
        # else:
        #     if self.sh_produce_qty > 0 and self.procurement_group_id:
        #         to_close_productions = self.procurement_group_id.mrp_production_ids.filtered(
        #             lambda production: production.state == 'to_close'
        #         )
        #         done_production = 1
        #         for production in to_close_productions:
        #             if done_production <= self.sh_produce_qty:
        #                 production.button_mark_done()
        #                 done_production += 1

        if self.procurement_group_id:
            done_productions = self.procurement_group_id.mrp_production_ids.filtered(
                lambda production: production.state in  ['partially_done','done']
            )
            lots = []
            if done_productions:
                for production in done_productions:
                    lots.append(production.lot_producing_id.id)
                
     
            existing_record = self.env['sh.finished.product'].search([('production_id', '=', self.id)],limit=1)
            if existing_record:
                existing_record.write({
                    'name': self.name,
                    'sh_product_qty': existing_record.sh_product_qty + self.sh_produce_qty,
                    'lot_ids': [(4, lot_id) for lot_id in lots],
                })
            else:
                self.sh_finished_product_ids = [(0, 0, {
                    'name': self.name,
                    'product_id': self.product_id.id,
                    'sh_product_qty': self.sh_produce_qty,
                    'production_id': self.id,  
                    'lot_ids': [(4, lot_id) for lot_id in lots],
                })]
        if self.sh_main_mo:
            self.sh_remaining_qty = self.sh_total_qty - len(self.sh_finished_product_ids.lot_ids)
          
        if self.sh_main_mo and self.sh_finished_product_ids and self.sh_total_qty != len(self.sh_finished_product_ids.lot_ids):
                self.sh_partially_done = True
        else:
            self.sh_partially_done = False
            self.state = 'done'
            # self.button_mark_done()
        qty = len(self.procurement_group_id.mrp_production_ids) if self.procurement_group_id else ''
        base = re.sub(r"\s*\([^)]*\)\s*$", "", self.name or "")
        self.name = f"{base} ({qty})"


    @api.model
    def _auto_update_mo_sequence(self):
        main_mos = self.search([
            ('sh_main_mo', '=', True),
            ('company_id', '=', self.env.company.id),
        ])
        for mo in main_mos:
            if not mo.name:
                # skip blank‐named MOs
                continue
            qty = len(mo.procurement_group_id.mrp_production_ids) if mo.procurement_group_id else 0
            base = re.sub(r"\s*\([^)]*\)\s*$", "", mo.name)
            new_name = f"{base} ({qty})"
            if new_name != mo.name:
                mo.name = new_name

      