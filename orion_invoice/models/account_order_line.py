from odoo import models, fields, api

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    # GST related fields
    cgst = fields.Float(
        string='CGST Amount',
        compute='_compute_gst_amounts',
        store=True,
        digits=(16, 2)
    )
    sgst = fields.Float(
        string='SGST Amount',
        compute='_compute_gst_amounts',
        store=True,
        digits=(16, 2)
    )
    igst = fields.Float(
        string='IGST Amount',
        compute='_compute_gst_amounts',
        store=True,
        digits=(16, 2)
    )
    cgst_rate = fields.Float(
        string='CGST Rate',
        compute='_compute_gst_amounts',
        store=True,
        digits=(16, 2)
    )
    sgst_rate = fields.Float(
        string='SGST Rate',
        compute='_compute_gst_amounts',
        store=True,
        digits=(16, 2)
    )
    igst_rate = fields.Float(
        string='IGST Rate',
        compute='_compute_gst_amounts',
        store=True,
        digits=(16, 2)
    )

    @api.depends('tax_ids', 'price_subtotal', 'move_id.partner_id.state_id')
    def _compute_gst_amounts(self):
        for line in self:
            line.cgst = 0.0
            line.sgst = 0.0
            line.igst = 0.0
            line.cgst_rate = 0.0
            line.sgst_rate = 0.0
            line.igst_rate = 0.0

            # Skip if not from India or no taxes
            if not line.tax_ids or not line.move_id.partner_id.country_id.code == 'IN':
                continue

            # Get company and partner states
            company_state = line.company_id.state_id
            partner_state = line.move_id.partner_id.state_id

            for tax in line.tax_ids:
                # Check if tax is GST by tax name/code
                if 'CGST' in tax.name:
                    line.cgst_rate = tax.amount
                    line.cgst = (line.price_subtotal * tax.amount) / 100
                elif 'SGST' in tax.name:
                    line.sgst_rate = tax.amount
                    line.sgst = (line.price_subtotal * tax.amount) / 100
                elif 'IGST' in tax.name:
                    line.igst_rate = tax.amount
                    line.igst = (line.price_subtotal * tax.amount) / 100
                # You might want to add more conditions based on your tax configuration