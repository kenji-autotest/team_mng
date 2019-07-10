# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models,_
from odoo.exceptions import UserError, AccessError, ValidationError


class GenerateAppraisals(models.TransientModel):
    _name = 'project.timesheet.batches'
    _description = 'Generate Project Timesheets Batches'

    def _default_start_date(self):
        return fields.Date.today().replace(day=1)

    date_from = fields.Date(required=True, default=_default_start_date)
    date_to = fields.Date(required=True, default=fields.Date.today())

    @api.multi
    @api.constrains('expired_date', 'review_expired_date', 'date')
    def _check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('Date To must greater than Date From'))

    @api.multi
    def action_generate_timesheet(self):
        date_from = fields.Date.from_string(self.date_from)
        date_to = fields.Date.from_string(self.date_to)
        res = self.env['project.member'].generate_timesheet(date_from, date_to)
        if not res:
            return False
        kanban_view = self.env.ref('hr_timesheet.view_kanban_account_analytic_line')
        tree_view = self.env.ref('hr_timesheet.hr_timesheet_line_tree')
        return {
            'name': _('Timesheets'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.analytic.line',
            'domain': [('id', 'in', res)],
            'views': [
                (tree_view.id, 'tree'),
                (kanban_view.id, 'kanban'),
            ],
            'type': 'ir.actions.act_window',
        }
