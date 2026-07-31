from odoo import models, fields


# =========================
# Master Models
# =========================

class PurchaseModePayment(models.Model):
    _name = 'purchase.mode.payment'
    _description = 'Mode of Payment'

    name = fields.Char(string='Mode of Payment', required=True)


class PurchaseFreightType(models.Model):
    _name = 'purchase.freight.type'
    _description = 'Freight Type'

    name = fields.Char(string='Freight Type', required=True)


class PurchaseInspection(models.Model):
    _name = 'purchase.inspection'
    _description = 'Inspection'

    name = fields.Text(string='Inspection', required=True)


class PurchaseInsurance(models.Model):
    _name = 'purchase.insurance'
    _description = 'Insurance'

    name = fields.Char(string='Insurance', required=True)


class PurchasePacking(models.Model):
    _name = 'purchase.packing'
    _description = 'Packing'

    name = fields.Char(string='Packing', required=True)


class PurchaseTransportMode(models.Model):
    _name = 'purchase.transport.mode'
    _description = 'Mode of Transport'

    name = fields.Char(string='Mode of Transport', required=True)

class Delivery(models.Model):
    _name = 'purchase.delivery'
    _description = 'delivery'

    name = fields.Char(string='Delivery', required=True)


# =========================
# Purchase Order Inherit
# =========================

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    payment_term = fields.Many2one(
        'account.payment.term',
        string="Payment Term"
    )

    delivery = fields.Many2one(
        'purchase.delivery',
        string="Delivery"
    )

    mode_of_payment_id = fields.Many2one(
        'purchase.mode.payment',
        string="Mode of Payment"
    )

    freight_id = fields.Many2one(
        'purchase.freight.type',
        string="Freight"
    )

    amount_freight = fields.Monetary(
        string='Freight Amount',
        store=True,
        readonly=True,
        compute='_amount_all'
    )

    freight_tax = fields.Many2many(
        'account.tax',
        relation='account_tax_freight_purchase_tax_rel',
        string='Freight Taxes'
    )

    inspection_id = fields.Many2one(
        'purchase.inspection',
        string="Inspection"
    )

    insurance_id = fields.Many2one(
        'purchase.insurance',
        string="Insurance"
    )

    insurance_tax = fields.Many2many(
        'account.tax',
        relation='account_tax_insurance_purchase_tax_rel',
        string='Insurance Taxes'
    )

    # delivery = fields.Text(string="Delivery")

    packing_id = fields.Many2one(
        'purchase.packing',
        string="Packing"
    )

    packch_tax = fields.Many2many(
        'account.tax',
        relation='account_tax_packch_purchase_tax_rel',
        string='Packaging Taxes'
    )

    mode_of_transport_id = fields.Many2one(
        'purchase.transport.mode',
        string="Mode of Transport"
    )
