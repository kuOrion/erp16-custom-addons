from odoo import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    purchase_order_id = fields.Many2one(
        comodel_name='purchase.order',
        string='Purchase Order',
        domain="[('state', 'in', ['purchase', 'done'])]",
        help="Select the Purchase Order to reference its details."
    )
    supplier_challan_number = fields.Char(
        string='Supplier Challan Number',
        help="Reference number provided by the supplier on their challan."
    )

    supplier_challan_date = fields.Date(
        string='Supplier Challan Date',
        help="Date on the supplier's challan."
    )
    #
    # @api.onchange('purchase_order_id')
    # def _onchange_purchase_order_id(self):
    #     if self.purchase_order_id:
    #         # Clear existing move lines
    #         self.move_ids_without_package = [(5, 0, 0)]
    #
    #         # Copy details from the selected Purchase Order
    #         for line in self.purchase_order_id.order_line:
    #             self.move_ids_without_package += self.move_ids_without_package.new({
    #                 'product_id': line.product_id.id,
    #                 'name': line.name,
    #                 'product_uom_qty': line.product_uom_qty,
    #                 'product_uom': line.product_uom.id,
    #                 'location_id': self.picking_type_id.default_location_src_id.id,
    #                 'location_dest_id': self.picking_type_id.default_location_dest_id.id,
    #             })
