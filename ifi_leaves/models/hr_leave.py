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

    def _check_approval_update(self, state):
        """ Check if target state is achievable. """
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        is_officer = self.env.user.has_group('hr_holidays.group_hr_holidays_user')
        is_manager = self.env.user.has_group('hr_holidays.group_hr_holidays_manager')
        for holiday in self:
            manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
            val_type = holiday.holiday_status_id.validation_type
            if state == 'confirm':
                continue

            if state == 'draft':
                if holiday.employee_id != current_employee and not is_manager:
                    raise UserError(_('Only a Leave Manager can reset other people leaves.'))
                continue

            if not is_officer and (not manager or manager != current_employee):
                raise UserError(_('Only a Leave Officer or Manager can approve or refuse leave requests.'))

            if is_officer:
                # use ir.rule based first access check: department, members, ... (see security.xml)
                holiday.check_access_rule('write')

            if holiday.employee_id == current_employee and not is_manager:
                raise UserError(_('Only a Leave Manager can approve its own requests.'))

            if (state == 'validate1' and val_type == 'both') or (state == 'validate' and val_type == 'manager'):
                # manager = holiday.employee_id.parent_id or holiday.employee_id.department_id.manager_id
                if (manager and manager != current_employee) and not self.env.user.has_group(
                        'hr_holidays.group_hr_holidays_manager'):
                    raise UserError(_('You must be either %s\'s manager or Leave manager to approve this leave') % (
                        holiday.employee_id.name))

            if state == 'validate' and val_type == 'both':
                if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                    raise UserError(_('Only an Leave Manager can apply the second approval on leave requests.'))

    def _get_number_of_days(self, date_from, date_to, employee_id):
        res = super(IFIEmployeeLeave, self)._get_number_of_days(date_from, date_to, employee_id)
        """ Returns a float equals to the timedelta between two dates given as string."""
        if self.request_unit_half:
            return 0.5
        return res

