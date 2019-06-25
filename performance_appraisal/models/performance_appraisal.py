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
    _inherit = ['mail.thread', 'mail.activity.mixin']

    indicator_id = fields.Many2one('performance.indicator', string="Indicator", ondelete='restrict')
    strategy_id = fields.Many2one('performance.strategy', string='Appraisal Strategy')
    weight = fields.Float("Weight(%)")
    note = fields.Char()
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)


class IFIPerformanceIndicator(models.Model):
    _name = 'performance.indicator'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char()
    description = fields.Text()
    value_ids = fields.Many2many('indicator.value', 'performance_indicator_value_rel', 'indicator_id', 'value_id',
                                 string="Values")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)


class IFIPerformanceIndicatorValues(models.Model):
    _name = 'indicator.value'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department_id', store=True,
                                    track_visibility='onchange')
    job_title = fields.Char("Job Title", compute='_compute_department_id', store=True, track_visibility='onchange')
    reviewer_id = fields.Many2one('hr.employee', string='Reviewer', required=True)
    date = fields.Date(string='Appraisal Date', track_visibility='onchange', required=True)
    start_date = fields.Date(string='Start Date', track_visibility='onchange')
    expired_date = fields.Date(string='Deadline', track_visibility='onchange', required=True)
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
    private_access = fields.Boolean(compute='compute_private_access')

    @api.depends('general', 'improvement_points', 'score_compute')
    def _compute_summary(self):
        for r in self:
            summary = ''
            if r.general:
                summary += 'General: ' + r.general + '\n'
            if r.improvement_points:
                summary += 'Improvement points: ' + r.improvement_points + '\n'
            if r.next_objectives:
                summary += 'Orientation: ' + r.next_objectives
            r.summary = summary

    def compute_private_access(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_manager = self.env.user.has_group('performance_appraisal.group_performance_appraisal_manager')
        is_readall = self.env.user.has_group('performance_appraisal.group_performance_appraisal_readall')
        is_dm = self.env.user.has_group('ifi_employee.group_hr_department_manager')
        is_vice_dm = self.env.user.has_group('ifi_employee.group_hr_department_vice')
        for r in self:
            private_access = False
            if is_manager or is_readall:
                private_access = True
            elif is_dm or is_vice_dm:
                if current_employee.department_id == r.department_id:
                    private_access = True
            r.private_access = private_access

    @api.depends('employee_id')
    def _compute_department_id(self):
        for r in self:
            if r.employee_id:
                r.department_id = r.employee_id.department_id or False
                r.job_title = r.employee_id.job_title or False

    @api.depends('auto_score', 'score_tmp', 'appraisal_details_ids.score',)
    def compute_score(self):
        for r in self:
            if r.auto_score:
                r.score_compute = sum([i.score for i in r.appraisal_details_ids if i.score])
            else:
                r.score_compute = r.score_tmp

    @api.model
    def create(self, vals):
        res = super(IFIEmployeePerformance, self).create(vals)
        if not vals.get('appraisal_details_ids', False):
            for r in res.strategy_id.indicator_ids:
                self.env['employee.performance.appraisal.details'].create({'appraisal_id': res.id,
                                                                           'employee_id': res.employee_id.id,
                                                                           'department_id': res.department_id.id,
                                                                           'job_title': res.job_title,
                                                                           'reviewer_id': res.reviewer_id.id,
                                                                           'date': res.date,
                                                                           'strategy_id': res.strategy_id.id,
                                                                           'indicator_id': r.indicator_id.id})
        return res


class IFIEmployeePerformanceDetails(models.Model):
    _name = "employee.performance.appraisal.details"
    _description = "Employee Performance Appraisal"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    appraisal_id = fields.Many2one('employee.performance.appraisal', string='Appraisal', required=True,
                                   track_visibility='onchange', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='Employee', related='appraisal_id.employee_id',
                                  track_visibility='onchange', store=True)
    department_id = fields.Many2one('hr.department', string='Department', related='appraisal_id.department_id',
                                    store=True, track_visibility='onchange')
    job_title = fields.Char("Job Title", related='appraisal_id.job_title', store=True, track_visibility='onchange')
    reviewer_id = fields.Many2one('hr.employee', string='Manager', related='appraisal_id.reviewer_id', store=True)
    date = fields.Date(string='Appraisal Date', track_visibility='onchange')
    strategy_id = fields.Many2one('performance.strategy', string='Appraisal Strategy', related='appraisal_id.strategy_id', store=True)
    indicator_id = fields.Many2one('performance.indicator')
    rating_guide = fields.Text(string="Description", related='indicator_id.description', store=True)
    value_id = fields.Many2one('indicator.value', string="Score")
    conceptual_score = fields.Float(related='value_id.conceptual_score', store=True, string='Rate')
    weight = fields.Float(compute='_compute_weight', store=True)
    score = fields.Float(compute='_compute_score', store=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)

    @api.depends('strategy_id', 'indicator_id', 'strategy_id.indicator_ids', 'strategy_id.indicator_ids.weight')
    def _compute_weight(self):
        indicator_weight = self.env['indicator.weigh']
        for r in self:
            if r.strategy_id and r.indicator_id:
                indicator_id = indicator_weight.search([('strategy_id', '=', r.strategy_id.id),
                                                       ('indicator_id', '=', r.indicator_id.id)])
                if indicator_id:
                    r.weight = indicator_id.weight

    @api.depends('weight', 'value_id')
    def _compute_score(self):
        for r in self:
            if r.weight and r.value_id:
                r.score = r.weight * r.value_id.conceptual_score / 100

    @api.onchange('indicator_id')
    def onchange_indicator_id(self):
        if not self.indicator_id:
            return {}
        return {'domain': {'value_id': [
            ('id', 'in', self.indicator_id.value_ids.ids)
        ]}}








