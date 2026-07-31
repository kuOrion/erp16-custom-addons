# from odoo import models, fields, api
#
#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     @api.onchange('partner_id', 'fiscal_position_id')
#     def _onchange_partner_id_tax_setup(self):
#         """
#         Automatically set taxes based on fiscal position:
#         - Intrastate: CGST 9% + SGST 9%
#         - Interstate: IGST 18%
#         - Export: No taxes
#         """
#         for order in self:
#             if not order.partner_id:
#                 continue
#
#             # Get the appropriate taxes
#             taxes_to_apply = self._get_auto_taxes(order.fiscal_position_id)
#
#             # Apply taxes to all order lines
#             for line in order.order_line:
#                 line.tax_id = taxes_to_apply
#
#     def _get_auto_taxes(self, fiscal_position):
#         """
#         Return taxes based on fiscal position
#         """
#         Tax = self.env['account.tax']
#
#         if not fiscal_position:
#             # If no fiscal position is set, return empty (will use product defaults)
#             return Tax
#
#         fiscal_position_name = (fiscal_position.name or '').lower()
#
#         if 'export' in fiscal_position_name:
#             # Export - no taxes
#             return Tax
#
#         if 'inter' in fiscal_position_name or 'interstate' in fiscal_position_name:
#             # Interstate - IGST 18%
#             igst_tax = Tax.search([
#                 ('name', 'ilike', 'IGST'),
#                 ('amount', '=', 18),
#                 ('type_tax_use', '=', 'sale'),
#                 ('company_id', '=', self.company_id.id)
#             ], limit=1)
#             return igst_tax if igst_tax else Tax
#         else:
#             # Default case (intrastate) - CGST 9% + SGST 9%
#             cgst_tax = Tax.search([
#                 ('name', 'ilike', 'CGST'),
#                 ('amount', '=', 9),
#                 ('type_tax_use', '=', 'sale'),
#                 ('company_id', '=', self.company_id.id)
#             ], limit=1)
#             sgst_tax = Tax.search([
#                 ('name', 'ilike', 'SGST'),
#                 ('amount', '=', 9),
#                 ('type_tax_use', '=', 'sale'),
#                 ('company_id', '=', self.company_id.id)
#             ], limit=1)
#             return cgst_tax + sgst_tax if cgst_tax and sgst_tax else Tax
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         orders = super().create(vals_list)
#         for order in orders:
#             if order.partner_id:
#                 taxes_to_apply = order._get_auto_taxes(order.fiscal_position_id)
#                 order.order_line.write({'tax_id': [(6, 0, taxes_to_apply.ids)]})
#         return orders

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id', 'fiscal_position_id')
    def _onchange_partner_id_tax_setup(self):
        """
        Automatically set taxes based on fiscal position:
        - Intrastate: CGST 9% + SGST 9%
        - Interstate: IGST 18%
        - Export: No taxes
        """
        for order in self:
            if not order.partner_id:
                continue

            # Get the appropriate taxes
            taxes_to_apply = self._get_auto_taxes(order.fiscal_position_id)

            # Apply taxes to all order lines
            for line in order.order_line:
                line.tax_id = taxes_to_apply

    @api.onchange('order_line')
    def _onchange_order_line_auto_tax(self):
        """
        Auto-apply taxes when new order lines are added
        """
        if self.partner_id and self.fiscal_position_id:
            taxes_to_apply = self._get_auto_taxes(self.fiscal_position_id)
            for line in self.order_line:
                if not line.tax_id:  # Only apply if no taxes are set
                    line.tax_id = taxes_to_apply

    def _get_auto_taxes(self, fiscal_position):
        """
        Return taxes based on fiscal position
        """
        Tax = self.env['account.tax']

        if not fiscal_position:
            # If no fiscal position is set, return empty (will use product defaults)
            return Tax

        fiscal_position_name = (fiscal_position.name or '').lower()

        if 'export' in fiscal_position_name:
            # Export - no taxes
            return Tax

        if 'inter' in fiscal_position_name or 'interstate' in fiscal_position_name:
            # Interstate - IGST 18%
            igst_tax = Tax.search([
                ('name', 'ilike', 'IGST'),
                ('amount', '=', 18),
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            return igst_tax if igst_tax else Tax
        else:
            # Default case (intrastate) - CGST 9% + SGST 9%
            cgst_tax = Tax.search([
                ('name', 'ilike', 'CGST'),
                ('amount', '=', 9),
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            sgst_tax = Tax.search([
                ('name', 'ilike', 'SGST'),
                ('amount', '=', 9),
                ('type_tax_use', '=', 'sale'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)
            return cgst_tax + sgst_tax if cgst_tax and sgst_tax else Tax

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        for order in orders:
            if order.partner_id and order.fiscal_position_id:
                taxes_to_apply = order._get_auto_taxes(order.fiscal_position_id)
                for line in order.order_line:
                    if not line.tax_id:  # Only apply if no taxes are set
                        line.write({'tax_id': [(6, 0, taxes_to_apply.ids)]})
        return orders

    def write(self, vals):
        """
        Auto-apply taxes when order is updated
        """
        result = super().write(vals)

        # If partner_id or fiscal_position_id is updated, reapply taxes
        if 'partner_id' in vals or 'fiscal_position_id' in vals:
            for order in self:
                if order.partner_id and order.fiscal_position_id:
                    taxes_to_apply = order._get_auto_taxes(order.fiscal_position_id)
                    for line in order.order_line:
                        if not line.tax_id:  # Only apply if no taxes are set
                            line.write({'tax_id': [(6, 0, taxes_to_apply.ids)]})

        return result

    @api.constrains('order_line', 'fiscal_position_id', 'partner_id')
    def _check_tax_validation(self):
        """
        Validate that proper taxes are applied based on fiscal position
        This acts as a fallback validation if automatic tax application fails
        """
        for order in self:
            if not order.partner_id or not order.fiscal_position_id:
                continue

            fiscal_position_name = (order.fiscal_position_id.name or '').lower()

            # Skip validation for export orders
            if 'export' in fiscal_position_name:
                continue

            # Check each order line for proper tax application
            for line in order.order_line:
                # Skip validation for lines without products or with zero quantity
                if not line.product_id or line.product_uom_qty == 0:
                    continue

                if not line.tax_id:
                    if 'inter' in fiscal_position_name or 'interstate' in fiscal_position_name:
                        raise ValidationError(
                            f"Tax Missing: Interstate transaction requires IGST 18% tax on order line '{line.product_id.name}'. "
                            f"Taxes should have been applied automatically, please check your tax configuration."
                        )
                    else:
                        raise ValidationError(
                            f"Tax Missing: Intrastate transaction requires CGST 9% and SGST 9% taxes on order line '{line.product_id.name}'. "
                            f"Taxes should have been applied automatically, please check your tax configuration."
                        )

                # Validate Interstate (IGST 18%)
                if 'inter' in fiscal_position_name or 'interstate' in fiscal_position_name:
                    igst_found = any(
                        'igst' in tax.name.lower() and tax.amount == 18
                        for tax in line.tax_id
                    )

                    if not igst_found:
                        current_taxes = ', '.join(
                            [f"{tax.name} ({tax.amount}%)" for tax in line.tax_id]) if line.tax_id else 'None'
                        raise ValidationError(
                            f"Invalid Tax Configuration: Interstate transaction for customer '{order.partner_id.name}' "
                            f"requires IGST 18% on order line '{line.product_id.name}'. "
                            f"Current taxes applied: {current_taxes}. "
                            f"Please verify your tax master data configuration."
                        )

                # Validate Intrastate (CGST 9% + SGST 9%)
                else:
                    cgst_found = any(
                        'cgst' in tax.name.lower() and tax.amount == 9
                        for tax in line.tax_id
                    )
                    sgst_found = any(
                        'sgst' in tax.name.lower() and tax.amount == 9
                        for tax in line.tax_id
                    )

                    if not cgst_found or not sgst_found:
                        missing_taxes = []
                        if not cgst_found:
                            missing_taxes.append("CGST 9%")
                        if not sgst_found:
                            missing_taxes.append("SGST 9%")

                        current_taxes = ', '.join(
                            [f"{tax.name} ({tax.amount}%)" for tax in line.tax_id]) if line.tax_id else 'None'
                        raise ValidationError(
                            f"Invalid Tax Configuration: Intrastate transaction for customer '{order.partner_id.name}' "
                            f"requires both CGST 9% and SGST 9% on order line '{line.product_id.name}'. "
                            f"Missing taxes: {', '.join(missing_taxes)}. "
                            f"Current taxes applied: {current_taxes}. "
                            f"Please verify your tax master data configuration."
                        )

    def action_confirm(self):
        """
        Override action_confirm to validate taxes before confirming the order
        """
        # Run tax validation before confirming
        self._check_tax_validation()
        return super().action_confirm()