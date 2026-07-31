# # from odoo import models, fields, api, _
# # from datetime import datetime
# #
# #
# # class SaleOrder(models.Model):
# #     _inherit = 'sale.order'
# #
# #     is_converted_to_order = fields.Boolean(string="Converted to Order", default=False)
# #     original_quotation_name = fields.Char(string="Quotation No", readonly=True)
# #
# #     @api.model
# #     def create(self, vals):
# #         if not vals.get('name') or vals['name'] == _('New'):
# #             partner_id = vals.get('partner_id')
# #             is_export = False
# #
# #             icp = self.env['ir.config_parameter'].sudo()
# #             domestic_prefix = icp.get_param('orion.quotation_prefix', default='KQ')
# #             export_prefix = icp.get_param('orion.export_quotation_prefix', default='KQ/EX')
# #
# #             if partner_id:
# #                 partner = self.env['res.partner'].browse(partner_id)
# #                 fiscal_position = partner.property_account_position_id
# #                 is_export = fiscal_position and 'export' in fiscal_position.name.lower()
# #
# #             if is_export:
# #                 prefix = f'{export_prefix}/'
# #                 # next_number = self._get_next_sequence_number('quotation_export')
# #                 next_number = self._get_next_sequence_number('quotation_export', prefix)
# #
# #             else:
# #                 prefix = f'{domestic_prefix}/'
# #                 # next_number = self._get_next_sequence_number('quotation_domestic')
# #                 next_number = self._get_next_sequence_number('quotation_domestic', prefix)
# #
# #             quotation_name = f"{prefix}{next_number:05d}"
# #             vals['name'] = quotation_name
# #             vals['original_quotation_name'] = quotation_name
# #         return super(SaleOrder, self).create(vals)
# #
# #     def action_confirm(self):
# #         res = super(SaleOrder, self).action_confirm()
# #         icp = self.env['ir.config_parameter'].sudo()
# #         order_prefix = icp.get_param('orion.order_prefix', default='OA')
# #
# #         for order in self:
# #             prefix = f"{order_prefix}/"
# #             # next_number = self._get_next_sequence_number('order')
# #             next_number = self._get_next_sequence_number('order', prefix)
# #
# #             order.name = f"{prefix}{next_number:05d}"
# #             order.is_converted_to_order = True
# #         return res
# #
# #     def action_draft(self):
# #         res = super(SaleOrder, self).action_draft()
# #         icp = self.env['ir.config_parameter'].sudo()
# #
# #         domestic_prefix = icp.get_param('orion.quotation_prefix', default='KQ')
# #         export_prefix = icp.get_param('orion.export_quotation_prefix', default='KQ/EX')
# #
# #         for order in self:
# #             if order.is_converted_to_order:
# #                 partner = order.partner_id
# #                 is_export = False
# #                 if partner:
# #                     fiscal_position = partner.property_account_position_id
# #                     is_export = fiscal_position and 'export' in fiscal_position.name.lower()
# #
# #                 if is_export:
# #                     prefix = f'{export_prefix}/'
# #                     next_number = self._get_next_sequence_number('quotation_export')
# #                 else:
# #                     prefix = f'{domestic_prefix}/'
# #                     next_number = self._get_next_sequence_number('quotation_domestic')
# #
# #                 quotation_name = f"{prefix}{next_number:05d}"
# #                 order.name = quotation_name
# #                 order.original_quotation_name = quotation_name
# #                 order.is_converted_to_order = False
# #         return res
# #
# #     # def _get_next_sequence_number(self, key):
# #     #     param_key = f'orion.{key}_next_number'
# #     #     icp = self.env['ir.config_parameter'].sudo()
# #     #     current = int(icp.get_param(param_key, default='1'))
# #     #     icp.set_param(param_key, str(current + 1))
# #     #     return current
# #
# #     def _get_next_sequence_number(self, key, current_prefix):
# #         icp = self.env['ir.config_parameter'].sudo()
# #         prefix_key = f'orion.{key}_last_prefix'
# #         number_key = f'orion.{key}_next_number'
# #
# #         last_prefix = icp.get_param(prefix_key, default='')
# #
# #         # If prefix changed, reset counter to 1
# #         if last_prefix != current_prefix:
# #             next_number = 1
# #             icp.set_param(prefix_key, current_prefix)
# #         else:
# #             next_number = int(icp.get_param(number_key, default='1'))
# #
# #         # Save updated number
# #         icp.set_param(number_key, str(next_number + 1))
# #         return next_number
# #
#
#
#
# from odoo import models, fields, api, _
# from datetime import datetime
#
#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     is_converted_to_order = fields.Boolean(string="Converted to Order", default=False)
#     original_quotation_name = fields.Char(string="Quotation No", readonly=True)
#
#     @api.model
#     def create(self, vals):
#         if not vals.get('name') or vals['name'] == _('New'):
#             partner_id = vals.get('partner_id')
#             is_export = False
#
#             icp = self.env['ir.config_parameter'].sudo()
#             domestic_prefix = icp.get_param('orion.quotation_prefix', default='KQ')
#             export_prefix = icp.get_param('orion.export_quotation_prefix', default='KQ/EX')
#
#             if partner_id:
#                 partner = self.env['res.partner'].browse(partner_id)
#                 fiscal_position = partner.property_account_position_id
#                 is_export = fiscal_position and 'export' in fiscal_position.name.lower()
#
#             if is_export:
#                 prefix = f'{export_prefix}/'
#                 next_number = self._get_next_sequence_number('quotation_export', prefix)
#             else:
#                 prefix = f'{domestic_prefix}/'
#                 next_number = self._get_next_sequence_number('quotation_domestic', prefix)
#
#             quotation_name = f"{prefix}{next_number:05d}"
#             vals['name'] = quotation_name
#             vals['original_quotation_name'] = quotation_name
#         return super(SaleOrder, self).create(vals)
#
#     def action_confirm(self):
#         res = super(SaleOrder, self).action_confirm()
#         icp = self.env['ir.config_parameter'].sudo()
#         order_prefix = icp.get_param('orion.order_prefix', default='OA')
#
#         for order in self:
#             prefix = f"{order_prefix}/"
#             next_number = self._get_next_sequence_number('order', prefix)
#             order.name = f"{prefix}{next_number:05d}"
#             order.is_converted_to_order = True
#         return res
#
#     def action_draft(self):
#         res = super(SaleOrder, self).action_draft()
#         icp = self.env['ir.config_parameter'].sudo()
#
#         domestic_prefix = icp.get_param('orion.quotation_prefix', default='KQ')
#         export_prefix = icp.get_param('orion.export_quotation_prefix', default='KQ/EX')
#
#         for order in self:
#             if order.is_converted_to_order:
#                 partner = order.partner_id
#                 is_export = False
#                 if partner:
#                     fiscal_position = partner.property_account_position_id
#                     is_export = fiscal_position and 'export' in fiscal_position.name.lower()
#
#                 if is_export:
#                     prefix = f'{export_prefix}/'
#                     next_number = self._get_next_sequence_number('quotation_export', prefix)
#                 else:
#                     prefix = f'{domestic_prefix}/'
#                     next_number = self._get_next_sequence_number('quotation_domestic', prefix)
#
#                 quotation_name = f"{prefix}{next_number:05d}"
#                 order.name = quotation_name
#                 order.original_quotation_name = quotation_name
#                 order.is_converted_to_order = False
#         return res
#
#     def _get_next_sequence_number(self, key, current_prefix):
#         icp = self.env['ir.config_parameter'].sudo()
#         # Remove trailing slash to avoid issues in key names
#         clean_prefix = current_prefix.rstrip('/')
#
#         param_key = f'orion.{key}.{clean_prefix}.next_number'
#         current = int(icp.get_param(param_key, default='1'))
#         icp.set_param(param_key, str(current + 1))
#         return current

from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_converted_to_order = fields.Boolean(string="Converted to Order", default=False)
    original_quotation_name = fields.Char(string="Quotation No", readonly=True)

    @api.model
    def create(self, vals):
        _logger.info("Creating Sale Order with vals: %s", vals)

        # Block fallback to default Odoo sequence like S00...
        if not vals.get('name') or vals.get('name').startswith('S') or vals['name'] == _('New'):
            partner_id = vals.get('partner_id')
            is_export = False

            icp = self.env['ir.config_parameter'].sudo()
            domestic_prefix = icp.get_param('orion.quotation_prefix', default='KQ')
            export_prefix = icp.get_param('orion.export_quotation_prefix', default='KQ/EX')

            if partner_id:
                partner = self.env['res.partner'].browse(partner_id)
                fiscal_position = partner.property_account_position_id
                is_export = fiscal_position and 'export' in fiscal_position.name.lower()

            if is_export:
                prefix = f'{export_prefix}/'
                next_number = self._get_next_sequence_number('quotation_export', prefix)
            else:
                prefix = f'{domestic_prefix}/'
                next_number = self._get_next_sequence_number('quotation_domestic', prefix)

            quotation_name = f"{prefix}{next_number:05d}"
            vals['name'] = quotation_name
            vals['original_quotation_name'] = quotation_name
        else:
            _logger.warning("Custom sequence logic skipped; using existing name: %s", vals.get('name'))

        return super(SaleOrder, self).create(vals)

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        icp = self.env['ir.config_parameter'].sudo()
        order_prefix = icp.get_param('orion.order_prefix', default='OA')

        for order in self:
            prefix = f"{order_prefix}/"
            next_number = self._get_next_sequence_number('order', prefix)
            order.name = f"{prefix}{next_number:05d}"
            order.is_converted_to_order = True
            _logger.info("Confirmed sale order with new name: %s", order.name)
        return res

    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        icp = self.env['ir.config_parameter'].sudo()

        domestic_prefix = icp.get_param('orion.quotation_prefix', default='KQ')
        export_prefix = icp.get_param('orion.export_quotation_prefix', default='KQ/EX')

        for order in self:
            if order.is_converted_to_order:
                partner = order.partner_id
                is_export = False
                if partner:
                    fiscal_position = partner.property_account_position_id
                    is_export = fiscal_position and 'export' in fiscal_position.name.lower()

                if is_export:
                    prefix = f'{export_prefix}/'
                    next_number = self._get_next_sequence_number('quotation_export', prefix)
                else:
                    prefix = f'{domestic_prefix}/'
                    next_number = self._get_next_sequence_number('quotation_domestic', prefix)

                quotation_name = f"{prefix}{next_number:05d}"
                order.name = quotation_name
                order.original_quotation_name = quotation_name
                order.is_converted_to_order = False
                _logger.info("Reset to draft with new quotation number: %s", quotation_name)
        return res

    def _get_next_sequence_number(self, key, current_prefix):
        icp = self.env['ir.config_parameter'].sudo()
        clean_prefix = current_prefix.rstrip('/')
        param_key = f'orion.{key}.{clean_prefix}.next_number'
        current = int(icp.get_param(param_key, default='1'))
        icp.set_param(param_key, str(current + 1))
        return current

    @api.model
    def _get_default_name_sequence(self):
        # Prevent default sequence fallback
        return False
