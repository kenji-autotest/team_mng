# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class IFIDepartmentLeave(models.Model):

    _inherit = 'hr.department'

    leave_approval_user_ids = fields.Many2many('res.users', string='Leave 2nd Approval', default=lambda self: self.env.user.employee_ids[0].department_id.manager_id.user_id)
    total_employee = fields.Integer(compute='_compute_total_employee', string='Total Employee')

    @api.multi
    def _compute_total_employee(self):
        for department in self:
            department.total_employee = len(department.get_department_employees())


