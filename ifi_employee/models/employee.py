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


class IFIEmployee(models.Model):

    _inherit = "hr.employee"

    skype = fields.Char(string='Skype')
    job_title = fields.Char("Job Title", required=True)
    work_email = fields.Char('Work Email', required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    staff_id = fields.Char(string='Staff ID')
    department_allocation_ids = fields.One2many('hr.employee.department', 'employee_id')

    @api.multi
    def create_user(self):
        for r in self:
            user_id = self.env['res.users'].create({'name': r.name, 'login': r.work_email})
            if user_id:
                r.user_id = user_id

    @api.model
    def create(self, vals):
        res = super(IFIEmployee, self).create(vals)
        if vals.get('user_id', False) not in vals:
            res.sudo().create_user()
        return res

    @api.multi
    def write(self, vals):
        res = super(IFIEmployee, self).write(vals)
        for r in self:
            if r.department_id and r.department_id not in [i.department_id for i in r.department_allocation_ids]:
                self.env['hr.employee.department'].create({'employee_id': r.id,
                                                           'department_id': r.department_id.id,
                                                           'date_start': fields.Date.today()})
        return res


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
