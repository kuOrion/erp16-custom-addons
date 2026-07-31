from odoo import models, fields


# orion menu
class TransporterOption(models.Model):
    _name = 'sale.transporter.option'
    _description = 'Transporter Option'

    name = fields.Char(string="Transporter", required=True)

class TermsAndConditionsOption(models.Model):
    _name = 'sale.terms.conditions.option'
    _description = 'Terms and Conditions Option'

    name = fields.Char(string="Terms and Conditions", required=True)



# orion-tax terms menu
class ValidityOption(models.Model):
    _name = 'sale.validity.option'
    _description = 'Validity Option'

    name = fields.Char(string='Validity Description', required=True)


class AccessoriesOption(models.Model):
    _name = 'sale.accessories.option'
    _description = 'Accessories Option'

    name = fields.Char(string='Accessories Description', required=True)


class PandFOption(models.Model):
    _name = 'sale.pandf.option'
    _description = 'Packaging and Freight Option'

    name = fields.Char(string='P & F Description', required=True)


class WarrantyOption(models.Model):
    _name = 'sale.warranty.option'
    _description = 'Warranty Option'

    name = fields.Text(string='Warranty Description', required=True)

class PriceTermOption(models.Model):
    _name = 'sale.price.term.option'
    _description = 'Price Term Option'

    name = fields.Char(string="Price Term", required=True)

class DeliveryOption(models.Model):
    _name = 'sale.delivery.option'
    _description = 'Delivery Option'

    name = fields.Char(string="Delivery", required=True)


class TPIOption(models.Model):
    _name = 'sale.third.party.inspection.option'
    _description = 'Third Party Inspection Option'

    name = fields.Text(string="Inspection Info", required=True)

class BankChargesOption(models.Model):
    _name = 'sale.bank.charges.option'
    _description = 'Bank Charges Option'

    name = fields.Char(string="Bank Charges", required=True)


class ModeOfTransportOption(models.Model):
    _name = 'sale.mode.transport.option'
    _description = 'Mode of Transport Option'

    name = fields.Char(string="Mode of Transport", required=True)


class OtherTermOption(models.Model):
    _name = 'sale.other.term.option'
    _description = 'Other Term Option'

    name = fields.Text(string="Other Term", required=True)

class PreCarriageOption(models.Model):
    _name = 'sale.pre.carriage.option'
    _description = 'Pre Carriage Option'

    name = fields.Char(string="Pre Carriage", required=True)

