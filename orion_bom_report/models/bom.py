# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class ProductWithCost(models.Model):
    _inherit = 'product.product'

    quoted_cost = fields.Monetary(store=True)
    budgeted_cost = fields.Monetary(store=True)
    actual_cost = fields.Monetary(store=True)


class BomReport(models.TransientModel):
    _name = "bom.report"
    _description = "Multiple BOM Report"

    bom1 = fields.Many2one('mrp.bom', string='BOM')

    def get_first(self):
        bom_list = []
        bom_list.append(self.bom1)
        return bom_list

    def get_total_quoted_cost(self):
        total = 0
        bom = self.bom1
        for line in bom.bom_line_ids:
            total = total + line.product_id.quoted_cost
        return total

    def get_total_budgeted_cost(self):
        total = 0
        bom = self.bom1
        for line in bom.bom_line_ids:
            total = total + line.product_id.budgeted_cost
        return total

    def get_total_actual_cost(self):
        total = 0
        bom = self.bom1
        for line in bom.bom_line_ids:
            total = total + line.product_id.actual_cost
        return total

    def create_bom_report(self):
        return self.env.ref('orion_bom_report.bom_report_action').report_action(self)