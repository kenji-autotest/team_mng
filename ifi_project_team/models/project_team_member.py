# See LICENSE file for full copyright and licensing details.

import datetime
from odoo import api, fields, models


class IFIProjectProject(models.Model):
    _inherit = 'project.project'

    member_ids = fields.One2many('project.member', 'project_id')


class IFIProjectTeamMember(models.Model):
    _name = 'project.member'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', required=True)
    job_id = fields.Many2one('hr.job', required=True, string='Position')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True)
    user_id = fields.Many2one('res.users', related='employee_id.user_id', store=True)
    project_id = fields.Many2one('project.project', required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date()
    allocation = fields.Integer(default=100, required=True)
    timesheet_ids = fields.One2many('account.analytic.line', 'project_member_id')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id and self.employee_id.job_id:
            self.job_id = self.employee_id.job_id

    @api.model
    def generate_timesheet(self, date_from, date_to):
        res = []
        members = self.search([('date_from', '<=', date_to),
                               ('project_id.allow_timesheets', '=', True),
                               '|', ('date_to', '=', False),
                               ('date_to', '>=', date_from)])
        if not members:
            return False
        timesheet = self.env['account.analytic.line'].sudo()
        timesheet_ids = timesheet.search([('project_member_id', '!=', False),
                                          ('date', '<=', date_to),
                                          ('date', '>=', date_from)])
        if timesheet_ids:
            timesheet_ids.unlink()
        delta = date_to - date_from
        for d in range(delta.days + 1):
            date = date_from + datetime.timedelta(days=d)
            members = members.filtered(lambda x: x.date_from <= date and (not x.date_to or x.date_to >= date))
            for r in members:
                vals = {'project_id': r.project_id.id,
                        'employee_id': r.employee_id.id,
                        'date': date,
                        'name': r.project_id.name + ': ' + 'default timesheet',
                        'unit_amount': r.allocation * 8/100,
                        'project_member_id': r.id}
                timesheet_id = timesheet.create(vals)
                if timesheet_id:
                    res.append(timesheet_id.id)
        return res


class IFIAccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    project_member_id = fields.Many2one('project.member')

