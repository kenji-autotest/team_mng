# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError


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

    # def _get_responsible_for_approval(self):
    #     if self.state == 'confirm' and self.manager_id.user_id:
    #         return self.manager_id.user_id
    #     elif self.state == 'confirm' and self.employee_id.parent_id.user_id:
    #         return self.employee_id.parent_id.user_id
    #     elif self.department_id.manager_id.user_id:
    #         return self.department_id.manager_id.user_id
    #     elif self.department_id.manager_id.parent_id and self.department_id.manager_id.parent_id.user_id:
    #         return self.department_id.manager_id.parent_id.user_id
    #     return self.env['res.users']


