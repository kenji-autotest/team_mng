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
    work_email = fields.Char('Work Email')
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    staff_id = fields.Char(string='Staff ID')
    state = fields.Selection([('working', 'Working'),
                              ('resigning', 'Resigning'),
                              ('terminated', 'Terminated'),
                              ('permanent', 'Permanent'),
                              ], string="State", default='working', track_visibility='onchange')
    employment_status = fields.Selection([('internship', 'Internship'),
                                          ('probation', 'Probation'),
                                          ('permanent', 'Permanent')
                                          ], default='permanent', track_visibility='onchange')

    @api.model
    def create(self, vals):
        res = super(IFIEmployee, self).create(vals)
        if not vals.get('user_id', False):
            # user_id = self.env['res.users'].create({'name': res.name, 'login': res.work_email})
            user_id = self.with_context(default_customer=False).env['res.users'].create({'name': res.name, 'login': res.work_email})
            if user_id:
                res.user_id = user_id
                res.work_email = user_id.login
                user_id.partner_id.email = user_id.login
        return res



