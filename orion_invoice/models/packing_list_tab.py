from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = "account.move"

    x_total_boxes = fields.Integer(string="Total Number of Boxes")
    box_ids = fields.One2many('account.move.box', 'move_id', string="Boxes")
    total_gross_weight = fields.Float(string="Total Gross Weight (Kg)", compute="_compute_total_gross_weight", store=True)
    x_net_weight = fields.Float(string="Net Weight (kg)")



    @api.depends('box_ids.gross_weight')
    def _compute_total_gross_weight(self):
        for move in self:
            move.total_gross_weight = sum(move.box_ids.mapped('gross_weight'))

    @api.onchange('x_total_boxes')
    def _onchange_total_boxes(self):
        for move in self:
            # Reset box lines
            move.box_ids = [(5, 0, 0)]
            for i in range(move.x_total_boxes):
                move.box_ids = [(0, 0, {'box_number': i + 1})]



from odoo import models, fields

class AccountMoveBox(models.Model):
    _name = "account.move.box"
    _description = "Box Details"

    move_id = fields.Many2one('account.move', string="Invoice/Delivery")
    box_number = fields.Integer(string="Box Number")
    length = fields.Float(string="Length (cm)")
    width = fields.Float(string="Width (cm)")
    height = fields.Float(string="Height (cm)")
    gross_weight = fields.Float(string="Gross Weight (Kg)")
