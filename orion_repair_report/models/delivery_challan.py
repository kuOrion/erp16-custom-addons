from odoo import models, fields
import pytz

class RepairOrder(models.Model):
    _inherit = 'repair.order'

    quotation_notes = fields.Text(
        string='Quotation Notes'
    )
    internal_notes = fields.Text(
        string='Internal Notes'
    )

    repair_fee_ids = fields.One2many(
        'repair.fee',
        'repair_id',
        string='Operations'
    )

    def format_datetime_user(self, dt):
        """Return datetime in user timezone (IST etc.) for Py3O reports"""
        if not dt:
            return ''

        user_tz = pytz.timezone(self.env.user.tz or 'UTC')

        dt = fields.Datetime.from_string(dt)
        dt = pytz.utc.localize(dt).astimezone(user_tz)

        return dt.strftime('%d-%b-%Y %H:%M:%S')




