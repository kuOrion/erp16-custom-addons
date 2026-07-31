# from odoo import api, fields, models, api
# import odoo.addons.decimal_precision as dp
#
# import logging
#
# _logger = logging.getLogger(__name__)
#
#
# class orion_orderline(models.Model):
#     _inherit = 'sale.order.line'
#
#     product_spec = fields.Text('Product Specifications')
#     tagno = fields.Text('Tag No/Material Code')
#
#     scheduleyn = fields.Boolean('Schedule Yes/No')
#     schedule_line = fields.One2many('sale.order.lineschedule', 'sale_line_id', string='Schedule Lines', readonly=True,
#                                     states={'draft': [('readonly', False)]}, copy=True)
#
#     schno = fields.Text('Schedule Number')
#
#     devyn = fields.Boolean('Deviation Yes/No')
#     deviation_line = fields.One2many('sale.order.linedev', 'sale_line_id', string='Deviation Lines', readonly=True,
#                                      states={'draft': [('readonly', False)]}, copy=True)
#
#     accessory_yn = fields.Boolean('Accessories Yes/No')
#     acessories_line = fields.One2many('sale.order.lineacc', 'sale_line_id', string='Acessories Lines', readonly=True,
#                                       states={'draft': [('readonly', False)]}, copy=True)
#
#     _defaults = {
#         'scheduleyn': False,
#         'devyn': False,
#         'accessory_yn': False,
#     }
#
#     cgst = fields.Float("cgst", compute='_compute_taxes', store=True, default=0.0)
#     igst = fields.Float("igst", compute='_compute_taxes', store=True, default=0.0)
#     sgst = fields.Float("sgst", compute='_compute_taxes', store=True, default=0.0)
#
#     @api.one
#     @api.depends('tax_id')
#     def _compute_taxes(self):
#         for i in self.tax_id:
#             _logger.info("name = %s, amt = %s", i.name, i.amount)
#         cgst = 0.0
#         sgst = 0.0
#         igst = 0.0
#         for i in self.tax_id:
#             if "CGST" in i.name:
#                 cgst = i.amount
#             elif "IGST" in i.name:
#                 igst = i.amount
#             elif "SGST" in i.name:
#                 sgst = i.amount
#
#         self.update({
#             'cgst': cgst, 'igst': igst, 'sgst': sgst
#         })
#         _logger.info("cgst = %s, sgst = %s, igst = %s", self.cgst, self.sgst, self.igst)
#
#
# class sale_order_lineschedule(models.Model):
#     _name = 'sale.order.lineschedule'
#     _description = 'sale order line Schedule'
#     sale_line_id = fields.Many2one('sale.order.line', 'Order Line Reference', required=True, ondelete='cascade',
#                                    index=True, readonly=True, states={'draft': [('readonly', False)]})
#     schdate = fields.Date('Schedule Date', help="Gives the Schedule Date when displaying a list of sales order lines.")
#     schqty = fields.Integer('Schedule Quantity',
#                             help="Gives the Schedule Quantity when displaying a list of sales order lines.")
#
#
# class sale_order_linedev(models.Model):
#     _name = 'sale.order.linedev'
#     _description = 'sale order line deviation'
#     sale_line_id = fields.Many2one('sale.order.line', 'Order Line Reference', required=True, ondelete='cascade',
#                                    index=True, readonly=True, states={'draft': [('readonly', False)]})
#     devyrspec = fields.Text('Your Specs Deviation', help="Your Specs - Deviation")
#     devourspec = fields.Text('Our Specs Deviation', help="Our Specs - Deviation")
#     devremark = fields.Char('Remarks - Deviation', help="Remarks - Deviation", size=256)
#
#
# class sale_order_lineacc(models.Model):
#     _name = 'sale.order.lineacc'
#     _description = 'sale order line Accessory'
#     sale_line_id = fields.Many2one('sale.order.line', 'Order Line Reference', required=True, ondelete='cascade',
#                                    index=True, readonly=True, states={'draft': [('readonly', False)]})
#     accessory_id = fields.Many2one('product.product', 'Accessory')
#     accessory_rate = fields.Float('Accessory Rate', help="Accessory Rate")
#     accessory_qty = fields.Integer('Accessory Quantity', help="Gives the Accessory Quantity")
#
# # vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class OrionOrderLine(models.Model):
    _inherit = 'sale.order.line'

    product_spec = fields.Text('Product Specifications')
    tagno = fields.Text('Tag No/Material Code')

    scheduleyn = fields.Boolean('Schedule Yes/No', default=False)
    schedule_line = fields.One2many(
        'sale.order.lineschedule', 'sale_line_id',
        string='Schedule Lines', readonly=True,
        states={'draft': [('readonly', False)]}, copy=True
    )

    schno = fields.Text('Schedule Number')

    devyn = fields.Boolean('Deviation Yes/No', default=False)
    deviation_line = fields.One2many(
        'sale.order.linedev', 'sale_line_id',
        string='Deviation Lines', readonly=True,
        states={'draft': [('readonly', False)]}, copy=True
    )

    accessory_yn = fields.Boolean('Accessories Yes/No', default=False)
    accessories_line = fields.One2many(
        'sale.order.lineacc', 'sale_line_id',
        string='Accessories Lines', readonly=True,
        states={'draft': [('readonly', False)]}, copy=True
    )

    cgst = fields.Float("CGST", compute='_compute_taxes', store=True, default=0.0)
    igst = fields.Float("IGST", compute='_compute_taxes', store=True, default=0.0)
    sgst = fields.Float("SGST", compute='_compute_taxes', store=True, default=0.0)

    @api.depends('tax_id')
    def _compute_taxes(self):
        for line in self:
            cgst = 0.0
            sgst = 0.0
            igst = 0.0
            for tax in line.tax_id:
                if "CGST" in tax.name:
                    cgst = tax.amount
                elif "IGST" in tax.name:
                    igst = tax.amount
                elif "SGST" in tax.name:
                    sgst = tax.amount

            line.update({
                'cgst': cgst,
                'igst': igst,
                'sgst': sgst,
            })
            _logger.info("CGST = %s, SGST = %s, IGST = %s", line.cgst, line.sgst, line.igst)


class SaleOrderLineSchedule(models.Model):
    _name = 'sale.order.lineschedule'
    _description = 'Sale Order Line Schedule'

    sale_line_id = fields.Many2one(
        'sale.order.line', 'Order Line Reference',
        required=True, ondelete='cascade',
        index=True, readonly=True,
        states={'draft': [('readonly', False)]}
    )
    schdate = fields.Date(
        'Schedule Date',
        help="Gives the schedule date when displaying a list of sales order lines."
    )
    schqty = fields.Integer(
        'Schedule Quantity',
        help="Gives the schedule quantity when displaying a list of sales order lines."
    )


class SaleOrderLineDeviation(models.Model):
    _name = 'sale.order.linedev'
    _description = 'Sale Order Line Deviation'

    sale_line_id = fields.Many2one(
        'sale.order.line', 'Order Line Reference',
        required=True, ondelete='cascade',
        index=True, readonly=True,
        states={'draft': [('readonly', False)]}
    )
    devyrspec = fields.Text('Your Specs Deviation', help="Your specs deviation.")
    devourspec = fields.Text('Our Specs Deviation', help="Our specs deviation.")
    devremark = fields.Char(
        'Remarks - Deviation', help="Remarks for deviation.", size=256
    )


class SaleOrderLineAccessory(models.Model):
    _name = 'sale.order.lineacc'
    _description = 'Sale Order Line Accessory'

    sale_line_id = fields.Many2one(
        'sale.order.line', 'Order Line Reference',
        required=True, ondelete='cascade',
        index=True, readonly=True,
        states={'draft': [('readonly', False)]}
    )
    accessory_id = fields.Many2one('product.product', 'Accessory')
    accessory_rate = fields.Float('Accessory Rate', help="Rate of the accessory.")
    accessory_qty = fields.Integer(
        'Accessory Quantity',
        help="Gives the quantity of the accessory."
    )
