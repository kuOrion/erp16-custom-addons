#
# from odoo import api, fields, models
# import logging
# import re
# from collections import defaultdict
#
# _logger = logging.getLogger(__name__)
#
#
# class MfgDone(models.TransientModel):
#     _name = "mfgdone"
#     _description = "Manufactured Goods Reports"
#
#     from_date = fields.Date('From', default=fields.Date.context_today)
#     to_date = fields.Date('To', default=fields.Date.context_today)
#     order_type = fields.Selection([
#         ('all', 'All Orders'),
#         ('domestic', 'Domestic Orders'),
#         ('export', 'Export Orders')
#     ], string='Order Type', default='all', required=True)
#     customer_id = fields.Many2one('res.partner', string='Customer')
#     product_id = fields.Many2one('product.product', string='Product')
#     total_quantity = fields.Float(compute='_compute_total_quantity', string='Total Quantity')
#
#     @api.depends('from_date', 'to_date', 'order_type', 'customer_id', 'product_id')
#     def _compute_total_quantity(self):
#         for record in self:
#             mfg_orders = record.get_mfg_done()
#             record.total_quantity = sum(order.product_qty for order in mfg_orders)
#
#     def get_mfg_done(self):
#         """Fetches MRP Orders in 'done' state within the given date range."""
#         domain = [
#             ('state', '=', 'done'),
#             ('date_finished', '>=', self.from_date),
#             ('date_finished', '<=', self.to_date),
#         ]
#
#         if self.product_id:
#             domain.append(('product_id', '=', self.product_id.id))
#
#         mfg_orders = self.env['mrp.production'].search(domain)
#
#         if self.customer_id:
#             mfg_orders = mfg_orders.filtered(lambda o: o.partner_id and o.partner_id.id == self.customer_id.id)
#
#         if self.order_type != 'all':
#             filtered_orders = self.env['mrp.production']
#             for order in mfg_orders:
#                 if not order.partner_id or not order.partner_id.country_id:
#                     continue
#                 if self.order_type == 'domestic' and order.partner_id.country_id.code == 'IN':
#                     filtered_orders |= order
#                 elif self.order_type == 'export' and order.partner_id.country_id.code != 'IN':
#                     filtered_orders |= order
#             return filtered_orders
#
#         return mfg_orders
#
#     def _extract_number(self, serial):
#         """Extracts numeric part from a serial number for sequencing."""
#         # Look for numbers in the serial string
#         numbers = re.findall(r'\d+', serial)
#         return int(numbers[-1]) if numbers else 0
#
#     def _format_serial_numbers(self, serials):
#         """Formats serial numbers into ranges when sequential"""
#         if not serials:
#             return ""
#
#         try:
#             # Natural sort for alphanumeric serials
#             serials.sort(key=lambda x: [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', x)])
#         except:
#             serials.sort()
#
#         # Group sequential serials
#         groups = []
#         current_group = [serials[0]]
#
#         for i in range(1, len(serials)):
#             prev_num = self._extract_number(serials[i - 1])
#             curr_num = self._extract_number(serials[i])
#
#             if curr_num == prev_num + 1:
#                 current_group.append(serials[i])
#             else:
#                 groups.append(current_group)
#                 current_group = [serials[i]]
#
#         groups.append(current_group)
#
#         # Format groups
#         formatted = []
#         for group in groups:
#             if len(group) > 1:
#                 formatted.append(f"{group[0]} TO {group[-1]}")
#             else:
#                 formatted.append(group[0])
#
#         return "\n".join(formatted)
#
#     # def get_grouped_mfg_done(self):
#     #     """
#     #     Returns one consolidated record per procurement group (or MO if no group).
#     #     Groups serial numbers, quantities, and references into a single line.
#     #     """
#     #     result = []
#     #     mfg_orders = self.get_mfg_done()
#     #
#     #     grouped_data = {}
#     #
#     #     for order in mfg_orders:
#     #         key = order.procurement_group_id.id or order.id  # Group by procurement group, fallback to MO ID
#     #
#     #         if key not in grouped_data:
#     #             grouped_data[key] = {
#     #                 'product': order.product_id,
#     #                 'serials': set(),
#     #                 'total_qty': 0.0,
#     #                 'total_order_qty': 0.0,
#     #                 'remaining_qty': 0.0,
#     #                 'mfg_refs': [],
#     #                 'sale_refs': [],
#     #                 'custom_order_refs': [],
#     #                 'specifications': [],
#     #             }
#     #
#     #         grouped_data[key]['serials'].update(order.get_mfg_serial_list())
#     #         grouped_data[key]['total_qty'] = order.sh_produce_qty or 0.0
#     #         grouped_data[key]['total_order_qty'] = order.sh_total_qty or 0.0
#     #         grouped_data[key]['remaining_qty'] = order.sh_remaining_qty or 0.0
#     #         grouped_data[key]['mfg_refs'].append(order.name)
#     #
#     #         if order.origin and order.origin.startswith('SO'):
#     #             grouped_data[key]['sale_refs'].append(order.origin)
#     #
#     #         if order.order_id:
#     #             grouped_data[key]['custom_order_refs'].append(order.order_id.name)
#     #
#     #         if order.product_speci:
#     #             grouped_data[key]['specifications'].append(order.product_speci)
#     #
#     #
#     #     # Convert grouped data into final result list
#     #     for data in grouped_data.values():
#     #         serial_range = self._format_serial_numbers(list(data['serials']))
#     #         result.append({
#     #             'product': data['product'],
#     #             'serial_range': serial_range,
#     #             'total_qty': data['total_qty'],
#     #             'produce_qty': data['total_qty'],
#     #             'total_order_qty': data['total_order_qty'],
#     #             'remaining_qty': data['remaining_qty'],
#     #             'individual_mo_quantities': ", ".join([f"{ref}" for ref in data['mfg_refs']]),
#     #             'mfg_refs': ", ".join(data['mfg_refs']),
#     #             'sale_refs': ", ".join(set(data['sale_refs'])),  # Remove duplicates
#     #             'custom_order_refs': ", ".join(set(data['custom_order_refs'])),
#     #             'specification': "\n".join(set(data['specifications'])),
#     #         })
#     #
#     #     return result
#
#     def get_grouped_mfg_done(self):
#         """
#         Returns one consolidated record per procurement group (or MO if no group).
#         Groups serial numbers, quantities, and references into a single line.
#         """
#         result = []
#         mfg_orders = self.get_mfg_done()
#
#         grouped_data = {}
#
#         for order in mfg_orders:
#             # Use procurement group as key, or MO ID if no group
#             key = order.procurement_group_id.id or order.id
#
#             if key not in grouped_data:
#                 grouped_data[key] = {
#                     'product': order.product_id,
#                     'serials': set(),
#                     'total_qty': 0.0,  # Total quantity produced across all related MOs
#                     'total_order_qty': 0.0,  # Original ordered quantity
#                     'remaining_qty': 0.0,  # Remaining quantity to produce
#                     'mfg_refs': [],
#                     'sale_refs': [],
#                     'custom_order_refs': [],
#                     'specifications': [],
#                 }
#
#             # Get ALL serial numbers from this procurement group
#             all_serials = order.get_mfg_serial_list()
#             grouped_data[key]['serials'].update(all_serials)
#
#             # Sum quantities from all related MOs in this procurement group
#             if order.procurement_group_id:
#                 # Find all MOs in this procurement group (including non-done ones)
#                 all_group_mos = self.env['mrp.production'].search([
#                     ('procurement_group_id', '=', order.procurement_group_id.id),
#                     ('product_id', '=', order.product_id.id),
#                 ])
#
#                 # Sum quantities from all MOs in the group
#                 total_produced = sum(mo.qty_produced for mo in all_group_mos)
#                 total_ordered = sum(mo.product_qty for mo in all_group_mos)
#                 remaining = total_ordered - total_produced
#
#                 grouped_data[key]['total_qty'] = total_produced
#                 grouped_data[key]['total_order_qty'] = total_ordered
#                 grouped_data[key]['remaining_qty'] = remaining
#             else:
#                 # For MOs without procurement group, use individual MO quantities
#                 grouped_data[key]['total_qty'] += order.qty_produced
#                 grouped_data[key]['total_order_qty'] += order.product_qty
#                 grouped_data[key]['remaining_qty'] += (order.product_qty - order.qty_produced)
#
#             # Collect references
#             grouped_data[key]['mfg_refs'].append(order.name)
#
#             if order.origin and order.origin.startswith('SO'):
#                 grouped_data[key]['sale_refs'].append(order.origin)
#
#             if order.order_id:
#                 grouped_data[key]['custom_order_refs'].append(order.order_id.name)
#
#             if order.product_speci:
#                 grouped_data[key]['specifications'].append(order.product_speci)
#
#         # Convert grouped data into final result list
#         for data in grouped_data.values():
#             serial_range = self._format_serial_numbers(list(data['serials']))
#             result.append({
#                 'product': data['product'],
#                 'serial_range': serial_range,
#                 'total_qty': data['total_qty'],
#                 'produce_qty': data['total_qty'],
#                 'total_order_qty': data['total_order_qty'],
#                 'remaining_qty': data['remaining_qty'],
#                 'individual_mo_quantities': ", ".join([f"{ref}" for ref in data['mfg_refs']]),
#                 'mfg_refs': ", ".join(data['mfg_refs']),
#                 'sale_refs': ", ".join(set(data['sale_refs'])),  # Remove duplicates
#                 'custom_order_refs': ", ".join(set(data['custom_order_refs'])),
#                 'specification': "\n".join(set(data['specifications'])),
#             })
#
#         return result
#
#     def get_individual_mfg_done(self):
#         """
#         Alternative method: Returns individual MO records without any grouping
#         """
#         result = []
#         mfg_orders = self.get_mfg_done()
#
#         for order in mfg_orders:
#             result.append({
#                 'mo_name': order.name,
#                 'product': order.product_id,
#                 'product_name': order.product_id.name,
#                 'quantity': order.sh_produce_qty or 0.0,
#                 'qty_produced': order.qty_produced,
#                 'total_order_qty': order.sh_total_qty or 0.0,  # ✅ ADD THIS
#                 'remaining_qty': order.sh_remaining_qty or 0.0,  # ✅ ADD THIS
#                 'serial_numbers': ", ".join(order.get_mfg_serial_list()),
#                 'sale_order': order.origin if order.origin and order.origin.startswith('SO') else '',
#                 'custom_order': order.order_id.name if order.order_id else '',
#                 'specification': order.product_speci or '',
#                 'date_finished': order.date_finished,
#                 'partner': order.partner_id.name if order.partner_id else '',
#             })
#
#         return result
#
#
#     def create_mfgdone_report(self):
#         """Generates a Py3O report for manufactured goods."""
#         return {
#             'type': 'ir.actions.report',
#             'report_name': 'orion_manufacturing_done_report.py3o_mfgdone',
#             'model': 'mfgdone',
#             'report_type': 'py3o',
#             'context': {'active_id': self.id, 'active_ids': [self.id]}
#         }
#
#     def create_mfgdone_treeview(self):
#         """Displays a tree view of manufactured goods."""
#         mfg_orders = self.get_mfg_done()
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Manufactured Goods Report',
#             'res_model': 'mrp.production',
#             'domain': [('id', 'in', mfg_orders.ids)],
#             'view_mode': 'tree',
#             'views': [(self.env.ref('orion_manufacturing_done_report.view_mfg_done_tree').id, 'tree')],
#             'target': 'self',
#         }
#
# class MrpProduction(models.Model):
#     _inherit = 'mrp.production'
#
#     partner_id = fields.Many2one('res.partner', string='Customer',
#                                  compute='_compute_partner_id', store=True)
#
#     @api.depends('origin')
#     def _compute_partner_id(self):
#         for record in self:
#             if record.origin and 'OA' in record.origin:
#                 sale_order = self.env['sale.order'].search([('name', '=', record.origin)], limit=1)
#                 if sale_order and sale_order.partner_id:
#                     record.partner_id = sale_order.partner_id
#                     continue
#             record.partner_id = False
#
#     def get_mfg_serial_list(self):
#         """Return serial numbers across this MO and all related backorders."""
#         serials = set()
#
#         def collect_serials(mo):
#             # Collect from all finished moves, regardless of state
#             for move in mo.move_finished_ids:
#                 for line in move.move_line_ids:
#                     if line.lot_id:
#                         serials.add(line.lot_id.name)
#
#         # 1️⃣ Collect from current MO
#         collect_serials(self)
#
#         # 2️⃣ Collect from related MOs (backorders)
#         if self.procurement_group_id:
#             related_mos = self.env['mrp.production'].search([
#                 ('procurement_group_id', '=', self.procurement_group_id.id),
#                 ('product_id', '=', self.product_id.id),
#             ])
#             for mo in related_mos:
#                 if mo.id != self.id:
#                     collect_serials(mo)
#
#         # 3️⃣ Fallback: directly look up stock moves with same procurement group
#         if self.procurement_group_id:
#             stock_moves = self.env['stock.move'].search([
#                 ('group_id', '=', self.procurement_group_id.id),
#                 ('product_id', '=', self.product_id.id),
#             ])
#             for move in stock_moves:
#                 for line in move.move_line_ids:
#                     if line.lot_id:
#                         serials.add(line.lot_id.name)
#
#         return sorted(serials)


from odoo import api, fields, models
import logging
import re
from collections import defaultdict

_logger = logging.getLogger(__name__)


class MfgDone(models.TransientModel):
    _name = "mfgdone"
    _description = "Manufactured Goods Reports"

    from_date = fields.Date('From', default=fields.Date.context_today)
    to_date = fields.Date('To', default=fields.Date.context_today)
    order_type = fields.Selection([
        ('all', 'All Orders'),
        ('domestic', 'Domestic Orders'),
        ('export', 'Export Orders')
    ], string='Order Type', default='all', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer')
    product_id = fields.Many2one('product.product', string='Product')
    total_quantity = fields.Float(compute='_compute_total_quantity', string='Total Quantity')

    @api.depends('from_date', 'to_date', 'order_type', 'customer_id', 'product_id')
    def _compute_total_quantity(self):
        for record in self:
            mfg_orders = record.get_mfg_done()
            record.total_quantity = sum(order.product_qty for order in mfg_orders)

    def get_mfg_done(self):
        """Fetches MRP Orders in 'done' state within the given date range."""
        domain = [
            ('state', '=', 'done'),
            ('date_finished', '>=', self.from_date),
            ('date_finished', '<=', self.to_date),
        ]

        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))

        mfg_orders = self.env['mrp.production'].search(domain)

        if self.customer_id:
            mfg_orders = mfg_orders.filtered(lambda o: o.partner_id and o.partner_id.id == self.customer_id.id)

        if self.order_type != 'all':
            filtered_orders = self.env['mrp.production']
            for order in mfg_orders:
                if not order.partner_id or not order.partner_id.country_id:
                    continue
                if self.order_type == 'domestic' and order.partner_id.country_id.code == 'IN':
                    filtered_orders |= order
                elif self.order_type == 'export' and order.partner_id.country_id.code != 'IN':
                    filtered_orders |= order
            return filtered_orders

        return mfg_orders

    def _extract_number(self, serial):
        """Extracts numeric part from a serial number for sequencing."""
        numbers = re.findall(r'\d+', serial)
        return int(numbers[-1]) if numbers else 0

    def _format_serial_numbers(self, serials):
        """Formats serial numbers into ranges when sequential."""
        if not serials:
            return ""

        try:
            serials.sort(key=lambda x: [int(c) if c.isdigit() else c.lower() for c in re.split('([0-9]+)', x)])
        except:
            serials.sort()

        groups = []
        current_group = [serials[0]]

        for i in range(1, len(serials)):
            prev_num = self._extract_number(serials[i - 1])
            curr_num = self._extract_number(serials[i])

            if curr_num == prev_num + 1:
                current_group.append(serials[i])
            else:
                groups.append(current_group)
                current_group = [serials[i]]

        groups.append(current_group)

        formatted = []
        for group in groups:
            if len(group) > 1:
                formatted.append(f"{group[0]} TO {group[-1]}")
            else:
                formatted.append(group[0])

        return "\n".join(formatted)

    def _get_main_mo_name(self, mo_names):
        """
        Returns the main/parent MO number from a list of MO names.
        In Odoo, backorders are suffixed like WH/MO/00123-001, WH/MO/00123-002.
        The parent MO has no such suffix (e.g. WH/MO/00123).
        Falls back to the first name alphabetically if all are backorders.
        """
        # Sort so parent MO (no suffix) comes first alphabetically
        sorted_names = sorted(mo_names)
        # Find a name that does NOT end with -001, -002, etc.
        main_mo = next(
            (name for name in sorted_names if not re.search(r'-\d+$', name)),
            sorted_names[0]  # fallback: first alphabetically
        )
        return main_mo

    def get_grouped_mfg_done(self):
        """
        Returns one consolidated record per procurement group (or MO if no group).
        Groups serial numbers, quantities, and references into a single line.
        Shows only the main/parent MO number in mfg_refs.
        """
        result = []
        mfg_orders = self.get_mfg_done()

        grouped_data = {}

        for order in mfg_orders:
            # Use procurement group as key, or MO ID if no group
            key = order.procurement_group_id.id or order.id

            if key not in grouped_data:
                grouped_data[key] = {
                    'product': order.product_id,
                    'serials': set(),
                    'total_qty': 0.0,
                    'total_order_qty': 0.0,
                    'remaining_qty': 0.0,
                    'mfg_orders': [],       # Store full order objects
                    'mfg_names': [],        # Store all MO names (for fallback/debug)
                    'sale_refs': [],
                    'custom_order_refs': [],
                    'specifications': [],
                }

            # Get ALL serial numbers from this procurement group
            all_serials = order.get_mfg_serial_list()
            grouped_data[key]['serials'].update(all_serials)

            # Track this order
            grouped_data[key]['mfg_orders'].append(order)
            grouped_data[key]['mfg_names'].append(order.name)

            # Sum quantities from all related MOs in this procurement group
            if order.procurement_group_id:
                all_group_mos = self.env['mrp.production'].search([
                    ('procurement_group_id', '=', order.procurement_group_id.id),
                    ('product_id', '=', order.product_id.id),
                ])
                total_produced = sum(mo.qty_produced for mo in all_group_mos)
                total_ordered = sum(mo.product_qty for mo in all_group_mos)
                remaining = total_ordered - total_produced

                grouped_data[key]['total_qty'] = total_produced
                grouped_data[key]['total_order_qty'] = total_ordered
                grouped_data[key]['remaining_qty'] = remaining
            else:
                grouped_data[key]['total_qty'] += order.qty_produced
                grouped_data[key]['total_order_qty'] += order.product_qty
                grouped_data[key]['remaining_qty'] += (order.product_qty - order.qty_produced)

            # Collect references
            if order.origin and order.origin.startswith('SO'):
                grouped_data[key]['sale_refs'].append(order.origin)

            if order.order_id:
                grouped_data[key]['custom_order_refs'].append(order.order_id.name)

            if order.product_speci:
                grouped_data[key]['specifications'].append(order.product_speci)

        # Convert grouped data into final result list
        for data in grouped_data.values():
            serial_range = self._format_serial_numbers(list(data['serials']))

            # ✅ Get only the main/parent MO number (no backorder suffix)
            main_mo_name = self._get_main_mo_name(data['mfg_names'])

            result.append({
                'product': data['product'],
                'serial_range': serial_range,
                'total_qty': data['total_qty'],
                'produce_qty': data['total_qty'],
                'total_order_qty': data['total_order_qty'],
                'remaining_qty': data['remaining_qty'],
                'mfg_refs': main_mo_name,                              # ✅ Single parent MO number
                'all_mfg_refs': ", ".join(data['mfg_names']),          # All MO names (for debug/reference)
                'sale_refs': ", ".join(set(data['sale_refs'])),
                'custom_order_refs': ", ".join(set(data['custom_order_refs'])),
                'specification': "\n".join(set(data['specifications'])),
            })

        return result

    def get_individual_mfg_done(self):
        """
        Alternative method: Returns individual MO records without any grouping.
        """
        result = []
        mfg_orders = self.get_mfg_done()

        for order in mfg_orders:
            result.append({
                'mo_name': order.name,
                'product': order.product_id,
                'product_name': order.product_id.name,
                'quantity': order.sh_produce_qty or 0.0,
                'qty_produced': order.qty_produced,
                'total_order_qty': order.sh_total_qty or 0.0,
                'remaining_qty': order.sh_remaining_qty or 0.0,
                'serial_numbers': ", ".join(order.get_mfg_serial_list()),
                'sale_order': order.origin if order.origin and order.origin.startswith('SO') else '',
                'custom_order': order.order_id.name if order.order_id else '',
                'specification': order.product_speci or '',
                'date_finished': order.date_finished,
                'partner': order.partner_id.name if order.partner_id else '',
            })

        return result

    def create_mfgdone_report(self):
        """Generates a Py3O report for manufactured goods."""
        return {
            'type': 'ir.actions.report',
            'report_name': 'orion_manufacturing_done_report.py3o_mfgdone',
            'model': 'mfgdone',
            'report_type': 'py3o',
            'context': {'active_id': self.id, 'active_ids': [self.id]}
        }

    def create_mfgdone_treeview(self):
        """Displays a tree view of manufactured goods."""
        mfg_orders = self.get_mfg_done()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufactured Goods Report',
            'res_model': 'mrp.production',
            'domain': [('id', 'in', mfg_orders.ids)],
            'view_mode': 'tree',
            'views': [(self.env.ref('orion_manufacturing_done_report.view_mfg_done_tree').id, 'tree')],
            'target': 'self',
        }


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner_id = fields.Many2one('res.partner', string='Customer',
                                 compute='_compute_partner_id', store=True)

    @api.depends('origin')
    def _compute_partner_id(self):
        for record in self:
            if record.origin and 'OA' in record.origin:
                sale_order = self.env['sale.order'].search([('name', '=', record.origin)], limit=1)
                if sale_order and sale_order.partner_id:
                    record.partner_id = sale_order.partner_id
                    continue
            record.partner_id = False

    def get_mfg_serial_list(self):
        """Return serial numbers across this MO and all related backorders."""
        serials = set()

        def collect_serials(mo):
            for move in mo.move_finished_ids:
                for line in move.move_line_ids:
                    if line.lot_id:
                        serials.add(line.lot_id.name)

        # Collect from current MO
        collect_serials(self)

        # Collect from related MOs (backorders)
        if self.procurement_group_id:
            related_mos = self.env['mrp.production'].search([
                ('procurement_group_id', '=', self.procurement_group_id.id),
                ('product_id', '=', self.product_id.id),
            ])
            for mo in related_mos:
                if mo.id != self.id:
                    collect_serials(mo)

        # Fallback: directly look up stock moves with same procurement group
        if self.procurement_group_id:
            stock_moves = self.env['stock.move'].search([
                ('group_id', '=', self.procurement_group_id.id),
                ('product_id', '=', self.product_id.id),
            ])
            for move in stock_moves:
                for line in move.move_line_ids:
                    if line.lot_id:
                        serials.add(line.lot_id.name)

        return sorted(serials)