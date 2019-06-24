# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval


class IFIPerformanceStrategy(models.Model):
    _name = "performance.strategy"
    _description = "Performance Strategy"

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    description = fields.Text()
    approval_id = fields.Many2one('hr.employee', string="Approved By")
    employee_ids = fields.Many2many('hr.employee', 'hr_employee_performance_strategy_rel', 'strategy_id',
                                    'employee_id', string="Apply For")
    indicator_ids = fields.Many2many('indicator.weigh')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', readonly=True)
    auto_score = fields.Boolean(string='Auto score?', default=True)
    active = fields.Boolean(default=True)

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
    def action_rejected(self):
        self.write({'state': 'rejected'})


class IFIIndicatorWeighing(models.Model):
    _name = 'indicator.weigh'

    indicator_id = fields.Many2one('performance.indicator', string="Indicator", ondelete='restrict')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    value_guide = field.Text(string="Guide", related='indicator_id.rating_guide')
    value_ids = fields.One2many('indicator.value', 'indicator_id', string="Values")
    weight = fields.Float("Weight(%)")
    note = fields.Char()
    active = fields.Boolean(default=True)


class IFIPerformanceIndicator(models.Model):
    _name = 'performance.indicator'

    indicator = fields.Char()
    value_ids = fields.Many2many('indicator.value', 'performance_indicator_value_rel', 'indicator_id', 'value_id',
                                 string="Values", default=lambda self: self.env['indicator.value'].search([]))
    rating_guide = field.Text(string="Guide", compute='_compute_rating_guide', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    @api.depends('value_ids')
    def _compute_rating_guide(self):
        for r in self:
            text = ''
            for i in r.value_ids:
                text += '- ' + i.code + ' | ' + i.name + ': ' + i.description + '\n'
            r.rating_guide = text


class IFIPerformanceIndicatorValues(models.Model):
    _name = 'indicator.value'
    _order = 'sequence'

    indicator_id = fields.Many2many('performance.indicator', 'performance_indicator_value_rel', 'value_id', 'indicator_id',
                                    string="Indicator")
    sequence = fields.Integer(default=1, required=True)
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    description = fields.Text()
    conceptual_score = fields.Float(required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)


class IFIEmployeePerformance(models.Model):
    _name = "employee.performance.appraisal"
    _description = "Employee Performance Appraisal"
    _inherit = ['portal.mixin', 'mail.alias.mixin', 'mail.thread']

    name = fields.Char(required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department_id', store=True,
                                    track_visibility='onchange')
    job_title = fields.Char("Job Title", compute='_compute_department_id', store=True, track_visibility='onchange')
    reviewer_id = fields.Many2one('hr.employee', string='Reviewer', required=True)
    date = fields.Date(string='Appraisal Date', track_visibility='onchange')
    start_date = fields.Date(string='Start Date', track_visibility='onchange')
    expired_date = fields.Date(string='Deadline', track_visibility='onchange')
    state = fields.Selection([('new', 'New'),
                              ('in_progress', 'In Progress'),
                              ('done', 'Done')], string="State", default='new', compute='_compute_state', store=True,
                             track_visibility='onchange')
    strategy_id = fields.Many2one('performance.strategy', string='Appraisal Strategy', required=True)
    auto_score = fields.Boolean(related='strategy_id.auto_score', store=True)
    general = fields.Text(track_visibility='onchange')
    improvement_points = fields.Text(track_visibility='onchange')
    next_objectives = fields.Text(track_visibility='onchange')
    score_compute = fields.Float(string='Score', compute='compute_score', store=True, group_operator="avg",
                                 track_visibility='onchange')
    score_tmp = fields.Float(string='Score(manual)', track_visibility='onchange')
    private_note = fields.Text(string="Private Note")
    summary = fields.Text(compute='_compute_summary', store=True, track_visibility='onchange')
    appraisal_details_ids = fields.One2many('employee.performance.appraisal.details', 'appraisal_id',
                                            string="Appraisal Details", track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    @api.depends('employee_id')
    def _compute_department_id(self):
        for r in self:
            if r.employee_id:
                r.department_id = r.employee_id.department_id or False
                r.job_title = r.employee_id.job_title or False

    @api.depends('auto_score', 'score_tmp', 'appraisal_details_ids.value_id')
    def compute_score(self):
        for r in self:
            if r.auto_score:
                r.score_compute = sum([i.value_id.conceptual_score * i.weigh for i in r.appraisal_details_ids if i.value_id])
            else:
                r.score_compute = r.score_tmp


class IFIEmployeePerformanceDetails(models.Model):
    _name = "employee.performance.appraisal.details"
    _description = "Employee Performance Appraisal"
    _inherit = ['portal.mixin', 'mail.alias.mixin', 'mail.thread']

    appraisal_id = fields.Many2one('employee.performance.appraisal', string='Appraisal', required=True,
                                   track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', string='Employee', related='appraisal_id.employee_id', required=True,
                                  track_visibility='onchange', store=True)
    department_id = fields.Many2one('hr.department', string='Department', related='appraisal_id.department_id',
                                    store=True,
                                    track_visibility='onchange')
    job_title = fields.Char("Job Title", related='appraisal_id.job_title', store=True, track_visibility='onchange')
    reviewer_id = fields.Many2one('hr.employee', string='Manager', required=True)
    date = fields.Date(string='Appraisal Date', track_visibility='onchange')
    strategy_id = fields.Many2one('performance.strategy', string='Appraisal Strategy', required=True)
    indicator_id = fields.Many2one('indicator.weigh')
    value_id = fields.Many2one('indicator.value', string="Score")
    weigh = fields.Float(related='indicator_id.weight', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)









