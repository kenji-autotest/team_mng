# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import pytz
import re
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class IFIAttendance(models.Model):

    _inherit = "hr.attendance"

    @api.model
    def daily_auto_checkin(self):
        today = pytz.UTC.localize(datetime.utcnow())
        today_start = today.replace(hour=0, minute=0, second=0)
        today_end = today.replace(hour=23, minute=59, second=59)
        dow = today_start.weekday()
        calendar_ids = self.env['resource.calendar.attendance'].search([('dayofweek', '=', dow)])

        manual_checkin = self.search([('check_in', '<=', today_end),
                                      ('check_out', '>=', today_start)]).mapped('employee_id')
        employees = self.env['hr.employee'].sudo().search([('id', '!=', 1)])
        today_leaves = self.env['hr.leave'].sudo().search([('request_date_from', '<', today_end),
                                                           ('request_date_to', '>', today_start),
                                                           ('state', 'not in', ['cancel', 'refuse'])])
        attendance = employees - today_leaves.mapped('employee_id') - manual_checkin
        for leave in today_leaves:
            employee_today_start = today_start
            if leave.employee_id in manual_checkin:
                continue
            calendar_id = leave.employee_id.resource_calendar_id
            offset = datetime.now(pytz.timezone(calendar_id.tz or 'UTC')).utcoffset()
            if offset:
                employee_today_start = today_start + offset
            if leave.request_unit_half:
                working_shift = calendar_ids.filtered(lambda x: x.calendar_id == calendar_id and x.day_period != leave.request_unit_half).sorted(key='hour_from')
                if working_shift:
                    checkin = working_shift[0].hour_from
                    checkout = working_shift[0].hour_to
                    if checkin:
                        self.create({'employee_id': leave.employee_id.id,
                                     'check_in': employee_today_start + relativedelta(hours=checkin),
                                     'check_out': employee_today_start + relativedelta(hours=checkout)
                                     })
        for r in attendance:
            calendar_id = r.resource_calendar_id
            offset = datetime.now(pytz.timezone(calendar_id.tz or 'UTC')).utcoffset()
            employee_today_start = today_start
            if offset:
                employee_today_start = today_start + offset
            working_shift = calendar_ids.filtered(lambda x: x.calendar_id == calendar_id).sorted(key='hour_from')
            if working_shift:
                checkin = employee_today_start + relativedelta(hours=working_shift[0].hour_from)
                checkout = employee_today_start + relativedelta(hours=working_shift[len(working_shift) - 1].hour_to)
                if checkin:
                    self.create({'employee_id': r.id,
                                 'check_in': checkin,
                                 'check_out': checkout,
                                 })

        return True

