
from odoo import api, fields, models
import logging

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

    def get_mfg_done(self):
        """Fetches MRP Orders in 'done' state within the given date range."""
        domain = [
            ('state', '=', 'done'),
            ('date_finished', '>=', self.from_date),
            ('date_finished', '<=', self.to_date),
        ]

        # Add product filter if specified
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))

        # Get all MRP orders that match the basic criteria
        mfg_orders = self.env['mrp.production'].search(domain)

        # Filter based on customer if specified
        if self.customer_id:
            mfg_orders = mfg_orders.filtered(lambda o: o.partner_id and o.partner_id.id == self.customer_id.id)

        # Filter based on order type
        if self.order_type != 'all':
            filtered_orders = self.env['mrp.production']
            for order in mfg_orders:
                # Skip if no partner is associated or no country is set
                if not order.partner_id or not order.partner_id.country_id:
                    continue

                # Filter based on country
                if self.order_type == 'domestic' and order.partner_id.country_id.code == 'IN':
                    filtered_orders |= order
                elif self.order_type == 'export' and order.partner_id.country_id.code != 'IN':
                    filtered_orders |= order

            return filtered_orders

        return mfg_orders

    def create_mfgdone_report(self):
        """Generates a Py3O report for manufactured goods."""
        return {
            'type': 'ir.actions.report',
            'report_name': 'orion_manufacturing_done_report.py3o_mfgdone',
            'model': 'mfgdone',
            'report_type': 'py3o',
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

    # Add partner_id as a related field if it doesn't exist already
    partner_id = fields.Many2one('res.partner', string='Customer',
                                 compute='_compute_partner_id', store=True)

    @api.depends('origin')
    def _compute_partner_id(self):
        for record in self:
            # Try to get partner from sale order if origin contains a sale order
            if record.origin and 'OA' in record.origin:
                sale_order = self.env['sale.order'].search([('name', '=', record.origin)], limit=1)
                if sale_order and sale_order.partner_id:
                    record.partner_id = sale_order.partner_id
                    continue

            # If no partner found, set to False
            record.partner_id = False

    def get_mfg_serial_no(self):
        """Fetches and formats serial numbers for finished products."""
        serials = []
        for move in self.move_finished_ids:
            for lot in move.move_line_ids:
                if lot.lot_id:
                    serials.append(lot.lot_id.name)

        if len(serials) > 1:
            return f"{serials[0]} TO {serials[-1]}"
        return " ".join(serials)