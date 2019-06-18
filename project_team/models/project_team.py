# See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    members = fields.Many2many('res.users', 'project_user_rel', 'project_id',
                               'uid', 'Project Members', help="""Project's
                               members are users who can have an access to
                               the tasks related to this project."""
                               )
    team_id = fields.Many2one('crm.team', "Project Team",
                              domain=[('type_team', '=', 'project')])

    @api.onchange('team_id')
    def get_team_members(self):
        self.members = False
        if self.team_id:
            self.members = [(6, 0, [member.id for member in self.team_id.team_members])]


class Employee(models.Model):
    _inherit = 'hr.employee'

    project_ids = fields.Many2many('project.project', compute='_compute_project_count')
    project_count = fields.Integer(string="#Project", compute='_compute_project_count')

    @api.multi
    def _compute_project_count(self):
        project = self.env['project.project'].sudo()
        for employee in self:
            user = employee.user_id
            if user:
                project_ids = project.search([('members', 'in', [user.id])])
            employee.update({'project_ids': [(6, 0, project_ids.ids)],
                             'project_count': len(set(project_ids.ids))
                             })
