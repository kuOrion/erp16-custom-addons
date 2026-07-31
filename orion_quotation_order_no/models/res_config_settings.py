from odoo import models, fields

"""
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    quotation_prefix = fields.Char(
        string="Quotation Prefix",
        config_parameter='orion.quotation_prefix',
        default='KQ',
        help="Prefix for domestic quotation numbers"
    )
    export_quotation_prefix = fields.Char(
        string="Export Quotation Prefix",
        config_parameter='orion.export_quotation_prefix',
        default='KQ/EX',
        help="Prefix for export quotation numbers"
    )
    order_prefix = fields.Char(
        string="Sale Order Prefix",
        config_parameter='orion.order_prefix',
        default='OA',
        help="Shared prefix for all sale orders (e.g., OA)"
    )

"""
class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    quotation_prefix = fields.Char(
        string="Quotation Prefix",
        config_parameter='orion.quotation_prefix',
        default='KQ',
        help="Prefix for domestic quotation numbers"
    )
    export_quotation_prefix = fields.Char(
        string="Export Quotation Prefix",
        config_parameter='orion.export_quotation_prefix',
        default='KQ/EX',
        help="Prefix for export quotation numbers"
    )
    order_prefix = fields.Char(
        string="Sale Order Prefix",
        config_parameter='orion.order_prefix',
        default='OA',
        help="Shared prefix for all sale orders (e.g., OA)"
    )

