# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError, AccessError, ValidationError


class GenerateAppraisals(models.TransientModel):
    _name = 'appraisal.batches'
    _description = 'Generate Appraisal Batches'

    strategy_id = fields.Many2one('performance.strategy', 'Strategy', required=True)
    interval = fields.Selection([
        ('month', 'Monthly'),
        ('semi-annual', 'Semi-Annual'),
        ('annual', 'Annual'),
    ], string='Interval', related="strategy_id.interval")
    month = fields.Selection([('01', 'January'), ('02', 'February'), ('03', 'March'), ('04', 'April'),
                              ('05', 'May'), ('06', 'June'), ('07', 'July'), ('08', 'August'), ('09', 'September'),
                              ('10', 'October'), ('11', 'November'), ('12', 'December')])
    term = fields.Selection([('01', '1H'), ('02', '2H')])
    year = fields.Char(size=4, required=True, default=fields.Date.from_string(fields.Date.today()).strftime('%Y'))
    date = fields.Date(compute='_compute_date')
    expired_date = fields.Date(required=True)
    review_expired_date = fields.Date(required=True)

    @api.multi
    @api.constrains('expired_date', 'review_expired_date', 'date')
    def _check_currency(self):
        if not self.year.isdigit():
            raise ValidationError(_('Year must be 4 digits number'))
        if self.date and self.expired_date and self.expired_date < self.date:
            raise ValidationError(_('Deadline must be greater than Appraisal Date'))
        if self.review_expired_date and self.expired_date and self.expired_date < self.review_expired_date:
            raise ValidationError(_('Review date must be earlier than Deadline'))

    @api.onchange('strategy_id')
    def _onchange_strategy_id(self):
        if self.strategy_id:
           self.interval = self.strategy_id.interval

    @api.onchange('year', 'term', 'month')
    def _onchange_date(self):
        if self.year and ((self.interval == 'month' and self.month) or (self.interval == 'semi-annual' and self.term) or self.interval == 'annual'):
            self._compute_date()
            self.expired_date = fields.Date.from_string(self.date) + relativedelta(days=7)
            self.review_expired_date = fields.Date.from_string(self.date) + relativedelta(days=3)

    @api.depends('strategy_id', 'interval', 'month', 'term', 'year')
    def _compute_date(self):
        today = fields.Date.from_string(fields.Date.context_today(self))
        if self.strategy_id.interval == 'month':
            if self.month and self.year:
                month = today.replace(month=int(self.month), year=int(self.year))
                date = str(month + relativedelta(months=+1, day=1, days=-1))[:10]
        elif self.strategy_id.interval == 'annual':
            if self.year:
                date = today.replace(month=12, year=int(self.year), day=31)
        elif self.strategy_id.interval == 'semi-annual':
            if self.year and self.term:
                if self.term == '01':
                    date = today.replace(month=6, year=int(self.year), day=30)
                elif self.term == '02':
                    date = today.replace(month=12, year=int(self.year), day=31)
        self.date = date

    @api.multi
    def action_generate_appraisal(self):
        appraisal_ids = []
        employee_ids = self.env['employee.performance.reviewer'].search([('strategy_id', '=', self.strategy_id.id)]).mapped('employee_id')
        existing_appraisals = self.env['employee.appraisal.summary'].search([('employee_id', 'in', employee_ids.ids),
                                                                             ('strategy_id', '=', self.strategy_id.id),
                                                                             ('date', '=', self.date)]).mapped('employee_id')
        employee_ids -= existing_appraisals
        if not employee_ids:
            raise ValidationError(_('There is no employee setting for this Strategy or the appraisals have been generated before!'))
        for r in employee_ids:
            res = self.env['employee.appraisal.summary'].create({'employee_id': r.id,
                                                                 'date': self.date,
                                                                 'expired_date': self.expired_date,
                                                                 'review_expired_date': self.review_expired_date,
                                                                 'strategy_id': self.strategy_id.id})
            if res:
                appraisal_ids.append(res.id)
        return self.redirect_appraisal_view(appraisal_ids)

    @api.multi
    def redirect_appraisal_view(self, appraisal_ids):
        form_view = self.env.ref('performance_appraisal.view_performance_appraisal_summary_form')
        tree_view = self.env.ref('performance_appraisal.view_performance_appraisal_summary_list')
        return {
            'name': _('Appraisals'),
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'employee.appraisal.summary',
            'domain': [('id', 'in', appraisal_ids)],
            'views': [
                (tree_view.id, 'tree'),
                (form_view.id, 'form'),
            ],
            'type': 'ir.actions.act_window',
        }
