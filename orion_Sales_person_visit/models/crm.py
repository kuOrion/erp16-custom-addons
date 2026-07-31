from odoo import models, fields, api
from odoo.exceptions import UserError

# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    sales_visit_id = fields.Many2one(
        'crm.sales.visit',
        string='Sales Visit'
    )

    handling_type = fields.Selection([
        ('internal', 'Handle Internally'),
        ('dealer', 'Forward to Dealer'),
    ], string='Handling Type', tracking=True)

    dealer_id = fields.Many2one(
        'res.partner',
        string='Dealer',
        domain=[],
        tracking=True
    )

    followup_ids = fields.One2many(
        'crm.opportunity.followup',
        'lead_id',
        string='Follow-ups'
    )

    followup_count = fields.Integer(
        string='Follow-up Count',
        compute='_compute_followup_count'
    )

    @api.depends('followup_ids')
    def _compute_followup_count(self):
        for rec in self:
            rec.followup_count = len(rec.followup_ids)

    def action_view_followups(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Follow-ups',
            'res_model': 'crm.opportunity.followup',
            'view_mode': 'tree,form',
            'domain': [('lead_id', '=', self.id)],
            'context': {
                'default_lead_id': self.id,
                'default_user_id': self.user_id.id,
            }
        }

    def action_make_call(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Log Call',
            'res_model': 'crm.opportunity.followup',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_lead_id': self.id,
                'default_user_id': self.user_id.id,
                'default_followup_type': 'call',
            }
        }

class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_dealer = fields.Boolean(string='Is a Dealer', default=False)


# class CrmSalesVisit(models.Model):
#     _name = 'crm.sales.visit'
#     _description = 'Sales Visit'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _order = 'visit_date desc'
#
#     name = fields.Char(
#         string='Visit Reference',
#         required=True,
#         copy=False,
#         default='New'
#     )

class CrmSalesVisit(models.Model):
    _name = 'crm.sales.visit'
    _description = 'Sales Visit'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'visit_date desc'

    name = fields.Char(
        string='Visit Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('crm.sales.visit') or 'New'
        return super(CrmSalesVisit, self).create(vals)

    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        tracking=True
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        tracking=True
    )

    visit_date = fields.Datetime(
        string='Visit Date',
        default=fields.Datetime.now,
        tracking=True
    )

    visit_type = fields.Selection([
        ('visit', 'Customer Visit'),
        ('call', 'Call'),
        ('meeting', 'Meeting'),
    ], string='Interaction Type', required=True, tracking=True)

    purpose = fields.Text(string='Purpose of Visit')
    discussion = fields.Text(string='Discussion / Notes')
    outcome = fields.Selection([
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ], string='Outcome', tracking=True)

    next_followup_date = fields.Date(string='Next Follow-up Date')

    lead_ids = fields.One2many(
        'crm.lead',
        'sales_visit_id',
        string='Generated Opportunities'
    )

    lead_count = fields.Integer(
        string='Opportunity Count',
        compute='_compute_lead_count'
    )

    @api.depends('lead_ids')
    def _compute_lead_count(self):
        for rec in self:
            rec.lead_count = len(rec.lead_ids)

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('crm.sales.visit') or 'New'
        return super().create(vals)

    def action_create_lead(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Create Opportunity',
            'res_model': 'crm.lead',
            'view_mode': 'form',
            'context': {
                'default_partner_id': self.partner_id.id,
                'default_user_id': self.user_id.id,
                'default_sales_visit_id': self.id,
            }
        }


class CrmOpportunityFollowup(models.Model):
    _name = 'crm.opportunity.followup'
    _description = 'Opportunity Follow-up'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'followup_date desc'

    name = fields.Char(
        string='Follow-up Reference',
        required=True,
        copy=False,
        readonly=True,
        default='New'
    )

    visit_id = fields.Many2one(
        'crm.sales.visit',
        string='Related Visit',
        ondelete='cascade'
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            # Generate the follow-up sequence number
            followup_seq = self.env['ir.sequence'].next_by_code('crm.opportunity.followup') or 'New'

            # Check if this follow-up is related to a visit
            if vals.get('visit_id'):
                visit = self.env['crm.sales.visit'].browse(vals['visit_id'])
                # Combine visit reference with follow-up sequence
                vals['name'] = f"{visit.name}/{followup_seq}"
            else:
                # Just use the follow-up sequence
                vals['name'] = followup_seq

        return super(CrmOpportunityFollowup, self).create(vals)

# class CrmOpportunityFollowup(models.Model):
#     _name = 'crm.opportunity.followup'
#     _description = 'Opportunity Follow-up'
#     _inherit = ['mail.thread', 'mail.activity.mixin']
#     _order = 'followup_date desc'
#
#     name = fields.Char(
#         string='Follow-up Reference',
#         required=True,
#         copy=False,
#         default='New'
#     )

    lead_id = fields.Many2one(
        'crm.lead',
        string='Opportunity',
        required=True,
        ondelete='cascade'
    )

    user_id = fields.Many2one(
        'res.users',
        string='Salesperson',
        default=lambda self: self.env.user,
        required=True
    )

    followup_date = fields.Datetime(
        string='Follow-up Date',
        default=fields.Datetime.now,
        required=True
    )

    followup_type = fields.Selection([
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('visit', 'Visit'),
    ], string='Follow-up Type', required=True, default='call')

    description = fields.Text(string='Description')

    status = fields.Selection([
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='pending', tracking=True)

    next_action = fields.Text(string='Next Action Required')
    next_followup_date = fields.Date(string='Next Follow-up Date')

    dealer_feedback = fields.Text(
        string='Dealer Feedback',
        help='Feedback received from dealer for forwarded opportunities'
    )

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('crm.opportunity.followup') or 'New'
        return super().create(vals)

    def action_mark_completed(self):
        self.write({'status': 'completed'})

    def action_mark_cancelled(self):
        self.write({'status': 'cancelled'})