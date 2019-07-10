# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
import re
import time
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC
from odoo import api, fields, models
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools import float_compare
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _


class IFIEmployeeLeave(models.Model):
    _inherit = 'hr.leave'

    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')
    approval_user_ids = fields.Many2many('res.users', string='2nd Approval By', compute='_compute_approval_user_ids', store=True)

    @api.depends('employee_id')
    def _compute_approval_user_ids(self):
        for r in self:
            if r.employee_id:
                department_ids = r.employee_id.get_department_ids()
                if department_ids:
                    approval_ids = department_ids.mapped('leave_approval_user_ids')
                    r.approval_user_ids = approval_ids

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        super(IFIEmployeeLeave, self)._compute_can_approve()
        for holiday in self:
            if holiday.can_approve:
                continue
            if self.env.user in holiday.approval_user_ids:
                holiday.can_approve = True
            elif self.user_has_groups('ifi_employee.group_hr_department_manager') or self.user_has_groups('ifi_employee.group_hr_department_vice'):
                if self.env.user.employee_ids and self.env.user.employee_ids[0].department_id \
                        and holiday.employee_id.department_id \
                        and (self.env.user.employee_ids[0].department_id == holiday.employee_id.department_id):
                    holiday.can_approve = True

    @api.onchange('request_date_from_period', 'request_hour_from', 'request_hour_to',
                  'request_date_from', 'request_date_to',
                  'employee_id')
    def _onchange_request_parameters(self):
        if not self.request_date_from:
            self.date_from = False
            return

        if self.request_unit_half or self.request_unit_hours:
            self.request_date_to = self.request_date_from

        if not self.request_date_to:
            self.date_to = False
            return

        domain = [('calendar_id', '=',
                   self.employee_id.resource_calendar_id.id or self.env.user.company_id.resource_calendar_id.id)]
        attendances = self.env['resource.calendar.attendance'].search(domain, order='dayofweek, day_period DESC')

        # find first attendance coming after first_day
        attendance_from = next((att for att in attendances if int(att.dayofweek) >= self.request_date_from.weekday()),
                               attendances[0])
        # find last attendance coming before last_day
        attendance_to = next(
            (att for att in reversed(attendances) if int(att.dayofweek) <= self.request_date_to.weekday()),
            attendances[-1])

        if self.request_unit_half:
            if self.request_date_from_period == 'am':
                hour_from = float_to_time(attendance_from.hour_from)
                hour_to = float_to_time(attendance_from.hour_to)
            else:
                hour_from = float_to_time(attendance_to.hour_from)
                hour_to = float_to_time(attendance_to.hour_to)
        elif self.request_unit_hours:
            # This hack is related to the definition of the field, basically we convert
            # the negative integer into .5 floats
            hour_from = float_to_time(
                abs(self.request_hour_from) - 0.5 if self.request_hour_from < 0 else self.request_hour_from)
            hour_to = float_to_time(
                abs(self.request_hour_to) - 0.5 if self.request_hour_to < 0 else self.request_hour_to)
        elif self.request_unit_custom:
            hour_from = self.date_from.time()
            hour_to = self.date_to.time()
        else:
            hour_from = float_to_time(attendance_from.hour_from)
            hour_to = float_to_time(attendance_to.hour_to)

        tz = self.env.user.tz if self.env.user.tz and not self.request_unit_custom else 'UTC'
        offset = datetime.now(pytz.timezone(tz or 'UTC')).utcoffset()
        self.date_from = (datetime.combine(self.request_date_from, hour_from) + offset).replace(tzinfo=None)
        self.date_to = (datetime.combine(self.request_date_to, hour_to) + offset).replace(tzinfo=None)
        self._onchange_leave_dates()

