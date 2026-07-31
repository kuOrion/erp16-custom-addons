from odoo import models
import json

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def get_project_names(self):
        """
        Returns comma-separated project (analytic account) names
        """
        self.ensure_one()
        names = []
        if self.analytic_distribution:
            for analytic_id in self.analytic_distribution.keys():
                analytic = self.env['account.analytic.account'].browse(int(analytic_id))
                if analytic.exists():
                    names.append(analytic.name)
        return ', '.join(names)
