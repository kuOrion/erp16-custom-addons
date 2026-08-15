from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def action_check_availability_preview(self):
        """
        Preview component availability without confirming MO
        """
        for rec in self:
            for line in rec.move_raw_ids:
                product = line.product_id

                # Available qty (free stock)
                available_qty = product.qty_available

                required_qty = line.product_uom_qty

                # Logging (you can replace this with wizard later)
                message = f"{product.display_name} → Required: {required_qty}, Available: {available_qty}"

                rec.message_post(body=message)

        return True