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

    appraisal_strategy_ids = fields.One2many('employee.performance.reviewer', 'employee_id', string="Appraisal Reviewers")
    performance_strategy_ids = fields.Many2many('performance.strategy', 'hr_employee_performance_strategy_rel',
                                                'employee_id', 'strategy_id', string="Performance Strategies")

    @api.multi
    def write(self, vals):
        res = super(IFIEmployeePerformance, self).write(vals)
        if vals.get('appraisal_strategy_ids', False):
            for r in self:
                strategy_ids = r.appraisal_strategy_ids.mapped('strategy_id')
                r.performance_strategy_ids = [(6, 0, list(set(strategy_ids.ids)))]
        return res


class IFIEmployeePerformanceStrategy(models.Model):

    _name = "employee.performance.reviewer"

    employee_id = fields.Many2one('hr.employee', string='Employee')
    strategy_id = fields.Many2one('performance.strategy', string="Performance Strategy")
    reviewer_ids = fields.Many2many('hr.employee', 'employee_performance_reviewer_employee_rel', 'employee_strategy_id',
                                    'reviewer_id', string="Reviewer",
                                    help="These people will be requested to give performance appraisal for the employee")
    
    @api.model
    def create(self, vals):
        employee_id = self.env.context.get('active_id')
        if not vals.get('employee_id', False):
            vals.update({'employee_id': employee_id})
        if vals.get('reviewer_ids', False):
            vals_tmp = vals.pop('reviewer_ids')
            res = super(IFIEmployeePerformanceStrategy, self).create(vals)
            res.write({'reviewer_ids': [tuple(vals_tmp[0])]})
        else:
            res = super(IFIEmployeePerformanceStrategy, self).create(vals)
        return res


