# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval


class IFIEmployeeAppraisalSummary(models.Model):
    _name = "employee.appraisal.summary"
    _description = "Employee Performance Appraisal Summary"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department_id', store=True,
                                    track_visibility='onchange')
    job_title = fields.Char("Job Title", compute='_compute_department_id', store=True, track_visibility='onchange')
    manager_id = fields.Many2one('hr.employee', string='Manager', required=True, compute='_compute_department_id')
    date = fields.Date(string='Appraisal Date', track_visibility='onchange', required=True)
    expired_date = fields.Date(string='Deadline', track_visibility='onchange', required=True)
    review_expired_date = fields.Date(string='Peer Review Deadline', track_visibility='onchange', required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('submitted', 'Submitted')
                              ], string="State", default='draft', track_visibility='onchange')
    strategy_id = fields.Many2one('performance.strategy', string='Appraisal Strategy', required=True)
    recommended_score = fields.Float(compute='_compute_recommended_score', string='Avg score', store=True,
                                       track_visibility='onchange', group_operator="avg")
    general = fields.Text(track_visibility='onchange')
    improvement_points = fields.Text(track_visibility='onchange')
    next_objectives = fields.Text(track_visibility='onchange')
    score = fields.Float(string='Score', track_visibility='onchange', group_operator="avg")
    private_note = fields.Text(string="Private Note")
    private_note_reviews = fields.Text(compute='_compute_recommended_score', track_visibility='onchange', store=True)
    summary = fields.Text(compute='_compute_summary', store=True, track_visibility='onchange')
    appraisal_ids = fields.One2many('employee.performance.appraisal', 'appraisal_summary_id',
                                    string="Appraisals", track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)
    private_access = fields.Boolean(compute='compute_private_access')

    _sql_constraints = [
        ('key_uniq', 'unique (employee_id, strategy_id, date)', 'Appraisal be unique.')
    ]

    @api.depends('general', 'improvement_points', 'score')
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
            elif current_employee == r.manager_id or current_employee == r.employee_id.parent_id:
                private_access = True
            r.private_access = private_access

    @api.depends('employee_id')
    def _compute_department_id(self):
        for r in self:
            if r.employee_id:
                r.update({'department_id': r.employee_id.department_id or False,
                          'job_title': r.employee_id.job_title or False,
                          'manager_id': r.employee_id.parent_id and r.employee_id.parent_id.id or False})

    @api.depends('appraisal_ids.score','appraisal_ids.private_note')
    def _compute_recommended_score(self):
        for r in self:
            private_note_reviews = ''
            score = 0
            for i in r.appraisal_ids:
                score += i.score if i.score else score
                private_note_reviews += i.private_note if i.private_note else ''
            r.recommended_score = score / len(r.appraisal_ids) if r.appraisal_ids else score
            r.private_note_reviews = private_note_reviews

    @api.one
    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    @api.one
    def action_submit(self):
        self.write({'state': 'submitted'})

    @api.model
    def create(self, vals):
        res = super(IFIEmployeeAppraisalSummary, self).create(vals)
        if not vals.get('appraisal_ids', False):
            reviewer_setting_ids = self.env['employee.performance.reviewer'].search([('employee_id', '=', res.employee_id.id),
                                                                                     ('strategy_id', '=', res.strategy_id.id),])
            reviewer_ids = reviewer_setting_ids.mapped('reviewer_ids')
            for r in reviewer_ids:
                self.env['employee.performance.appraisal'].create({'appraisal_summary_id': res.id,
                                                                   'employee_id': res.employee_id.id,
                                                                   'department_id': res.department_id.id,
                                                                   'job_title': res.job_title,
                                                                   'reviewer_id': r.id,
                                                                   'date': res.date,
                                                                   'expired_date': res.review_expired_date,
                                                                   'strategy_id': res.strategy_id.id})
        return res


class IFIEmployeePerformance(models.Model):
    _name = "employee.performance.appraisal"
    _description = "Employee Performance Appraisal"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'employee_id'

    appraisal_summary_id = fields.Many2one('employee.appraisal.summary', string='Appraisal',
                                           track_visibility='onchange', ondelete='restrict')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department_id', store=True,
                                    track_visibility='onchange')
    job_title = fields.Char("Job Title", compute='_compute_department_id', store=True, track_visibility='onchange')
    reviewer_id = fields.Many2one('hr.employee', string='Reviewer', required=True)
    date = fields.Date(string='Appraisal Date', track_visibility='onchange', required=True)
    start_date = fields.Date(string='Start Date', track_visibility='onchange')
    expired_date = fields.Date(string='Deadline', track_visibility='onchange', required=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('submitted', 'Submitted')
                              ], string="State", default='draft', track_visibility='onchange')
    strategy_id = fields.Many2one('performance.strategy', string='Appraisal Strategy', required=True)
    auto_score = fields.Boolean(related='strategy_id.auto_score', store=True)
    general = fields.Text(track_visibility='onchange')
    score = fields.Float(string='Score', compute='compute_score', store=True, group_operator="avg",
                         track_visibility='onchange')
    score_tmp = fields.Float(string='Score(manual)', track_visibility='onchange', group_operator="avg")
    private_note = fields.Text(string="Private Note")
    appraisal_details_ids = fields.One2many('employee.performance.appraisal.details', 'appraisal_id',
                                            string="Appraisal Details", track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    active = fields.Boolean(default=True)
    private_access = fields.Boolean(compute='compute_private_access')

    _sql_constraints = [
        ('key_uniq', 'unique (employee_id, strategy_id, reviewer_id, date)', 'Appraisal be unique.')
    ]

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
            elif current_employee == r.reviewer_id or current_employee == r.employee_id.parent_id:
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
                r.score = sum([i.score for i in r.appraisal_details_ids if i.score])
            else:
                r.score = r.score_tmp

    @api.one
    def action_set_to_draft(self):
        self.write({'state': 'draft'})

    @api.one
    def action_submit(self):
        self.write({'state': 'submitted'})

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
    _rec_name = 'employee_id'

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
    value_id = fields.Many2one('indicator.value', string="Rate")
    conceptual_score = fields.Float(related='value_id.conceptual_score', store=True, string='Rate', group_operator="avg")
    weight = fields.Float(compute='_compute_weight', store=True, group_operator="max")
    score = fields.Float(compute='_compute_score', store=True, group_operator="avg")
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

    # @api.onchange('indicator_id')
    # def onchange_indicator_id(self):
    #     if not self.indicator_id:
    #         return {}
    #     return {'domain': {'value_id': [
    #         ('id', 'in', self.indicator_id.value_ids.ids)
    #     ]}}








