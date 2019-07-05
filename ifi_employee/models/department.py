# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2017-today Ascetic Business Solution <www.asceticbs.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

from odoo import api, fields, models, _


class IFIDepartment(models.Model):
    _name = "hr.employee.department"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    employee_id = fields.Many2one('hr.employee', required=True)
    department_id = fields.Many2one('hr.department', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date')
    allocation = fields.Float(default=100)
    note = fields.Char()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)


class IFIEmployeeInherit(models.Model):

    _inherit = "hr.employee"

    department_allocation_ids = fields.One2many('hr.employee.department', 'employee_id')
    department_ids = fields.Many2many('hr.department', compute='_compute_department_ids', store=True)

    @api.multi
    @api.depends('department_allocation_ids')
    def _compute_department_ids(self):
        for r in self:
            r.department_ids = r.department_allocation_ids.mapped('department_id')

    @api.multi
    def write(self, vals):
        res = super(IFIEmployeeInherit, self).write(vals)
        for r in self:
            if r.department_id and r.department_id not in [i.department_id for i in r.department_allocation_ids]:
                self.env['hr.employee.department'].create({'employee_id': r.id,
                                                           'department_id': r.department_id.id,
                                                           'date_start': fields.Date.today()})
        return res


class IFIDepartmentInherit(models.Model):
    _inherit = "hr.department"

    employee_all_ids = fields.Many2many('hr.employee', compute='_compute_employee_all_ids')

    @api.one
    def _compute_employee_all_ids(self):
        self.employee_all_ids = self.get_employees_by_department(self.id)

    @api.returns('self')
    def get_employees_by_department(self, department_id, date=fields.Date.today()):
        employees_allocation = self.env['hr.employee.department'].search([('department_id', 'child_of', [department_id]),
                                                                          ('date_start', '<=', date),
                                                                          '|', ('date_end', '>', date),
                                                                          ('date_end', '=', False)])
        employees = self.env['hr.employee'].search([('department_id', 'child_of', [department_id])])
        employee_ids = employees_allocation.mapped('employee_id') + employees
        employee_ids = list(set(employee_ids.ids))
        return self.env['hr.employee'].browse(employee_ids)
