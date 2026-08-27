# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
from odoo import models, fields,api


class StockLot(models.Model):
    _inherit = 'stock.lot'

    sh_finished_product_id = fields.Many2one('sh.finished.product', string='Finished Product')
    sh_config_prifix_type = fields.Char(string='Serial No Prefix 1')
    sh_is_released = fields.Boolean(string='Released for Reuse', default=False, copy=False)
    sh_reassign_log_ids = fields.One2many(
        'sh.serial.reassign.log', 'lot_id', string='Release/Reuse History')


    @api.model
    def sh_get_next_serial(self, company, product,prifix,serial_type):
        """Custom Method for Return the next serial number to be attributed to the product.
        Anchors on the HIGHEST serial number by name (not the newest record by id):
        released serials reused later create new rows with old names, so the
        latest id can point at a low number and cause duplicate-name collisions."""
        if product.tracking != "none":
            candidates = self.env['stock.lot'].search([
                ('company_id', '=', company.id),
                ('name', '=like', '%s%%' % prifix),
            ])
            last_serial = self.env['stock.lot']
            max_number = -1
            for lot in candidates:
                suffix = (lot.name or '')[len(prifix):]
                if suffix.isdigit() and int(suffix) > max_number:
                    max_number = int(suffix)
                    last_serial = lot
            if last_serial:
                return self.env['stock.lot'].generate_lot_names(last_serial.name, 2)[1]
        return False

    @api.model
    def sh_get_released_serials(self, company, prefix, qty):
        """Return up to `qty` previously released Serial Numbers for this prefix,
        lowest number first, so they get reused before generating new ones.
        Filters by NAME starting with `prefix`, not just the sh_config_prifix_type
        tag, so a stale/mistagged lot (name doesn't match its tag) can never be
        offered as a released serial for the wrong prefix."""
        if qty <= 0:
            return self.browse()
        candidates = self.search([
            ('company_id', '=', company.id),
            ('sh_config_prifix_type', '=', prefix),
            ('sh_is_released', '=', True),
            ('name', '=like', '%s%%' % prefix),
        ], order='name ASC')
        return candidates[:int(qty)]
    