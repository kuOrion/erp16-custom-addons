# from odoo import models, fields, api
#
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     cgst = fields.Float(string="CGST")
#     sgst = fields.Float(string="SGST")
#     igst = fields.Float(string="IGST")
#
#     # Your custom fields
#     product_specifications = fields.Text(string='Product Specifications')
#     tag_material_code = fields.Char(string='Tag/Material Code')
#     schedule_number = fields.Char(string='Schedule Number')
#     has_schedule = fields.Boolean(string='Has Schedule')
#     schedule_quantity = fields.Float(string='Schedule Quantity')
#     schedule_date = fields.Date(string='Schedule Date')
#     has_deviation = fields.Boolean(string='Has Deviation')
#     your_spec_deviation = fields.Text(string='Your Spec Deviation')
#     our_spec_deviation = fields.Text(string='Our Spec Deviation')
#     remark_deviation = fields.Text(string='Remark Deviation')
#     has_accessories = fields.Boolean(string='Has Accessories')
#     accessory = fields.Char(string='Accessory')
#     accessory_quantity = fields.Float(string='Accessory Quantity')
#     accessory_rate = fields.Float(string='Accessory Rate')
#
#     # internal reference adding in additional details
#     internal_reference = fields.Char(string='Internal Reference',compute='_compute_internal_reference')
#
#     @api.depends('product_id', 'product_id.attribute_line_ids')
#     def _compute_internal_reference(self):
#         for line in self:
#             if line.product_id:
#                 # Get all product attributes and their values
#                 attribute_values = []
#                 for attr_line in line.product_id.attribute_line_ids:
#                     # Get the selected value for this attribute
#                     selected_value = line.product_template_attribute_value_ids.filtered(
#                         lambda v: v.attribute_id == attr_line.attribute_id
#                     )
#                     if selected_value:
#                         attribute_values.append(f"{selected_value.name}")
#
#                 # Combine product reference and attributes
#                 reference_parts = [line.product_id.default_code or '']  # Start with product's internal reference
#                 reference_parts.extend(attribute_values)
#
#                 # Create the internal reference string
#                 line.internal_reference = ' | '.join(filter(None, reference_parts))
#             else:
#                 line.internal_reference = False
#
#     def action_open_line_details(self):
#         return {
#             'name': 'Order Line Details',
#             'type': 'ir.actions.act_window',
#             'res_model': 'sale.order.line',
#             'view_mode': 'form',
#             'res_id': self.id,  # This ensures we edit the current record
#             'view_id': self.env.ref('orion_sales_schedule.view_order_line_form_custom').id,
#             'target': 'new',
#             'context': {'form_view_ref': 'orion_sales_schedule.view_order_line_form_custom'},
#         }
#



# from odoo import models, fields, api
#
#
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     cgst = fields.Float(string="CGST")
#     sgst = fields.Float(string="SGST")
#     igst = fields.Float(string="IGST")
#
#     # Your custom fields
#     product_specifications = fields.Text(string='Product Specifications')
#     tag_material_code = fields.Char(string='Tag/Material Code')
#     schedule_number = fields.Char(string='Schedule Number')
#     has_schedule = fields.Boolean(string='Has Schedule')
#     has_deviation = fields.Boolean(string='Has Deviation')
#     your_spec_deviation = fields.Text(string='Your Spec Deviation')
#     our_spec_deviation = fields.Text(string='Our Spec Deviation')
#     remark_deviation = fields.Text(string='Remark Deviation')
#     has_accessories = fields.Boolean(string='Has Accessories')
#     accessory = fields.Char(string='Accessory')
#     accessory_quantity = fields.Float(string='Accessory Quantity')
#     accessory_rate = fields.Float(string='Accessory Rate')
#
#     # internal reference adding in additional details
#     internal_reference = fields.Char(string='Internal Reference', compute='_compute_internal_reference')
#
#     # 🔹 One2many for multiple schedule lines
#     schedule_ids = fields.One2many(
#         'sale.order.line.schedule',
#         'order_line_id',
#         string='Schedules'
#     )
#
#     @api.depends('product_id', 'product_id.attribute_line_ids')
#     def _compute_internal_reference(self):
#         for line in self:
#             if line.product_id:
#                 attribute_values = []
#                 for attr_line in line.product_id.attribute_line_ids:
#                     selected_value = line.product_template_attribute_value_ids.filtered(
#                         lambda v: v.attribute_id == attr_line.attribute_id
#                     )
#                     if selected_value:
#                         attribute_values.append(f"{selected_value.name}")
#
#                 reference_parts = [line.product_id.default_code or '']
#                 reference_parts.extend(attribute_values)
#
#                 line.internal_reference = ' | '.join(filter(None, reference_parts))
#             else:
#                 line.internal_reference = False
#
#     def action_open_line_details(self):
#         return {
#             'name': 'Order Line Details',
#             'type': 'ir.actions.act_window',
#             'res_model': 'sale.order.line',
#             'view_mode': 'form',
#             'res_id': self.id,
#             'view_id': self.env.ref('orion_sales_schedule.view_order_line_form_custom').id,
#             'target': 'new',
#             'context': {'form_view_ref': 'orion_sales_schedule.view_order_line_form_custom'},
#         }
#
#
# class SaleOrderLineSchedule(models.Model):
#     _name = 'sale.order.line.schedule'
#     _description = 'Sale Order Line Schedule'
#
#     order_line_id = fields.Many2one('sale.order.line', string="Order Line", ondelete='cascade')
#     schedule_quantity = fields.Float(string='Schedule Quantity')
#     schedule_date = fields.Date(string='Schedule Date')



from odoo import models, fields, api, exceptions, _
from datetime import date


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Taxes
    cgst = fields.Float(string="CGST")
    sgst = fields.Float(string="SGST")
    igst = fields.Float(string="IGST")

    # Custom product info
    product_specifications = fields.Text(string='Product Specifications')
    tag_material_code = fields.Char(string='Tag/Material Code')
    schedule_number = fields.Char(string='Schedule Number')
    has_schedule = fields.Boolean(string='Has Schedule')
    remark_deviation = fields.Text(string='Remark Deviation')

    # Internal Reference
    internal_reference = fields.Char(string='Internal Reference', compute='_compute_internal_reference')

    # Schedule lines
    schedule_ids = fields.One2many(
        'sale.order.line.schedule',
        'order_line_id',
        string='Schedules'
    )

    # Deviation fields
    devyn = fields.Boolean('Deviation Yes/No')
    deviation_line = fields.One2many(
        'sale.order.linedev',
        'sale_line_id',
        string='Deviation Lines',
        copy=True
    )

    # Accessory fields
    accessory_yn = fields.Boolean('Accessories Yes/No')
    accessories_line = fields.One2many(
        'sale.order.lineacc',
        'sale_line_id',
        string='Accessories Lines',
        copy=True
    )

    @api.depends('product_id', 'product_id.attribute_line_ids')
    def _compute_internal_reference(self):
        for line in self:
            if line.product_id:
                attribute_values = []
                for attr_line in line.product_id.attribute_line_ids:
                    selected_value = line.product_template_attribute_value_ids.filtered(
                        lambda v: v.attribute_id == attr_line.attribute_id
                    )
                    if selected_value:
                        attribute_values.append(f"{selected_value.name}")

                reference_parts = [line.product_id.default_code or '']
                reference_parts.extend(attribute_values)
                line.internal_reference = ' | '.join(filter(None, reference_parts))
            else:
                line.internal_reference = False

    def action_open_line_details(self):
        return {
            'name': 'Order Line Details',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.line',
            'view_mode': 'form',
            'res_id': self.id,
            'view_id': self.env.ref('orion_sales_schedule.view_order_line_form_custom').id,
            'target': 'new',
            'context': {'form_view_ref': 'orion_sales_schedule.view_order_line_form_custom'},
        }


class SaleOrderLineSchedule(models.Model):
    _name = 'sale.order.line.schedule'
    _description = 'Sale Order Line Schedule'

    order_line_id = fields.Many2one('sale.order.line', string="Order Line", ondelete='cascade')
    schedule_quantity = fields.Float(string='Schedule Quantity')
    schedule_date = fields.Date(string='Schedule Date')


class SaleOrderLineDeviation(models.Model):
    _name = 'sale.order.linedev'
    _description = 'Sale Order Line Deviation'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Order Line Reference',
        required=True,
        ondelete='cascade',
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    devyrspec = fields.Text('Your Specs Deviation', help="Your Specs - Deviation")
    devourspec = fields.Text('Our Specs Deviation', help="Our Specs - Deviation")
    devremark = fields.Char('Remarks - Deviation', help="Remarks - Deviation", size=256)


class SaleOrderLineAccessory(models.Model):
    _name = 'sale.order.lineacc'
    _description = 'Sale Order Line Accessory'

    sale_line_id = fields.Many2one(
        'sale.order.line',
        string='Order Line Reference',
        required=True,
        ondelete='cascade',
        index=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )
    accessory_id = fields.Many2one('product.product', string='Accessory')
    accessory_rate = fields.Float('Accessory Rate', help="Accessory Rate")
    accessory_qty = fields.Integer('Accessory Quantity', help="Gives the Accessory Quantity")


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def is_deviation(self):
        for line in self.order_line:
            if line.devyn:
                return True

        partner_o = self.env['res.partner'].browse(self.partner_id.id)
        if not partner_o.property_account_position_id:
            raise exceptions.except_orm(
                _('Orion Instruments'),
                _('Kindly configure Fiscal Position of your Customer')
            )
        return False

    def is_accessory(self):
        for line in self.order_line:
            if line.accessory_yn:
                return True
        return False
