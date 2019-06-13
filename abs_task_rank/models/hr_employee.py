# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-today Ascetic Business Solution <www.asceticbs.com>
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

## inherit class 'hr.employee' to get details of employee and set rank according to assigned Tasks to salesperson
class Employee(models.Model):
    _inherit = "hr.employee"

    number_task_rank = fields.Integer(string="Rank", compute='task_rank')

    def task_rank(self):
        employee_rank_list = []
        for employee in self:
            if employee.user_id:
                tasks_list = []
                task_ids = self.env['project.task'].search([('user_id','=',employee.user_id.id)])
                for task in task_ids:
                    if task.stage_id.name == 'Done':
                        tasks_list.append(task)
                employee_dict = { 'employee' : employee , 'length' : len(tasks_list)}
                employee_rank_list.append(employee_dict)

        ## sorted dictionary to get rank of employee
        newlist = sorted(employee_rank_list, key=lambda k: k['length'], reverse=True)   
        rank = 0
        for line in newlist:
            if line:
                rank = rank + 1
                line['employee'].update({'number_task_rank' : rank})

