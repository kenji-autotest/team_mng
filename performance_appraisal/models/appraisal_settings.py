# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval


class IFIPerformanceStrategy(models.Model):
    _name = "performance.strategy"
    _description = "Performance Strategy"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    description = fields.Text()
    approval_id = fields.Many2one('hr.employee', string="Approved By")
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_performance_strategy_rel', 'strategy_id',
                                    'employee_id', string="Apply For")
    indicator_ids = fields.One2many('indicator.weigh', 'strategy_id')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', readonly=True)
    auto_score = fields.Boolean(string='Auto score?', default=True)
    active = fields.Boolean(default=True)
    interval = fields.Selection([
        ('month', 'Monthly'),
        ('semi-annual', 'Semi-Annual'),
        ('annual', 'Annual'),
    ], string='Interval', default="month")
    date = fields.Date(string='Effective Date')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Strategy already exists!"),
    ]

    @api.one
    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    @api.one
    def action_submit(self):
        self.write({'state': 'submitted'})

    @api.one
    def action_approve(self):
        self.write({'state': 'draft'})

    @api.one
    def action_reject(self):
        self.write({'state': 'rejected'})


class IFIIndicatorWeighing(models.Model):
    _name = 'indicator.weigh'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    indicator_id = fields.Many2one('performance.indicator', string="Indicator", ondelete='restrict')
    strategy_id = fields.Many2one('performance.strategy', string='Appraisal Strategy')
    weight = fields.Float("Weight(%)", default=100)
    note = fields.Char()
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)


class IFIIndicatorCategory(models.Model):
    _name = 'performance.indicator.category'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    description = fields.Text()
    indicator_ids = fields.One2many('performance.indicator', 'category_id', string='Indicator')
    active = fields.Boolean(default=True)


class IFIPerformanceIndicator(models.Model):
    _name = 'performance.indicator'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    description = fields.Text()
    value_ids = fields.One2many('indicator.value', 'indicator_id', string="Rates")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    category_id = fields.Many2one('performance.indicator.category', string='Category')
    active = fields.Boolean(default=True)


class IFIPerformanceIndicatorValues(models.Model):
    _name = 'indicator.value'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'

    indicator_id = fields.Many2one('performance.indicator', string="Indicator")
    sequence = fields.Integer(default=1, required=True)
    name = fields.Char(required=True)
    description = fields.Text()
    conceptual_score = fields.Float(required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)







