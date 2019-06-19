# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval


class IFIPerformanceStrategy(models.Model):
    """ Tags of project's tasks """
    _name = "performance.strategy"
    _description = "Performance Strategy"

    name = fields.Char(required=True)
    description = fields.Text()
    user_id = fields.Many2one('res.users', string="Approved By")
    user_ids = fields.Many2many('res.users', string="Apply For")
    indicator_ids = fields.Many2many('indicator.weigh')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', readonly=True)

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
    value_guide = field.Text(string="Guide", related='indicator_id.rating_guide')
    weight = fields.Float("Weight(%)")
    note = fields.Char()


class IFIPerformanceIndicator(models.Model):
    _name = 'performance.indicator'

    indicator = fields.Char()
    value_ids = fields.One2many('indicator.value', 'indicator_id', string="Values")
    rating_guide = field.Text(string="Guide", compute='_compute_rating_guide', store=True)

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

    indicator_id = fields.Many2one('performance.indicator', string="Indicator", required=True, ondelete='cascade')
    sequence = fields.Integer(default=1, required=True)
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    description = fields.Text()
    conceptual_score = fields.Float(required=True)


class IFIEmployeePerformance(models.Model):
    _name = "employee.performance.review"
    _description = "Employee Performance Review"
    _inherit = ['portal.mixin', 'mail.alias.mixin', 'mail.thread']

    name = fields.Char(required=True)
    user_id = res.user('res.users', string="User", required=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', related='user_id.employee_id')
    user1_id = res.user('res.users', string="Reviewer ", required=True)

    job_id = fields.Many2one('ntq.employee.role', string='Role', compute='_compute_department_id', store=True,
                              track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Department', compute='_compute_department_id', store=True,
                                    track_visibility='onchange')
    appreciation = fields.Float('Appreciation', compute='compute_appreciation', store=True, group_operator="avg",
                                track_visibility='onchange')
    state = fields.Selection([('new', 'New'),
                              ('in_progress', 'In Progress'),
                              ('done', 'Done')], string="State", default='new', compute='_compute_state', store=True,
                             track_visibility='onchange')
    strategy_id = fields.Many2one('ntq.appraisal.plan', string='Plan', required=True, track_visibility='onchange')

    start_date = fields.Date(string='Start Date', track_visibility='onchange')
    end_date = fields.Date(string='End Date', track_visibility='onchange', compute='_compute_state', store=True)
    expired_date = fields.Date(string='Deadline', track_visibility='onchange')
    note = fields.Text(string="Note", track_visibility='onchange')
    suggestion_ids = fields.One2many('ntq.appraisal.suggestion.orientation', 'appraisal_id', string="Suggestion",
                                     track_visibility='onchange')
    auto_done = fields.Boolean(string='Done by system', compute='_compute_done_by_sys', store=True,
                               track_visibility='onchange')
    pm_review = fields.Boolean(string='PM Review(New)', compute='_compute_pm_review_not_done', store=True,
                               default=False, track_visibility='onchange')





