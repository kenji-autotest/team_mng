# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IFIDepartmentLeave(models.Model):

    _inherit = 'hr.department'

    absence_of_today = fields.Integer(
        compute='_compute_leave_count', string='Absence by Today')
    leave_to_approve_count = fields.Integer(
        compute='_compute_leave_count', string='Leave to Approve')
    allocation_to_approve_count = fields.Integer(
        compute='_compute_leave_count', string='Allocation to Approve')
    total_employee = fields.Integer(
        compute='_compute_total_employee', string='Total Employee')

    @api.multi
    def _compute_leave_count(self):
        Requests = self.env['hr.leave']
        Allocations = self.env['hr.leave.allocation']
        today_date = datetime.datetime.utcnow().date()
        today_start = fields.Datetime.to_string(today_date)  # get the midnight of the current utc day
        today_end = fields.Datetime.to_string(today_date + relativedelta(hours=23, minutes=59, seconds=59))
        for department in self:

            leave_count = Requests.search_count([('employee_id.department_ids', 'in', [department.id]),
                                                 ('state', '=', 'confirm')])
            allocation_count = Allocations.search([('employee_id.department_ids', 'in', [department.id]),
                                                   ('state', '=', 'confirm')])
            absence_count = Requests.seach([('employee_id.department_ids', 'in', [department.id]),
                                            ('state', 'not in', ['cancel', 'refuse']),
                                            ('date_from', '<=', today_end),
                                            ('date_to', '>=', today_start)])

            department.leave_to_approve_count = leave_count
            department.allocation_to_approve_count = allocation_count
            department.absence_of_today = absence_count

    @api.multi
    def _compute_total_employee(self):
        for department in self:
            department.total_employee = len(department.get_department_employees())


