from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    transferred_from_pdi = fields.Boolean(string="Transferred from PDI", default=False)
    transferred_from_fg = fields.Boolean(string="Transferred from FG", default=False)


class PDITOFG(models.TransientModel):
    _name = 'pdi.to.fg'
    _description = 'PDI to FG Transfer'

    # def open_quants(self):
    #     """
    #         Open quants related to PDI locations with serial numbers and completed manufacturing orders
    #     """
    #     IrConfigParam = self.env['ir.config_parameter']
    #     action_lines = self.env.ref('orion_inventory_product_transfer.action_quant_transfer_pdifg')
    #     td_manufactured_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_manufactured_location_id')
    #     td_fg_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_fg_location_id')
    #     if not td_manufactured_location_id:
    #         raise UserError(_('Please configure "Route Transfer Locations" from inventory > setting menu!'))
    #     if not td_fg_location_id:
    #         raise UserError(_('Please configure "Route Transfer Locations" from inventory > setting menu!'))
    #
    #     # Get completed manufacturing orders
    #     completed_mo_products = []
    #     manufacturing_orders = self.env['mrp.production'].search([
    #         ('state', '=', 'done'),  # Only completed orders
    #     ])
    #
    #     # Extract product IDs from completed manufacturing orders
    #     for mo in manufacturing_orders:
    #         if mo.product_id:
    #             completed_mo_products.append(mo.product_id.id)
    #
    #     action = action_lines.read()[0]
    #     # Filter by both location and products from completed manufacturing orders
    #     domain = [
    #         ('location_id', '=', int(td_manufactured_location_id)),
    #         ('transferred_from_pdi', '=', False)  # Exclude transferred quants
    #     ]
    #
    #     # Add product filter only if we have completed manufacturing orders
    #     if completed_mo_products:
    #         domain.append(('product_id', 'in', completed_mo_products))
    #
    #     action['domain'] = domain
    #     action['context'] = {
    #         'search_default_productgroup': 1
    #     }
    #     return action
    def open_quants(self):
        """
        Open all serial numbers available in PDI location
        """
        IrConfigParam = self.env['ir.config_parameter']
        action_lines = self.env.ref(
            'orion_inventory_product_transfer.action_quant_transfer_pdifg'
        )

        td_manufactured_location_id = IrConfigParam.get_param(
            'orion_inventory_product_transfer.td_manufactured_location_id'
        )

        td_fg_location_id = IrConfigParam.get_param(
            'orion_inventory_product_transfer.td_fg_location_id'
        )

        if not td_manufactured_location_id:
            raise UserError(
                _('Please configure "Route Transfer Locations" from Inventory > Settings!')
            )

        if not td_fg_location_id:
            raise UserError(
                _('Please configure "Route Transfer Locations" from Inventory > Settings!')
            )

        action = action_lines.read()[0]

        domain = [
            ('location_id', '=', int(td_manufactured_location_id)),
            ('transferred_from_pdi', '=', False),
            ('lot_id', '!=', False),
            ('quantity', '>', 0),
        ]

        action['domain'] = domain

        action['context'] = {
            'search_default_productgroup': 1
        }

        return action

class PDITOFGTransfer(models.TransientModel):
    _name = 'pdi.to.fg.transfer'
    _description = 'PDI to FG Transfer Process'

    def _default_serials(self):
        """
        Generate a detailed message about selected quants and their serial numbers
        """
        quant_ids = self._context.get('active_ids', []) or []
        quant_records = self.env['stock.quant'].browse(quant_ids)

        # Prepare detailed serial information
        serial_details = []
        for quant in quant_records:
            if quant.lot_id:
                serial_details.append(f"{quant.product_id.name}: {quant.lot_id.name} (Qty: {quant.quantity})")

        # Format the message
        if serial_details:
            message = "Below serial numbers will transfer from PDI to FG, are you sure?\n\n" + "\n".join(serial_details)
        else:
            message = "There is no serials/lot for selected products."

        return message

    total_serials = fields.Text(default=_default_serials, readonly=True)

    @api.model
    def _get_picking_internal(self):
        """
            Find internal type from source location
        """
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'internal'), ('warehouse_id', '=', False)])
            if not types:
                raise UserError(
                    _("Make sure you have at least an internal picking type defined.\n For that you have to activate 'Advanced routing of products using rules' from inventory setting."))
        return types and types[0] or False

    @api.model
    def _get_locations(self):
        IrConfigParam = self.env['ir.config_parameter']
        model_location = self.env['stock.location'].sudo()
        td_manufactured_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_manufactured_location_id')
        td_fg_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_fg_location_id')
        source_location = model_location.browse(int(td_manufactured_location_id))
        destination_location = model_location.browse(int(td_fg_location_id))
        return source_location.id, destination_location.id, \
            source_location.display_name, destination_location.display_name

    @api.model
    def _create_picking_vals(self):
        internal_type = self._get_picking_internal()
        source_id, dest_id, source_name, dest_name = self._get_locations()
        return {
            'origin': source_name + '>>' + dest_name + '(By ' + self.env.user.name + ')',
            'company_id': self.env.user.company_id.id,
            'picking_type_id': internal_type.id,
            'location_dest_id': dest_id,
            'location_id': source_id,
            'move_type': 'direct',  # Added for Odoo 16
        }

    @api.model
    def _move_lines(self, pick_id, quant):
        source_id, dest_id, source_name, dest_name = self._get_locations()
        return {
            'name': source_name + '>>' + dest_name + '(' + quant.product_id.name + ')',
            'product_id': quant.product_id.id,
            'product_uom': quant.product_id.uom_id.id,
            'product_uom_qty': quant.quantity,  # Changed from qty to quantity for Odoo 16
            'date': fields.Datetime.now(),  # Updated for Odoo 16
            'company_id': self.env.user.company_id.id,  # Updated for Odoo 16
            'state': 'draft',
            'location_id': source_id,
            'location_dest_id': dest_id,
            'picking_id': pick_id
        }

    @api.model
    def _check_warning(self):
        model_config = self.env['ir.config_parameter']
        model_quant = self.env['stock.quant'].sudo()
        td_manufactured_location_id = model_config.get_param('orion_inventory_product_transfer.td_manufactured_location_id')
        td_fg_location_id = model_config.get_param('orion_inventory_product_transfer.td_fg_location_id')
        if not td_manufactured_location_id:
            raise UserError(_('Please configure "Route Transfer Locations" from inventory > setting menu!'))
        if not td_fg_location_id:
            raise UserError(_('Please configure "Route Transfer Locations" from inventory > setting menu!'))
        active_recs = self._context.get('active_ids', []) or []
        all_locations = list(set([x.location_id.id for x in model_quant.browse(active_recs)]))
        if len(all_locations) > 1 or (not all_locations):
            raise UserError(_('Wrong selection, please refresh & try again!'))
        if len(all_locations) == 1 and all_locations[0] != int(td_manufactured_location_id):
            raise UserError(_('Wrong selection, please refresh & try again!'))


    def action_transfer(self):
        self.ensure_one()
        self._check_warning()

        picking_model = self.env['stock.picking'].sudo()
        move_model = self.env['stock.move'].sudo()
        move_line_model = self.env['stock.move.line'].sudo()
        quant_model = self.env['stock.quant'].sudo()

        # First picking: PDI → FG
        pick_vals_1 = self._create_picking_vals()
        pick_1 = picking_model.create(pick_vals_1)
        active_quant_ids = self._context.get('active_ids', [])
        quant_records = quant_model.browse(active_quant_ids)

        for quant in quant_records:
            # Create stock.move
            move = move_model.create({
                'name': 'PDI >> FG (%s)' % quant.product_id.name,
                'product_id': quant.product_id.id,
                'product_uom': quant.product_id.uom_id.id,
                'product_uom_qty': quant.quantity,
                'location_id': quant.location_id.id,  # current PDI location
                'location_dest_id': self._get_locations()[1],  # FG location
                'picking_id': pick_1.id,
                'company_id': self.env.user.company_id.id,
            })

            # Create stock.move.line with correct lot and qty_done
            move_line_model.create({
                'move_id': move.id,
                'picking_id': pick_1.id,
                'location_id': quant.location_id.id,
                'location_dest_id': self._get_locations()[1],
                'product_id': quant.product_id.id,
                'product_uom_id': quant.product_id.uom_id.id,
                'qty_done': quant.quantity,
                'lot_id': quant.lot_id.id,
            })

            # Set your flags only
            quant.write({
                'transferred_from_pdi': True,
                'transferred_from_fg': False,
            })

        # Confirm, assign, and mark done
        pick_1.action_confirm()
        pick_1.action_assign()
        pick_1._action_done()

        # Show success
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Products successfully transferred from PDI to FG.',
                'sticky': False,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }


class FGTOSTOCK(models.TransientModel):
    _name = 'fg.to.stock'
    _description = 'FG to Stock Transfer'

    def open_quants(self):
        """
        Open quants related to FG locations with serial numbers
        """
        IrConfigParam = self.env['ir.config_parameter']
        # CHANGED: Reference the new FG to Stock action instead of PDI to FG action
        action_lines = self.env.ref('orion_inventory_product_transfer.action_quant_transfer_fgtostock')
        td_fg_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_fg_location_id')
        if not td_fg_location_id:
            raise UserError(_('Please configure "Route Transfer Locations" from inventory>setting menu!'))

        action = action_lines.read()[0]
        action['domain'] = [
            ('location_id', '=', int(td_fg_location_id)),
            ('transferred_from_fg', '=', False)  # Only show non-transferred quants
        ]
        action['context'] = {
            'search_default_productgroup': 1,
            'search_default_available': 1  # This ensures only available quants are shown
        }
        return action



    # def open_quants(self):
    #     """
    #     Open quants related to FG locations with serial numbers
    #     """
    #     IrConfigParam = self.env['ir.config_parameter']
    #     action_lines = self.env.ref('orion_inventory_product_transfer.action_quant_transfer_pdifg')
    #     td_fg_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_fg_location_id')
    #     if not td_fg_location_id:
    #         raise UserError(_('Please configure "Route Transfer Locations" from inventory>setting menu!'))
    #
    #     action = action_lines.read()[0]
    #     action['domain'] = [
    #         ('location_id', '=', int(td_fg_location_id)),
    #         ('transferred_from_fg', '=', False)  # Only show non-transferred quants
    #     ]
    #     action['context'] = {
    #         'search_default_productgroup': 1,
    #         'search_default_available': 1  # This ensures only available quants are shown
    #     }
    #     return action


class FGTOSTOCKTransfer(models.TransientModel):
    _name = 'fg.to.stock.transfer'
    _description = 'FG to Stock Transfer Process'

    def _default_serials(self):
        """
        Generate a detailed message about selected quants and their serial numbers
        """
        quant_ids = self._context.get('active_ids', []) or []
        quant_records = self.env['stock.quant'].browse(quant_ids)

        # Prepare detailed serial information
        serial_details = []
        for quant in quant_records:
            if quant.lot_id:
                serial_details.append(f"{quant.lot_id.name}")

        # Format the message
        if serial_details:
            message = "Below serial numbers will transfer from FG to Stock, are you sure?\n\n" + ", ".join(
                serial_details)
        else:
            message = "There is no serials/lot for selected products."

        return message

    total_serials = fields.Text(default=_default_serials, readonly=True)

    @api.model
    def _get_picking_internal(self):
        """
            Find internal type from source location
        """
        type_obj = self.env['stock.picking.type']
        company_id = self.env.context.get('company_id') or self.env.user.company_id.id
        types = type_obj.search([('code', '=', 'internal'), ('warehouse_id.company_id', '=', company_id)])
        if not types:
            types = type_obj.search([('code', '=', 'internal'), ('warehouse_id', '=', False)])
            if not types:
                raise UserError(
                    _("Make sure you have at least an internal picking type defined.\n For that you have to activate 'Advanced routing of products using rules' from inventory setting."))
        return types and types[0] or False

    @api.model
    def _get_locations(self):
        IrConfigParam = self.env['ir.config_parameter']
        model_location = self.env['stock.location'].sudo()
        td_fglocation_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_fg_location_id')
        td_stocklocation_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_stock_location_id')
        source_location = model_location.browse(int(td_fglocation_id))
        destination_location = model_location.browse(int(td_stocklocation_id))
        return source_location.id, destination_location.id, \
            source_location.display_name, destination_location.display_name

    @api.model
    def _create_picking_vals(self):
        internal_type = self._get_picking_internal()
        source_id, dest_id, source_name, dest_name = self._get_locations()
        return {
            'origin': source_name + '>>' + dest_name + '(By ' + self.env.user.name + ')',
            'company_id': self.env.user.company_id.id,
            'picking_type_id': internal_type.id,
            'location_dest_id': dest_id,
            'location_id': source_id,
            'move_type': 'direct',  # Added for Odoo 16
        }


    @api.model
    def _move_lines(self, pick_id, quant):
        source_id, dest_id, source_name, dest_name = self._get_locations()
        move_vals = {
            'name': source_name + '>>' + dest_name + '(' + quant.product_id.name + ')',
            'product_id': quant.product_id.id,
            'product_uom': quant.product_id.uom_id.id,
            'product_uom_qty': quant.quantity,
            'location_id': source_id,
            'location_dest_id': dest_id,
            'picking_id': pick_id,
            'state': 'draft',
            'company_id': self.env.user.company_id.id,
        }
        move = self.env['stock.move'].create(move_vals)

        # Create move line directly with lot and qty_done
        self.env['stock.move.line'].create({
            'move_id': move.id,
            'picking_id': pick_id,
            'location_id': source_id,
            'location_dest_id': dest_id,
            'product_id': quant.product_id.id,
            'product_uom_id': quant.product_id.uom_id.id,
            'qty_done': quant.quantity,
            'lot_id': quant.lot_id.id,
        })

        return move

    @api.model
    def _check_warning(self):
        model_config = self.env['ir.config_parameter']
        model_quant = self.env['stock.quant'].sudo()
        td_fglocation_id = model_config.get_param('orion_inventory_product_transfer.td_fg_location_id')
        td_stocklocation_id = model_config.get_param('orion_inventory_product_transfer.td_stock_location_id')

        if not td_fglocation_id:
            raise UserError(_('Please configure "Route Transfer Locations" from inventory > setting menu!'))
        if not td_stocklocation_id:
            raise UserError(_('Please configure "Route Transfer Locations" from inventory > setting menu!'))
        active_recs = self._context.get('active_ids', []) or []
        all_locations = list(set([x.location_id.id for x in model_quant.browse(active_recs)]))
        if len(all_locations) > 1 or (not all_locations):
            raise UserError(_('Wrong selection, please refresh & try again!'))
        if len(all_locations) == 1 and all_locations[0] != int(td_fglocation_id):
            raise UserError(_('Wrong selection, please refresh & try again!'))

    def action_transfer(self):
        self.ensure_one()
        self._check_warning()

        StockPicking = self.env['stock.picking'].sudo()
        StockQuant = self.env['stock.quant'].sudo()
        StockMove = self.env['stock.move'].sudo()
        StockMoveLine = self.env['stock.move.line'].sudo()

        # Get locations
        source_location_id, dest_location_id, _, _ = self._get_locations()

        # Create the picking
        picking = StockPicking.create(self._create_picking_vals())
        quant_ids = self._context.get('active_ids', [])
        quants = StockQuant.browse(quant_ids)

        # Store product and lot information for each quant
        product_lot_pairs = []

        # Verify all quants are in the correct source location
        for quant in quants:
            if quant.location_id.id != source_location_id:
                raise UserError("Selected quant %s is not in the expected FG location!" % quant.display_name)
            product_lot_pairs.append((quant.product_id.id, quant.lot_id.id))

            # Create the move
            move = StockMove.create({
                'name': f"FG->STOCK: {quant.product_id.name}",
                'product_id': quant.product_id.id,
                'product_uom': quant.product_id.uom_id.id,
                'product_uom_qty': quant.quantity,
                'location_id': source_location_id,
                'location_dest_id': dest_location_id,
                'picking_id': picking.id,
                'state': 'draft',
                'origin': picking.origin,
            })

            # Create move line with all details
            StockMoveLine.create({
                'move_id': move.id,
                'product_id': quant.product_id.id,
                'product_uom_id': quant.product_id.uom_id.id,
                'location_id': source_location_id,
                'location_dest_id': dest_location_id,
                'lot_id': quant.lot_id.id,
                'qty_done': quant.quantity,
                'picking_id': picking.id,
                'owner_id': quant.owner_id.id if quant.owner_id else False,
            })

        # Process the transfer
        picking.action_confirm()
        picking.action_assign()
        picking._action_done()

        # Now COMPLETELY remove the quants from the source location
        self.env.cr.execute("""
            DELETE FROM stock_quant 
            WHERE location_id = %s 
            AND product_id IN %s
            AND lot_id IN %s
        """, (
            source_location_id,
            tuple([p[0] for p in product_lot_pairs]) if product_lot_pairs else (0,),
            tuple([l[1] for l in product_lot_pairs]) if product_lot_pairs else (0,),
        ))

        # Make sure quants in destination have the correct flags
        for product_id, lot_id in product_lot_pairs:
            dest_quants = StockQuant.search([
                ('product_id', '=', product_id),
                ('lot_id', '=', lot_id),
                ('location_id', '=', dest_location_id)
            ])

            if dest_quants:
                dest_quants.write({
                    'transferred_from_pdi': True,
                    'transferred_from_fg': True
                })

        # Return success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Success',
                'message': 'Products fully transferred to Stock. Picking: ' + picking.name,
                'sticky': False,
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }