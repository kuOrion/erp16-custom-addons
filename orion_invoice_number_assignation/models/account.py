import re
from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'

    # -----------------------------------------------------------------------
    # Counter helpers
    # -----------------------------------------------------------------------
    def _get_prefix_counter_key(self, prefix):
        safe = re.sub(r'[^a-zA-Z0-9_]', '_', prefix or 'blank')
        return f'custom_invoice_prefix.counter.{safe}'

    # def _get_next_number_for_prefix(self, prefix, padding):
    #     ICP = self.env['ir.config_parameter'].sudo()
    #     key = self._get_prefix_counter_key(prefix)
    #     # Use SELECT FOR UPDATE to prevent race conditions across workers
    #     self.env.cr.execute(
    #         "SELECT value FROM ir_config_parameter WHERE key = %s FOR UPDATE",
    #         (key,)
    #     )
    #     row = self.env.cr.fetchone()
    #     current = int(row[0]) if row else 0
    #     next_val = current + 1
    #     ICP.set_param(key, str(next_val))
    #     return str(next_val).zfill(padding) if padding > 0 else str(next_val)

    def _get_next_number_for_prefix(self, prefix, padding):
        ICP = self.env['ir.config_parameter'].sudo()

        is_credit = self.move_type in ('out_refund', 'in_refund')

        if is_credit:

            current = int(
                ICP.get_param(
                    'custom_invoice_prefix.next_credit_note_counter',
                    default='1'
                )
            )

            ICP.set_param(
                'custom_invoice_prefix.next_credit_note_counter',
                str(current + 1)
            )

        else:

            current = int(
                ICP.get_param(
                    'custom_invoice_prefix.next_invoice_counter',
                    default='1'
                )
            )

            ICP.set_param(
                'custom_invoice_prefix.next_invoice_counter',
                str(current + 1)
            )

        return str(current).zfill(padding)

    def _peek_current_number_for_prefix(self, prefix):
        """Return current counter without incrementing (for display)."""
        ICP = self.env['ir.config_parameter'].sudo()
        key = self._get_prefix_counter_key(prefix)
        return int(ICP.get_param(key, default=0))

    # -----------------------------------------------------------------------
    # Settings helpers
    # -----------------------------------------------------------------------
    def _get_invoice_prefix_and_padding(self):
        ICP = self.env['ir.config_parameter'].sudo()
        prefix = ICP.get_param(
            'custom_invoice_prefix.invoice_number_prefix', default='')
        padding = int(ICP.get_param(
            'custom_invoice_prefix.invoice_number_padding', default=4))
        credit_prefix = ICP.get_param(
            'custom_invoice_prefix.credit_note_number_prefix', default='')
        return prefix, padding, credit_prefix

    def _get_active_prefix_and_padding(self):
        """Return (active_prefix, padding) for this specific move."""
        prefix, padding, credit_prefix = self._get_invoice_prefix_and_padding()
        is_credit = self.move_type in ('out_refund', 'in_refund')
        active_prefix = credit_prefix if (is_credit and credit_prefix) else prefix
        return active_prefix, padding

    def _is_custom_prefix_enabled(self):
        prefix, padding, credit_prefix = self._get_invoice_prefix_and_padding()
        return bool(prefix or credit_prefix)

    # -----------------------------------------------------------------------
    # Override _set_next_sequence — fires BEFORE Odoo writes the name
    # This is the correct interception point in Odoo 16
    # -----------------------------------------------------------------------
    def _set_next_sequence(self):
        """
        Called by Odoo when it is about to assign the sequence name.
        We intercept here so we own the name from the start — no
        conflict with Odoo's own sequence engine.
        """
        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund'):
                # Not an outgoing invoice/credit note — use Odoo default
                super(AccountMove, move)._set_next_sequence()
                continue

            active_prefix, padding = move._get_active_prefix_and_padding()

            if not active_prefix:
                # No custom prefix configured — use Odoo default
                super(AccountMove, move)._set_next_sequence()
                continue

            # Build our custom name using our own counter
            padded = move._get_next_number_for_prefix(active_prefix, padding)
            new_name = f'{active_prefix}{padded}'

            # Write directly, bypassing Odoo's sequence machinery entirely
            # skip_invoice_prefix prevents our _post hook from double-incrementing
            move.with_context(
                skip_invoice_prefix=True,
                ir_sequence_date=None,
            ).write({'name': new_name})

    # -----------------------------------------------------------------------
    # Override _post — safety net in case _set_next_sequence was skipped
    # (e.g. invoice confirmed via button after draft with name already set)
    # -----------------------------------------------------------------------
    def _post(self, soft=True):
        res = super()._post(soft=soft)
        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund'):
                continue
            if self.env.context.get('skip_invoice_prefix'):
                continue

            active_prefix, padding = move._get_active_prefix_and_padding()
            if not active_prefix:
                continue

            # Only re-apply if the current name does NOT already start with
            # our prefix — meaning _set_next_sequence already handled it
            if move.name and move.name.startswith(active_prefix):
                continue

            # Name was set by Odoo's engine without our prefix — replace it
            padded = move._get_next_number_for_prefix(active_prefix, padding)
            new_name = f'{active_prefix}{padded}'
            move.with_context(skip_invoice_prefix=True).write({'name': new_name})

        return res

    # -----------------------------------------------------------------------
    # Remove Odoo 16's 16-character name length restriction
    # -----------------------------------------------------------------------
    def _check_move_sequence_constraints(self, sequence):
        try:
            return super()._check_move_sequence_constraints(sequence)
        except UserError as e:
            if '16' not in str(e) and 'characters' not in str(e).lower():
                raise

    # -----------------------------------------------------------------------
    # Replace uniqueness check — remove the length check Odoo bundles in
    # -----------------------------------------------------------------------
    @api.constrains('name', 'journal_id', 'state')
    def _check_unique_sequence_number(self):
        moves = self.filtered(lambda m: m.state == 'posted')
        if not moves:
            return

        self.flush_model(['name', 'journal_id', 'move_type', 'state'])

        self._cr.execute('''
            SELECT move2.id
              FROM account_move move
              JOIN account_move move2
                ON move2.name       = move.name
               AND move2.journal_id = move.journal_id
               AND move2.move_type  = move.move_type
               AND move2.id        != move.id
             WHERE move.id IN %s
               AND move2.state = 'posted'
        ''', [tuple(moves.ids)])

        if self._cr.fetchone():
            raise UserError(
                self.env._('Duplicated invoice/bill number detected. '
                           'Make sure your prefix and padding produce a unique sequence.')
            )

    # -----------------------------------------------------------------------
    # Accept Odoo 16's lock kwarg
    # -----------------------------------------------------------------------
    def _get_last_sequence(self, relaxed=False, with_prefix=None, lock=True):
        return super()._get_last_sequence(
            relaxed=relaxed, with_prefix=with_prefix, lock=lock)