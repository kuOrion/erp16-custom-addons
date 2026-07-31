from odoo import models, fields, api, _


class MrpBom(models.Model):
    _inherit = "mrp.bom"

    @api.onchange("product_tmpl_id")
    def _onchange_product_tmpl_id_check_existing_bom(self):
        if not self.product_tmpl_id:
            return

        domain = [
            ("product_tmpl_id", "=", self.product_tmpl_id.id),
        ]

        # If we are editing an existing BOM, exclude it
        if self._origin and self._origin.id:
            domain.append(("id", "!=", self._origin.id))

        existing_bom = self.env["mrp.bom"].search(domain, limit=1)

        if existing_bom:
            return {
                "warning": {
                    "title": _("BOM Already Exists"),
                    "message": _(
                        "A Bill of Materials already exists for this product.\n"
                        "You can still create another one if needed."
                    ),
                }
            }
