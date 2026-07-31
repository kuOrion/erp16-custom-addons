from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    td_manufactured_location_id = fields.Many2one(
        'stock.location', string='Manufactured PDI Location',
        domain=[('usage', '=', 'internal')],
        config_parameter='orion_inventory_product_transfer.td_manufactured_location_id')

    td_fg_location_id = fields.Many2one(
        'stock.location', string='FG Location',
        domain=[('usage', '=', 'internal')],
        config_parameter='orion_inventory_product_transfer.td_fg_location_id')

    td_stock_location_id = fields.Many2one(
        'stock.location', string='Stock Location',
        domain=[('usage', '=', 'internal')],
        config_parameter='orion_inventory_product_transfer.td_stock_location_id')

    @api.model
    def get_default_route_location(self, fields):
        IrConfigParam = self.env['ir.config_parameter']
        td_manufactured_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_manufactured_location_id')
        td_fg_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_fg_location_id')
        td_stock_location_id = IrConfigParam.get_param('orion_inventory_product_transfer.td_stock_location_id')
        return {
            'td_manufactured_location_id': td_manufactured_location_id and int(td_manufactured_location_id) or False,
            'td_fg_location_id': td_manufactured_location_id and int(td_fg_location_id) or False,
            'td_stock_location_id': td_manufactured_location_id and int(td_stock_location_id) or False,
        }

    # @api.multi
    def set_route_location(self):
        self.ensure_one()
        IrConfigParam = self.env['ir.config_parameter']
        IrConfigParam.set_param('orion_inventory_product_transfer.td_manufactured_location_id', self.td_manufactured_location_id.id or '')
        IrConfigParam.set_param('orion_inventory_product_transfer.td_fg_location_id', self.td_fg_location_id.id or '')
        IrConfigParam.set_param('orion_inventory_product_transfer.td_stock_location_id', self.td_stock_location_id.id or '')


