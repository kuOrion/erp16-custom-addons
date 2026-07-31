# from odoo import models, fields, api
# from odoo.exceptions import ValidationError
#
#
# class PurchaseOrder(models.Model):
#     _inherit = 'purchase.order'
#
#     @api.onchange('partner_id', 'fiscal_position_id')
#     def _onchange_partner_id_tax_setup(self):
#         """
#         Automatically set taxes based on fiscal position:
#         - Intrastate: Purchase CGST 9% + Purchase SGST 9%
#         - Interstate: Purchase IGST 18%
#         - Export: No taxes
#         """
#         for order in self:
#             if not order.partner_id:
#                 continue
#
#             taxes_to_apply = order._get_auto_taxes(order.fiscal_position_id)
#
#             for line in order.order_line:
#                 line.taxes_id = taxes_to_apply
#
#     @api.onchange('order_line')
#     def _onchange_order_line_auto_tax(self):
#         """
#         Auto-apply taxes when new order lines are added
#         """
#         if self.partner_id and self.fiscal_position_id:
#             taxes_to_apply = self._get_auto_taxes(self.fiscal_position_id)
#             for line in self.order_line:
#                 if not line.taxes_id:  # Only apply if no taxes are set
#                     line.taxes_id = taxes_to_apply
#
#     def _get_auto_taxes(self, fiscal_position):
#         """
#         Return purchase taxes based on fiscal position
#         """
#         Tax = self.env['account.tax']
#
#         if not fiscal_position:
#             return Tax
#
#         fiscal_position_name = (fiscal_position.name or '').lower()
#
#         if 'export' in fiscal_position_name:
#             # Export - no taxes
#             return Tax
#
#         if 'inter' in fiscal_position_name or 'interstate' in fiscal_position_name:
#             # Interstate - IGST 18% (Purchase)
#             igst_tax = Tax.search([
#                 ('name', 'ilike', 'IGST'),
#                 ('amount', '=', 18),
#                 ('type_tax_use', '=', 'purchase'),
#                 ('company_id', '=', self.company_id.id)
#             ], limit=1)
#             return igst_tax if igst_tax else Tax
#         else:
#             # Intrastate - Purchase CGST 9% + SGST 9%
#             cgst_tax = Tax.search([
#                 ('name', 'ilike', 'CGST'),
#                 ('amount', '=', 9),
#                 ('type_tax_use', '=', 'purchase'),
#                 ('company_id', '=', self.company_id.id)
#             ], limit=1)
#             sgst_tax = Tax.search([
#                 ('name', 'ilike', 'SGST'),
#                 ('amount', '=', 9),
#                 ('type_tax_use', '=', 'purchase'),
#                 ('company_id', '=', self.company_id.id)
#             ], limit=1)
#             return cgst_tax + sgst_tax if cgst_tax and sgst_tax else Tax
#
#     @api.model_create_multi
#     def create(self, vals_list):
#         orders = super().create(vals_list)
#         for order in orders:
#             if order.partner_id and order.fiscal_position_id:
#                 taxes_to_apply = order._get_auto_taxes(order.fiscal_position_id)
#                 for line in order.order_line:
#                     if not line.taxes_id:
#                         line.write({'taxes_id': [(6, 0, taxes_to_apply.ids)]})
#         return orders
#
#     def write(self, vals):
#         result = super().write(vals)
#         if 'partner_id' in vals or 'fiscal_position_id' in vals:
#             for order in self:
#                 if order.partner_id and order.fiscal_position_id:
#                     taxes_to_apply = order._get_auto_taxes(order.fiscal_position_id)
#                     for line in order.order_line:
#                         if not line.taxes_id:
#                             line.write({'taxes_id': [(6, 0, taxes_to_apply.ids)]})
#         return result
#
#     @api.constrains('order_line', 'fiscal_position_id', 'partner_id')
#     def _check_tax_validation(self):
#         """
#         Validate that proper purchase taxes are applied
#         """
#         for order in self:
#             if not order.partner_id or not order.fiscal_position_id:
#                 continue
#
#             fiscal_position_name = (order.fiscal_position_id.name or '').lower()
#
#             if 'export' in fiscal_position_name:
#                 continue
#
#             for line in order.order_line:
#                 if not line.product_id or line.product_qty == 0:
#                     continue
#
#                 if not line.taxes_id:
#                     if 'inter' in fiscal_position_name or 'interstate' in fiscal_position_name:
#                         raise ValidationError(
#                             f"Tax Missing: Interstate purchase requires IGST 18% tax on product '{line.product_id.name}'."
#                         )
#                     else:
#                         raise ValidationError(
#                             f"Tax Missing: Intrastate purchase requires CGST 9% and SGST 9% taxes "
#                             f"on product '{line.product_id.name}'."
#                         )
#
#                 if 'inter' in fiscal_position_name or 'interstate' in fiscal_position_name:
#                     igst_found = any(
#                         'igst' in tax.name.lower() and tax.amount == 18
#                         for tax in line.taxes_id
#                     )
#                     if not igst_found:
#                         raise ValidationError(
#                             f"Invalid Tax: Interstate purchase requires IGST 18% on '{line.product_id.name}', "
#                             f"but got {', '.join([t.name for t in line.taxes_id])}."
#                         )
#                 else:
#                     cgst_found = any(
#                         'cgst' in tax.name.lower() and tax.amount == 9
#                         for tax in line.taxes_id
#                     )
#                     sgst_found = any(
#                         'sgst' in tax.name.lower() and tax.amount == 9
#                         for tax in line.taxes_id
#                     )
#                     if not cgst_found or not sgst_found:
#                         raise ValidationError(
#                             f"Invalid Tax: Intrastate purchase requires both CGST 9% and SGST 9% "
#                             f"on '{line.product_id.name}', but got {', '.join([t.name for t in line.taxes_id])}."
#                         )
#
#     def button_confirm(self):
#         """
#         Validate before confirming PO
#         """
#         self._check_tax_validation()
#         return super().button_confirm()


from odoo import models, api
from odoo.exceptions import ValidationError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'


    @api.onchange('partner_id', 'fiscal_position_id')
    def _onchange_partner_id_tax_setup(self):
        """
        Automatically set taxes based on fiscal position:
        - Intrastate: Purchase CGST 9% + Purchase SGST 9%
        - Interstate: Purchase IGST 18%
        - Export: No taxes
        - Import: No taxes
        """

        for order in self:

            if not order.partner_id:
                continue

            taxes_to_apply = order._get_auto_taxes(order.fiscal_position_id)

            for line in order.order_line:
                line.taxes_id = taxes_to_apply



    @api.onchange('order_line')
    def _onchange_order_line_auto_tax(self):
        """
        Auto apply taxes when new lines added
        """

        if self.partner_id and self.fiscal_position_id:

            taxes_to_apply = self._get_auto_taxes(
                self.fiscal_position_id
            )

            for line in self.order_line:

                if not line.taxes_id:
                    line.taxes_id = taxes_to_apply



    def _get_auto_taxes(self, fiscal_position):

        """
        Return taxes based on fiscal position
        """

        Tax = self.env['account.tax']

        if not fiscal_position:
            return Tax


        fiscal_position_name = (
            fiscal_position.name or ''
        ).lower()



        # Export / Import = No Tax
        if (
            'export' in fiscal_position_name
            or
            'import' in fiscal_position_name
        ):
            return Tax



        # Interstate = IGST
        if (
            'inter' in fiscal_position_name
            or
            'interstate' in fiscal_position_name
        ):

            igst_tax = Tax.search([
                ('name', 'ilike', 'IGST'),
                ('amount', '=', 18),
                ('type_tax_use', '=', 'purchase'),
                ('company_id', '=', self.company_id.id)
            ], limit=1)


            return igst_tax if igst_tax else Tax



        # Intrastate = CGST + SGST

        cgst_tax = Tax.search([
            ('name', 'ilike', 'CGST'),
            ('amount', '=', 9),
            ('type_tax_use', '=', 'purchase'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)


        sgst_tax = Tax.search([
            ('name', 'ilike', 'SGST'),
            ('amount', '=', 9),
            ('type_tax_use', '=', 'purchase'),
            ('company_id', '=', self.company_id.id)
        ], limit=1)



        return (
            cgst_tax + sgst_tax
            if cgst_tax and sgst_tax
            else Tax
        )




    @api.model_create_multi
    def create(self, vals_list):

        orders = super().create(vals_list)


        for order in orders:

            if (
                order.partner_id
                and
                order.fiscal_position_id
            ):

                taxes = order._get_auto_taxes(
                    order.fiscal_position_id
                )


                for line in order.order_line:

                    if not line.taxes_id:

                        line.write({
                            'taxes_id': [
                                (6, 0, taxes.ids)
                            ]
                        })


        return orders





    def write(self, vals):

        result = super().write(vals)


        if (
            'partner_id' in vals
            or
            'fiscal_position_id' in vals
        ):


            for order in self:


                if (
                    order.partner_id
                    and
                    order.fiscal_position_id
                ):


                    taxes = order._get_auto_taxes(
                        order.fiscal_position_id
                    )


                    for line in order.order_line:


                        if not line.taxes_id:

                            line.write({
                                'taxes_id': [
                                    (6,0,taxes.ids)
                                ]
                            })


        return result





    @api.constrains(
        'order_line',
        'fiscal_position_id',
        'partner_id'
    )
    def _check_tax_validation(self):


        for order in self:


            if (
                not order.partner_id
                or
                not order.fiscal_position_id
            ):
                continue



            fiscal_position_name = (
                order.fiscal_position_id.name or ''
            ).lower()



            # Export / Import no validation
            if (
                'export' in fiscal_position_name
                or
                'import' in fiscal_position_name
            ):
                continue




            for line in order.order_line:


                if (
                    not line.product_id
                    or
                    line.product_qty == 0
                ):
                    continue




                if not line.taxes_id:


                    if (
                        'inter' in fiscal_position_name
                        or
                        'interstate' in fiscal_position_name
                    ):


                        raise ValidationError(
                            f"Tax Missing: Interstate purchase requires IGST 18% tax "
                            f"on product '{line.product_id.name}'."
                        )

                    else:


                        raise ValidationError(
                            f"Tax Missing: Intrastate purchase requires CGST 9% and SGST 9% "
                            f"taxes on product '{line.product_id.name}'."
                        )





                # Interstate check

                if (
                    'inter' in fiscal_position_name
                    or
                    'interstate' in fiscal_position_name
                ):


                    igst_found = any(
                        'igst' in tax.name.lower()
                        and
                        tax.amount == 18
                        for tax in line.taxes_id
                    )


                    if not igst_found:

                        raise ValidationError(
                            f"Invalid Tax: Interstate purchase requires IGST 18% "
                            f"on '{line.product_id.name}'."
                        )




                # Intrastate check

                else:


                    cgst_found = any(
                        'cgst' in tax.name.lower()
                        and
                        tax.amount == 9
                        for tax in line.taxes_id
                    )


                    sgst_found = any(
                        'sgst' in tax.name.lower()
                        and
                        tax.amount == 9
                        for tax in line.taxes_id
                    )


                    if not cgst_found or not sgst_found:


                        raise ValidationError(
                            f"Invalid Tax: Intrastate purchase requires both CGST 9% "
                            f"and SGST 9% on '{line.product_id.name}'."
                        )




    def button_confirm(self):

        self._check_tax_validation()

        return super().button_confirm()