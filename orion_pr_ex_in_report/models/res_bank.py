from odoo import api, fields, models


class ResBank(models.Model):
    _inherit = 'res.bank'

    account_name = fields.Char('Acoount Name', default='KAUSTUBHA UDYOG')
    account_number = fields.Char('Account Number', default='0007059701')
    swift_code = fields.Char('Swift Code', default='CITIINBX')
    ifsc_code = fields.Char('IFSC Code')
    phone = fields.Char('Phone')
    fax = fields.Char('Fax')