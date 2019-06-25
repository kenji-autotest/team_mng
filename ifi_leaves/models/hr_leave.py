# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, _
from odoo.exceptions import UserError


# class IFIEmployee(models.Model):
#
#     _inherit = "hr.employee"
#
#     manager_ids = fields.Many2many('hr.employee', string='Other Managers')


class IFIEmployeeLeave(models.Model):
    _inherit = 'hr.leave'

    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')

    @api.depends('state', 'employee_id', 'department_id')
    def _compute_can_approve(self):
        super(IFIEmployeeLeave, self)._compute_can_approve()
        for holiday in self:
            if holiday.can_approve:
                continue
            if self.user_has_groups('ifi_employee.group_hr_department_manager', 'ifi_employee.group_hr_department_vice'):
                if self.user.employee_ids and self.user.employee_ids[0].department_id \
                        and holiday.employee_id.department_id \
                        and self.user.employee_ids[0].department_id == holiday.employee_id.department_id:
                    holiday.can_approve = True

    # @api.multi
    # def add_follower(self, employee_id):
    #     super(IFIEmployeeLeave, self).add_follower(employee_id)
    #     partner_ids = []
    #     for i in employee_id.manager_ids:
    #         if i.user_id:
    #             partner_ids.append(i.user_id.partner_id.id)
    #     if partner_ids:
    #         self.message_subscribe(partner_ids=partner_ids)


