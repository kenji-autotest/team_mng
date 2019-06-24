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


class IFIEmployeePerformance(models.Model):

    _inherit = "hr.employee"

    performance_reviewer_ids = fields.Many2many('hr.employee', 'hr_employee_performance_reviewer_rel',
                                                'employee_id', 'reviewer_id', string="Performance Review",
                                                help="These people will be requested to give performance appraisal for the employee",
                                                )
    performance_strategy_ids = fields.Many2many('performance.strategy', 'hr_employee_performance_strategy_rel',
                                                'employee_id', 'strategy_id',
                                                string="Performance Strategies")

