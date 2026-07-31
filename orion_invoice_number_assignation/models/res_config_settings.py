# import re
# from odoo import api, fields, models
#
#
# class ResConfigSettings(models.TransientModel):
#     _inherit = 'res.config.settings'
#
#     invoice_number_prefix = fields.Char(
#         string='Invoice Number Prefix',
#         config_parameter='custom_invoice_prefix.invoice_number_prefix',
#     )
#     invoice_number_padding = fields.Integer(
#         string='Invoice Number Padding (Digits)',
#         config_parameter='custom_invoice_prefix.invoice_number_padding',
#         default=4,
#     )
#     credit_note_number_prefix = fields.Char(
#         string='Credit Note Number Prefix',
#         config_parameter='custom_invoice_prefix.credit_note_number_prefix',
#     )
#
#     @api.model
#     def get_values(self):
#         res = super().get_values()
#         ICP = self.env['ir.config_parameter'].sudo()
#         res.update(
#             invoice_number_prefix=ICP.get_param(
#                 'custom_invoice_prefix.invoice_number_prefix', default=''),
#             invoice_number_padding=int(ICP.get_param(
#                 'custom_invoice_prefix.invoice_number_padding', default=4)),
#             credit_note_number_prefix=ICP.get_param(
#                 'custom_invoice_prefix.credit_note_number_prefix', default=''),
#         )
#         return res
#
#     def set_values(self):
#         super().set_values()
#         ICP = self.env['ir.config_parameter'].sudo()
#         ICP.set_param('custom_invoice_prefix.invoice_number_prefix',
#                       self.invoice_number_prefix or '')
#         ICP.set_param('custom_invoice_prefix.invoice_number_padding',
#                       self.invoice_number_padding or 4)
#         ICP.set_param('custom_invoice_prefix.credit_note_number_prefix',
#                       self.credit_note_number_prefix or '')
#
#     # ------------------------------------------------------------------
#     # Counter management helpers (called from settings buttons)
#     # ------------------------------------------------------------------
#     def _reset_counter_for(self, prefix):
#         ICP = self.env['ir.config_parameter'].sudo()
#         safe = re.sub(r'[^a-zA-Z0-9_]', '_', prefix or 'blank')
#         ICP.set_param(f'custom_invoice_prefix.counter.{safe}', '0')
#
#     def action_reset_invoice_counter(self):
#         self._reset_counter_for(self.invoice_number_prefix)
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'display_notification',
#             'params': {
#                 'title': 'Counter Reset',
#                 'message': f'Invoice counter for "{self.invoice_number_prefix}" reset to 0.',
#                 'type': 'success',
#             }
#         }
#
#     def action_reset_credit_note_counter(self):
#         self._reset_counter_for(self.credit_note_number_prefix)
#         return {
#             'type': 'ir.actions.client',
#             'tag': 'display_notification',
#             'params': {
#                 'title': 'Counter Reset',
#                 'message': f'Credit note counter for "{self.credit_note_number_prefix}" reset to 0.',
#                 'type': 'success',
#             }
#         }


import re
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_number_prefix = fields.Char(
        string='Invoice Number Prefix',
        config_parameter='custom_invoice_prefix.invoice_number_prefix',
    )

    invoice_number_padding = fields.Integer(
        string='Invoice Number Padding (Digits)',
        config_parameter='custom_invoice_prefix.invoice_number_padding',
        default=4,
    )

    credit_note_number_prefix = fields.Char(
        string='Credit Note Number Prefix',
        config_parameter='custom_invoice_prefix.credit_note_number_prefix',
    )

    # next_invoice_number = fields.Char(
    #     string='Next Invoice Number',
    #     compute='_compute_next_invoice_number',
    #     readonly=True,
    # )
    #
    # next_credit_note_number = fields.Char(
    #     string='Next Credit Note Number',
    #     compute='_compute_next_credit_note_number',
    #     readonly=True,
    # )

    next_invoice_counter = fields.Integer(
        string='Next Invoice Number',
        config_parameter='custom_invoice_prefix.next_invoice_counter',
        default=1,
    )

    next_credit_note_counter = fields.Integer(
        string='Next Credit Note Number',
        config_parameter='custom_invoice_prefix.next_credit_note_counter',
        default=1,
    )

    @api.depends(
        'invoice_number_prefix',
        'invoice_number_padding',
    )
    def _compute_next_invoice_number(self):
        ICP = self.env['ir.config_parameter'].sudo()

        for rec in self:
            prefix = rec.invoice_number_prefix or ''
            padding = rec.invoice_number_padding or 4

            safe = re.sub(r'[^a-zA-Z0-9_]', '_', prefix or 'blank')

            current = int(
                ICP.get_param(
                    f'custom_invoice_prefix.counter.{safe}',
                    default='0'
                )
            )

            if prefix:
                rec.next_invoice_number = (
                    f"{prefix}{str(current + 1).zfill(padding)}"
                )
            else:
                rec.next_invoice_number = 'Odoo Default Sequence'

    @api.depends(
        'credit_note_number_prefix',
        'invoice_number_padding',
    )
    def _compute_next_credit_note_number(self):
        ICP = self.env['ir.config_parameter'].sudo()

        for rec in self:
            prefix = rec.credit_note_number_prefix or ''
            padding = rec.invoice_number_padding or 4

            safe = re.sub(r'[^a-zA-Z0-9_]', '_', prefix or 'blank')

            current = int(
                ICP.get_param(
                    f'custom_invoice_prefix.counter.{safe}',
                    default='0'
                )
            )

            if prefix:
                rec.next_credit_note_number = (
                    f"{prefix}{str(current + 1).zfill(padding)}"
                )
            else:
                rec.next_credit_note_number = 'Odoo Default Sequence'

    # @api.model
    # def get_values(self):
    #     res = super().get_values()
    #
    #     ICP = self.env['ir.config_parameter'].sudo()
    #
    #     res.update(
    #         invoice_number_prefix=ICP.get_param(
    #             'custom_invoice_prefix.invoice_number_prefix',
    #             default=''
    #         ),
    #         invoice_number_padding=int(
    #             ICP.get_param(
    #                 'custom_invoice_prefix.invoice_number_padding',
    #                 default=4
    #             )
    #         ),
    #         credit_note_number_prefix=ICP.get_param(
    #             'custom_invoice_prefix.credit_note_number_prefix',
    #             default=''
    #         ),
    #     )
    #
    #     return res

    @api.model
    def get_values(self):
        res = super().get_values()

        ICP = self.env['ir.config_parameter'].sudo()

        res.update(
            invoice_number_prefix=ICP.get_param(
                'custom_invoice_prefix.invoice_number_prefix',
                default=''
            ),
            invoice_number_padding=int(
                ICP.get_param(
                    'custom_invoice_prefix.invoice_number_padding',
                    default=4
                )
            ),
            credit_note_number_prefix=ICP.get_param(
                'custom_invoice_prefix.credit_note_number_prefix',
                default=''
            ),
            next_invoice_counter=int(
                ICP.get_param(
                    'custom_invoice_prefix.next_invoice_counter',
                    default=1
                )
            ),
            next_credit_note_counter=int(
                ICP.get_param(
                    'custom_invoice_prefix.next_credit_note_counter',
                    default=1
                )
            ),
        )

        return res

    # def set_values(self):
    #     super().set_values()
    #
    #     ICP = self.env['ir.config_parameter'].sudo()
    #
    #     ICP.set_param(
    #         'custom_invoice_prefix.invoice_number_prefix',
    #         self.invoice_number_prefix or ''
    #     )
    #
    #     ICP.set_param(
    #         'custom_invoice_prefix.invoice_number_padding',
    #         self.invoice_number_padding or 4
    #     )
    #
    #     ICP.set_param(
    #         'custom_invoice_prefix.credit_note_number_prefix',
    #         self.credit_note_number_prefix or ''
    #     )

    def set_values(self):
        super().set_values()

        ICP = self.env['ir.config_parameter'].sudo()

        ICP.set_param(
            'custom_invoice_prefix.invoice_number_prefix',
            self.invoice_number_prefix or ''
        )

        ICP.set_param(
            'custom_invoice_prefix.invoice_number_padding',
            self.invoice_number_padding or 4
        )

        ICP.set_param(
            'custom_invoice_prefix.credit_note_number_prefix',
            self.credit_note_number_prefix or ''
        )

        ICP.set_param(
            'custom_invoice_prefix.next_invoice_counter',
            self.next_invoice_counter or 1
        )

        ICP.set_param(
            'custom_invoice_prefix.next_credit_note_counter',
            self.next_credit_note_counter or 1
        )

    # ------------------------------------------------------------
    # Counter helpers
    # ------------------------------------------------------------
    def _reset_counter_for(self, prefix):
        ICP = self.env['ir.config_parameter'].sudo()

        safe = re.sub(
            r'[^a-zA-Z0-9_]',
            '_',
            prefix or 'blank'
        )

        ICP.set_param(
            f'custom_invoice_prefix.counter.{safe}',
            '0'
        )

    def action_reset_invoice_counter(self):
        self._reset_counter_for(
            self.invoice_number_prefix
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Counter Reset',
                'message': (
                    f'Invoice counter for '
                    f'"{self.invoice_number_prefix}" '
                    f'reset to 0.'
                ),
                'type': 'success',
            }
        }

    def action_reset_credit_note_counter(self):
        self._reset_counter_for(
            self.credit_note_number_prefix
        )

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Counter Reset',
                'message': (
                    f'Credit note counter for '
                    f'"{self.credit_note_number_prefix}" '
                    f'reset to 0.'
                ),
                'type': 'success',
            }
        }