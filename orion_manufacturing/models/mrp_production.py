from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    schedule_id = fields.Many2one(
        'order.schedule',
        string="Schedule"
    )


class OrionMRP(models.Model):
    _inherit = 'mrp.production'

    schedule_id = fields.Many2one("sale.order.line.schedule", string="Schedule Line")

    oayn = fields.Boolean('Order Reference')
    order_id = fields.Many2one('sale.order', string="Order Reference", help="Select Sale Order")
    order_sch_date = fields.Datetime(string="Scheduled Date", required=True )
    customer_id = fields.Many2one()
    product_oa_id = fields.Many2one(
        'product.product',
        string="Order Reference Product",
        help="Select product",
        domain="[('sale_ok', '=', True)]"
    )
    o_product_qty = fields.Float(string="Product Quantity", help="Quantity of the selected product")
    product_def_code = fields.Char("Internal Reference")

    # ✅ SOLUTION 1: Use a separate field for customer that won't be overridden
    customer_id = fields.Many2one('res.partner', string="Customer Name", readonly=True)

    # ✅ SOLUTION 2: Computed field as backup (optional)
    customer_name = fields.Char(string="Customer", compute="_compute_customer_name", store=True)

    product_speci = fields.Text("Specification")

    @api.depends('order_id', 'customer_id')
    def _compute_customer_name(self):
        """Compute customer name from order or customer_id"""
        for record in self:
            if record.customer_id:
                record.customer_name = record.customer_id.name
            elif record.order_id:
                record.customer_name = record.order_id.partner_id.name
            else:
                record.customer_name = ""

    # --- Onchange when selecting Sale Order ---
    @api.onchange('order_id')
    def onchange_order_id(self):
        if not self.order_id:
            self.product_id = False
            self.product_oa_id = False
            self.product_speci = ""
            self.order_sch_date = False
            # ✅ Clear customer fields
            self.customer_id = False
            return

        # ✅ Set customer immediately when order is selected
        self.customer_id = self.order_id.partner_id.id

        # 🔑 Get products already in MRP for this order
        used_products = self.search([
            ('order_id', '=', self.order_id.id),
            ('state', 'not in', ['cancel', 'done'])
        ]).mapped('product_id').ids

        # 🔑 Exclude used products from available list
        available_products = self.order_id.order_line.filtered(
            lambda l: l.product_id.id not in used_products
        ).mapped('product_id').ids

        if not available_products:
            self.product_id = False
            self.product_oa_id = False
            self.product_speci = ""
            return {
                'warning': {
                    'title': 'No Available Products',
                    'message': 'All products from this sale order are already in production.'
                }
            }

        # By default, load the first available line
        first_line = self.order_id.order_line.filtered(
            lambda l: l.product_id.id in available_products
        )[0]
        self._load_order_line_details(first_line)

        return {'domain': {'product_oa_id': [('id', 'in', available_products)]}}

    # --- Onchange when selecting Product from that order ---
    @api.onchange('product_oa_id')
    def onchange_product_oa_id(self):
        if not self.product_oa_id or not self.order_id:
            return

        line = self.order_id.order_line.filtered(
            lambda l: l.product_id.id == self.product_oa_id.id
        )[:1]

        if line:
            self._load_order_line_details(line)

    # def _load_order_line_details(self, line):
    #     """Fill MRP fields from sale order line"""
    #     self.product_id = line.product_id.id
    #     self.product_oa_id = line.product_id.id
    #     # ✅ Use customer_id instead of partner_id
    #     self.customer_id = self.order_id.partner_id.id
    #     self.product_def_code = line.product_id.default_code
    #     self.product_uom_id = line.product_uom.id
    #     self.o_product_qty = line.product_uom_qty
    #     self.product_qty = line.product_uom_qty
    #     self.product_speci = getattr(line, "product_specifications", "") or ""
    #
    #     # ✅ Fetch from custom schedules (if any)
    #     if line.schedule_ids:
    #         first_schedule = line.schedule_ids.sorted(lambda s: s.schedule_date)[0]
    #         self.schedule_id = first_schedule.id
    #         self.o_product_qty = first_schedule.schedule_quantity
    #         self.product_qty = first_schedule.schedule_quantity
    #         self.order_sch_date = first_schedule.schedule_date
    #         self.date_planned_start = first_schedule.schedule_date
    #

    def _load_order_line_details(self, line):
        """Fill MRP fields from sale order line"""
        self.product_id = line.product_id.id
        self.product_oa_id = line.product_id.id
        self.customer_id = self.order_id.partner_id.id
        self.product_def_code = line.product_id.default_code
        self.product_uom_id = line.product_uom.id
        self.o_product_qty = line.product_uom_qty
        self.product_qty = line.product_uom_qty

        # ---------------------------------------------------------
        # Combine Product Specification + Tag/Material Code
        # ---------------------------------------------------------
        specification = line.product_specifications or ""
        tag_code = line.tag_material_code or ""

        if specification and tag_code:
            self.product_speci = (
                f"{specification}\n"
                f"Tag/Material Code : {tag_code}"
            )
        elif specification:
            self.product_speci = specification
        elif tag_code:
            self.product_speci = f"Tag/Material Code : {tag_code}"
        else:
            self.product_speci = ""

        # ---------------------------------------------------------

        if line.schedule_ids:
            first_schedule = line.schedule_ids.sorted(
                lambda s: s.schedule_date
            )[0]

            self.schedule_id = first_schedule.id
            self.o_product_qty = first_schedule.schedule_quantity
            self.product_qty = first_schedule.schedule_quantity
            self.order_sch_date = first_schedule.schedule_date
            self.date_planned_start = first_schedule.schedule_date
    # --- Sync qty manually ---
    @api.onchange('o_product_qty')
    def onchange_o_product_qty(self):
        if self.o_product_qty:
            self.product_qty = self.o_product_qty

    @api.onchange('order_sch_date')
    def onchange_order_sch_date(self):
        if self.order_sch_date:
            self.date_planned_start = self.order_sch_date

    # ✅ SOLUTION 3: Override create to ensure customer is preserved
    @api.model
    def create(self, vals):
        # Handle product_id sync
        if vals.get('product_oa_id') and not vals.get('product_id'):
            if isinstance(vals['product_oa_id'], models.BaseModel):
                vals['product_id'] = vals['product_oa_id'].id
            else:
                vals['product_id'] = vals['product_oa_id']

        # ✅ Ensure customer_id is set from order_id if not provided
        if vals.get('order_id') and not vals.get('customer_id'):
            order = self.env['sale.order'].browse(vals['order_id'])
            if order.exists():
                vals['customer_id'] = order.partner_id.id

        return super(OrionMRP, self).create(vals)

    # ✅ SOLUTION 4: Override write to preserve customer
    def write(self, vals):
        # Handle product_id sync
        if vals.get('product_oa_id'):
            if isinstance(vals['product_oa_id'], models.BaseModel):
                vals['product_id'] = vals['product_oa_id'].id
            else:
                vals['product_id'] = vals['product_oa_id']

        # ✅ Preserve customer_id if order changes
        if vals.get('order_id'):
            order = self.env['sale.order'].browse(vals['order_id'])
            if order.exists():
                vals['customer_id'] = order.partner_id.id

        return super(OrionMRP, self).write(vals)

    # ✅ SOLUTION 5: Override standard MRP methods that might clear partner_id
    def _get_partner_to_assign(self):
        """Override to prevent standard logic from clearing our customer"""
        # Return the customer from our custom field instead of standard logic
        if self.customer_id:
            return self.customer_id
        return super(OrionMRP, self)._get_partner_to_assign()

    @api.model
    def _prepare_mo_vals(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values,
                         bom):
        """Override MO preparation to preserve customer"""
        vals = super(OrionMRP, self)._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name, origin, company_id, values, bom
        )

        # ✅ If this MO is created from a sale order, preserve the customer
        if values and values.get('sale_line_id'):
            sale_line = self.env['sale.order.line'].browse(values['sale_line_id'])
            if sale_line.exists():
                vals['customer_id'] = sale_line.order_id.partner_id.id
                vals['order_id'] = sale_line.order_id.id

        return vals


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     def action_confirm(self):
#         res = super().action_confirm()
#         mrp_obj = self.env['mrp.production']
#
#         for order in self:
#             for line in order.order_line:
#                if line.product_id.type == 'product' and line.schedule_id:
#                     vals = {
#                         'product_id': line.product_id.id,
#                         'product_qty': line.product_uom_qty,
#                         'product_uom_id': line.product_uom.id,
#                         'origin': order.name,
#                         'order_id': order.id,  # Sale Order reference
#                         'schedule_id': line.schedule_id.id,  # ensure .id, not record
#                         'date_planned_start': line.schedule_id.schedule_date
#                             if line.schedule_id and line.schedule_id.schedule_date
#                             else fields.Datetime.now(),
#                         'bom_id': line.product_id.bom_id.id if line.product_id.bom_id else False,
#                         'company_id': order.company_id.id,
#                     }
#
#                     # Only keep safe keys (remove Nones for Many2one)
#                     clean_vals = {k: v for k, v in vals.items() if v not in (False, None)}
#
#                     mrp_obj.create(clean_vals)
#
#         return res

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super().action_confirm()
        mrp_obj = self.env['mrp.production']

        for order in self:
            for line in order.order_line:

                if line.product_id.type == 'product' and line.schedule_id:

                    # -------------------------------------------------
                    # Combine Product Specification + Tag/Material Code
                    # -------------------------------------------------
                    specification = line.product_specifications or ""
                    tag_code = line.tag_material_code or ""

                    if specification and tag_code:
                        product_speci = (
                            f"{specification}\n\n"
                            f"Tag/Material Code : {tag_code}"
                        )
                    elif specification:
                        product_speci = specification
                    elif tag_code:
                        product_speci = f"Tag/Material Code : {tag_code}"
                    else:
                        product_speci = ""
                    # -------------------------------------------------

                    vals = {
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom_id': line.product_uom.id,
                        'origin': order.name,
                        'order_id': order.id,
                        'schedule_id': line.schedule_id.id,
                        'product_speci': product_speci,
                        'date_planned_start': (
                            line.schedule_id.schedule_date
                            if line.schedule_id and line.schedule_id.schedule_date
                            else fields.Datetime.now()
                        ),
                        'bom_id': (
                            line.product_id.bom_id.id
                            if line.product_id.bom_id
                            else False
                        ),
                        'company_id': order.company_id.id,
                    }

                    clean_vals = {
                        k: v
                        for k, v in vals.items()
                        if v not in (False, None)
                    }

                    mrp_obj.create(clean_vals)

        return res