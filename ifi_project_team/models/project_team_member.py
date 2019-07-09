# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class IFIProjectProject(models.Model):
    _inherit = 'project.project'

    member_ids = fields.One2many('project.member', 'project_id')


class IFIProjectTeamMember(models.Model):
    _name = 'project.member'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', required=True)
    job_id = fields.Many2one('hr.job', required=True, string='Position')
    department_id = fields.Many2one('hr.department', related='employee_id.department_id', store=True)
    user_id = fields.Many2one('res.users', related='employee_id.user_id', store=True)
    project_id = fields.Many2one('project.project', required=True)
    date_from = fields.Date(required=True)
    date_to = fields.Date()
    allocation = fields.Integer(default=100, required=True)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id and self.employee_id.job_id:
            self.job_id = self.employee_id.job_id
