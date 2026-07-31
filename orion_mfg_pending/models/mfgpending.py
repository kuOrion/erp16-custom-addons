from odoo import api, fields, models, _
from datetime import timedelta
import logging

_logger = logging.getLogger(__name__)


class MfgPending(models.TransientModel):
    _name = "mfgpending"
    _description = "Manufacturing Pending reports"

    # Default to today's date for daily report
    from_date = fields.Date('From', default=lambda self: fields.Date.today())
    to_date = fields.Date('To', default=lambda self: fields.Date.today())
    schedule_date = fields.Date('Schedule Date')

    date_filter_type = fields.Selection([
        ('range', 'From-To Date Range'),
        ('schedule', 'From-Schedule Date Range')
    ], string="Date Filter Type", default='range', required=True)

    order_type = fields.Selection([
        ('all', 'All Pending Orders'),
        ('domestic', 'Domestic Pending Orders'),
        ('export', 'Export Pending Orders')
    ], string="Order Type", default='all', required=True)

    product_id = fields.Many2one('product.product', string='Product')
    partner_id = fields.Many2one('res.partner', string='Customer')
    mo_line_ids = fields.Many2many('mrp.production', string='MO Lines')
    group_by = fields.Selection([
        ('none', 'No Grouping'),
        ('product', 'Group by Product'),
        ('customer', 'Group by Customer')
    ], string="Group By", default='none', required=True)

    cnt = fields.Integer(string='Counter', default=0)
    tot_qty = fields.Float(string='Total Quantity', default=0.0)
    # Additional summary fields for the new quantities
    tot_produce_qty = fields.Float(string='Total Produce Quantity', default=0.0)
    tot_remaining_qty = fields.Float(string='Total Remaining Quantity', default=0.0)

    def _get_date_domain(self):
        """Helper method to get date domain based on filter type"""
        domain = []
        today = fields.Date.today()

        if self.date_filter_type == 'range':
            # Default: fetch only today's created MOs
            if self.from_date and self.to_date:
                domain.extend([
                    ('create_date', '>=', f"{self.from_date} 00:00:00"),
                    ('create_date', '<=', f"{self.to_date} 23:59:59")
                ])
            else:
                domain.extend([
                    ('create_date', '>=', f"{today} 00:00:00"),
                    ('create_date', '<=', f"{today} 23:59:59")
                ])
        elif self.date_filter_type == 'schedule' and self.schedule_date:
            # If user selects schedule date, filter on planned start
            if self.from_date:
                domain.extend([
                    ('date_planned_start', '>=', self.from_date),
                    ('date_planned_start', '<=', self.schedule_date)
                ])
        return domain

    def getOA(self):
        """Return Manufacturing Orders based on filters and grouping"""
        domain = [
            ('origin', '!=', False),
            ('state', 'not in', ['done', 'cancel']),
        ]
        domain.extend(self._get_date_domain())

        if self.group_by == 'product':
            if self.cnt < len(self.mo_line_ids):
                product_id = self.mo_line_ids[self.cnt].product_id.id
                domain.append(('product_id', '=', product_id))
            else:
                return []
        elif self.group_by == 'customer':
            if self.cnt < len(self.mo_line_ids):
                customer_id = self.mo_line_ids[self.cnt].partner_id.id
                domain.append(('partner_id', '=', customer_id))
            else:
                return []
        else:  # No grouping
            if self.cnt < len(self.mo_line_ids):
                result = [self.mo_line_ids[self.cnt]]
                self.cnt += 1
                return result
            else:
                return []

        if self.order_type == 'domestic':
            domain.append(('partner_id.country_id.code', '=', 'IN'))
        elif self.order_type == 'export':
            domain.append(('partner_id.country_id.code', '!=', 'IN'))

        if self.product_id and self.group_by != 'product':
            domain.append(('product_id', '=', self.product_id.id))
        if self.partner_id and self.group_by != 'customer':
            domain.append(('partner_id', '=', self.partner_id.id))

        line_ids = self.env['mrp.production'].search(domain)

        self.cnt += 1
        # Calculate totals including the new fields
        self.tot_qty = sum(line.product_qty for line in line_ids)
        self.tot_produce_qty = sum(line.sh_produce_qty for line in line_ids)
        self.tot_remaining_qty = sum(line.sh_remaining_qty for line in line_ids)

        return line_ids

    def _get_root_mo(self, mo):
        """Find the root MO for a given MO by traversing backorder_ids backwards"""
        current_mo = mo
        while True:
            parent_mo = self.env['mrp.production'].search([('backorder_ids', 'in', current_mo.id)], limit=1)
            if parent_mo:
                current_mo = parent_mo
            else:
                break
        return current_mo

    def getMfgPending(self):
        """Fetch all Manufacturing Orders based on filters and group by MO root name prefix"""
        self.cnt = 0
        domain = [('state', 'not in', ['done', 'cancel'])]
        domain.extend(self._get_date_domain())

        if self.order_type == 'domestic':
            domain.append(('partner_id.country_id.code', '=', 'IN'))
        elif self.order_type == 'export':
            domain.append(('partner_id.country_id.code', '!=', 'IN'))

        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        if self.partner_id:
            domain.append(('partner_id', '=', self.partner_id.id))

        _logger.info(f"Applying domain filter: {domain}")
        mo_ids = self.env['mrp.production'].search(domain, order="name, id")

        grouped_mos = {}
        for mo in mo_ids:
            # Extract root reference (everything before last dash)
            root_ref = mo.name.rsplit('-', 1)[0] if '-' in mo.name else mo.name

            if root_ref not in grouped_mos:
                grouped_mos[root_ref] = {
                    'root_ref': root_ref,
                    'lines': self.env['mrp.production'],
                    'product_qty': 0.0,
                    'produce_qty': 0.0,
                    'remaining_qty': 0.0,
                    'first_mo': mo,  # keep a reference to display in report
                }

            grouped_mos[root_ref]['lines'] |= mo
            grouped_mos[root_ref]['product_qty'] += mo.product_qty
            grouped_mos[root_ref]['produce_qty'] += mo.sh_produce_qty
            grouped_mos[root_ref]['remaining_qty'] += mo.sh_remaining_qty

        # Replace mo_line_ids with representative MO records
        self.mo_line_ids = [(6, 0, [g['first_mo'].id for g in grouped_mos.values()])]

        # Calculate totals
        self.tot_qty = sum(g['product_qty'] for g in grouped_mos.values())
        self.tot_produce_qty = sum(g['produce_qty'] for g in grouped_mos.values())
        self.tot_remaining_qty = sum(g['remaining_qty'] for g in grouped_mos.values())

        _logger.info(
            f"Summary - Total Qty: {self.tot_qty}, Produce Qty: {self.tot_produce_qty}, Remaining Qty: {self.tot_remaining_qty}"
        )

        return self.env['mrp.production'].browse([g['first_mo'].id for g in grouped_mos.values()])

    def create_mfgpending_report(self):
        """Generate Py3O Report"""
        self.getMfgPending()
        return self.env.ref('orion_mfg_pending.py3o_mfgpending').report_action(self)

    def create_mfgpending_treeview(self):
        """Show Tree View of Pending MOs"""
        mo_ids = self.getMfgPending()
        _logger.info(f"Found {len(mo_ids)} manufacturing orders")
        return {
            'type': 'ir.actions.act_window',
            'name': 'Manufacture Pending Report',
            'res_model': 'mrp.production',
            'domain': [('id', 'in', mo_ids.ids)],
            'view_mode': 'tree',
            'views': [(self.env.ref('orion_mfg_pending.view_mfg_pending_tree').id, 'tree')],
            'target': 'self',
        }

    @api.model
    def default_get(self, fields_list):
        """Ensure default date is today"""
        res = super(MfgPending, self).default_get(fields_list)
        res['from_date'] = fields.Date.today()
        res['to_date'] = fields.Date.today()
        return res

    def get_mo_summary_data(self):
        """Helper method to get summary data for the report"""
        return {
            'total_orders': len(self.mo_line_ids),
            'total_quantity': self.tot_qty,
            'total_produce_quantity': self.tot_produce_qty,
            'total_remaining_quantity': self.tot_remaining_qty,
            'report_date': fields.Date.today(),
            'date_filter': f"{self.from_date} to {self.to_date}" if self.date_filter_type == 'range' else f"Schedule: {self.from_date} to {self.schedule_date}",
            'order_type': dict(self._fields['order_type'].selection).get(self.order_type),
            'group_by': dict(self._fields['group_by'].selection).get(self.group_by),
        }

    def get_product_grouped_data(self):
        data = {}

        for mo in self.env['mrp.production'].browse(self.mo_line_ids.ids):
            product = mo.product_id

            if product not in data:
                data[product] = {
                    'product_name': product.name,
                    'lines': [],
                    'total_qty': 0,
                    'total_produce_qty': 0,
                    'total_remaining_qty': 0,
                }

            data[product]['lines'].append(mo)
            data[product]['total_qty'] += mo.product_qty
            data[product]['total_produce_qty'] += mo.sh_produce_qty
            data[product]['total_remaining_qty'] += mo.sh_remaining_qty

        return list(data.values())

    def get_product_grouped_lines(self):
        result = []
        sr_no = 1

        for product in self.get_product_grouped_data():
            for line in product['lines']:

                # Fetch Sale Order for accurate customer + OA
                sale_order = False
                if line.origin:
                    sale_order = self.env['sale.order'].search(
                        [('name', '=', line.origin)], limit=1
                    )

                result.append({
                    'sr_no': sr_no,
                    'customer_name': sale_order.partner_id.name if sale_order else '',
                    'product_name': line.product_id.name or '',
                    'product_spec': line.product_id.product_tmpl_id.specification or '',
                    'order_qty': line.product_qty or 0.0,
                    'pending_qty': line.sh_remaining_qty or 0.0,
                    'date': line.date_planned_start or '',
                    'mo_number': line.name or '',
                    'oa_no': sale_order.name if sale_order else (line.origin or ''),
                })

                sr_no += 1

        return result



    def get_product_grouped_report(self):
        result = []

        for product in self.get_product_grouped_data():

            # Get product record (important)
            product_record = self.env['product.product'].search(
                [('name', '=', product['product_name'])],
                limit=1
            )

            total_qty = sum(line.o_product_qty or 0.0 for line in product['lines'])
            remaining_qty = sum(line.sh_produce_qty or 0.0 for line in product['lines'])

            product_block = {
                'product_name': product['product_name'],
                'default_code': product_record.default_code or '',

                'total_qty': total_qty,

                # ✅ Now using direct sum of sh_produce_qty
                'total_pending_qty': remaining_qty,

                # ✅ Produced Qty = Total - Remaining
                'produced_qty': total_qty - remaining_qty,

                'lines': []
            }

            sr_no = 1

            for line in product['lines']:
                product_block['lines'].append({
                    'sr_no': sr_no,
                    'customer_name': line.customer_id.name or '',
                    'product_spec': line.product_speci or '',
                    # 'order_qty': line.product_qty or 0.0,
                    'order_qty': line.o_product_qty or 0.0,
                    'pending_qty': line.sh_remaining_qty or 0.0,
                    'date': line.order_sch_date or line.date_planned_start or '',
                    'mo_number': line.name or '',
                    'oa_no': line.order_id.name or '',
                })
                sr_no += 1

            result.append(product_block)

        return result



class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        compute='_compute_partner_id',
        store=True
    )

    # Your additional fields (make sure these are defined in your other model file too)
    sh_produce_qty = fields.Float('Produce Quantity')
    sh_remaining_qty = fields.Integer(string='Remaining Produce Quantity')
    sh_total_qty = fields.Integer(string='Total Quantity')

    @api.depends('origin')
    def _compute_partner_id(self):
        for production in self:
            partner = False
            if production.origin:
                sale_order = self.env['sale.order'].search([('name', '=', production.origin)], limit=1)
                if sale_order:
                    partner = sale_order.partner_id
            production.partner_id = partner

    def get_production_summary(self):
        """Helper method to get production summary for individual MO"""
        return {
            'name': self.name,
            'product_name': self.product_id.name,
            'customer_name': self.partner_id.name if self.partner_id else '',
            'product_qty': self.product_qty,
            'sh_produce_qty': self.sh_produce_qty,
            'sh_remaining_qty': self.sh_remaining_qty,
            'sh_total_qty': self.sh_total_qty,
            'state': self.state,
            'date_planned_start': self.date_planned_start,
            'origin': self.origin,
        }




class ProductTemplate(models.Model):
    _inherit = 'product.template'

    specification = fields.Text("Specification")
