# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from odoo import fields, models


class ShSerialReassignLog(models.Model):
    _name = 'sh.serial.reassign.log'
    _description = 'Serial Number Release/Reuse History'
    _order = 'create_date desc'

    lot_id = fields.Many2one('stock.lot', string='Serial Number', required=True, ondelete='cascade')
    from_production_id = fields.Many2one('mrp.production', string='Released From MO')
    to_production_id = fields.Many2one('mrp.production', string='Assigned To MO')
    action = fields.Selection([
        ('release', 'Released'),
        ('reuse', 'Auto-Reused'),
    ], string='Action', required=True)
    user_id = fields.Many2one('res.users', string='Done By', default=lambda self: self.env.user)
