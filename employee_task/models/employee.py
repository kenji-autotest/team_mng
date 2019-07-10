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


class Employee(models.Model):

    _inherit = "hr.employee"

    tasks = fields.Char(compute='_compute_tasks', string='Tasks')
    tasks_count = fields.Integer(compute='_compute_tasks', string='Tasks')
    projects = fields.Char(compute='_compute_project_count', string='Projects')
    project_ids = fields.Many2many('project.project', compute='_compute_project_count', string='Projects')
    project_count = fields.Integer(compute='_compute_project_count', string="#Project")

    def _compute_project_count(self):
        project = self.env['project.project'].sudo()
        for employee in self:
            user = employee.user_id
            if user:
                project_ids = project.search(['|',
                                              ('member_ids.user_id', 'in', [user.id]),
                                              ('user_id', '=', user.id),
                                              ('message_partner_ids', 'in', [user.partner_id.id])
                                              ])
                project_count = len(set(project_ids.ids))
                employee.update({'project_ids': [(6, 0, project_ids.ids)],
                                 'projects': 'Projects: ' + str(project_count),
                                 'project_count': project_count
                                 })

    def _compute_tasks(self):
        for employee in self:
            user = employee.user_id
            if user:
                tasks = self.env['project.task'].sudo().search([('user_id', '=', user.id)])
                employee.tasks = "Tasks: " + str(len(tasks))
                employee.tasks_count = str(len(tasks))

    @api.multi
    def display_employee_tasks(self):
        """Display employee tasks"""
        if self.user_id:
            context = "{'group_by':'stage_id'}"
            template_id = self.env.ref('project.view_task_tree2').id
            search_id = self.env.ref('project.view_task_search_form').id
            return {
                'name': _('Employee Tasks'),
                'view_type': 'form',
                'view_mode': 'kanban,tree,calendar,pivot,graph,form',
                'res_model': 'project.task',
                'type': 'ir.actions.act_window',
                'view_id': template_id,
                'views': [(self.env.ref('project.view_task_tree2').id, 'tree'),
                          (self.env.ref('project.view_task_form2').id, 'form'),
                          (self.env.ref('project.view_task_kanban').id, 'kanban'),
                          (self.env.ref('project.view_task_calendar').id, 'calendar'),
                          (self.env.ref('project.view_project_task_pivot').id, 'pivot'),
                          (self.env.ref('project.view_project_task_graph').id, 'graph')],
                'search_view_id': search_id,
                'domain': [('user_id', '=', self.user_id.id)],
                'context': context
             }

    @api.multi
    def display_employee_projects(self):
        """Display employee projects"""
        if self.user_id:
            template_id = self.env.ref('project.view_project').id
            return {
                'name': _('Employee Tasks'),
                'view_type': 'form',
                'view_mode': 'tree,kanban,form',
                'res_model': 'project.project',
                'type': 'ir.actions.act_window',
                'view_id': template_id,
                'views': [(self.env.ref('project.view_project').id, 'tree'),
                          (self.env.ref('project.view_project_kanban').id, 'kanban'),
                          (self.env.ref('project.edit_project').id, 'form'),
                          ],
                'domain': [('id', 'in', self.project_ids.ids)],
             }



