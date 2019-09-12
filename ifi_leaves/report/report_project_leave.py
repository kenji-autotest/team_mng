# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class ProjectLeaveReport(models.Model):
    _name = "project.leave.report"
    _auto = False

    leave_id = fields.Many2one('hr.leave', string='Leave Request')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    job_title = fields.Char()
    department_id = fields.Many2one('hr.department')
    date_from = fields.Date()
    date_to = fields.Date()
    number_of_days = fields.Float(string='Number of Days')
    project_id = fields.Many2one('project.project', string='Project')
    project_manager = fields.Many2one('hr.employee', string='PM')
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Approved')
    ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
        help="The status is set to 'To Submit', when a leave request is created." +
             "\nThe status is 'To Approve', when leave request is confirmed by user." +
             "\nThe status is 'Refused', when leave request is refused by manager." +
             "\nThe status is 'Approved', when leave request is approved by manager.")

    @api.model_cr
    def init(self):
        """ Leave by project"""
        tools.drop_view_if_exists(self._cr, 'project_leave_report')
        self._cr.execute(""" CREATE VIEW project_leave_report AS (
            SELECT row_number() over() as id,
            e.id AS employee_id,
            e.job_title,
            e.department_id,
            l.id AS leave_id,
            pp.id AS project_id,
            pp.user_id as project_manager,
            l.state,
            CASE l.request_unit_half WHEN true THEN 0.5
                ELSE l.number_of_days
                END AS number_of_days,
                
            CASE WHEN l.request_date_from < p.date_from THEN p.date_from
                ELSE l.request_date_from
                END AS date_from,
            
            CASE WHEN l.request_date_to > p.date_to THEN p.date_to
                ELSE l.request_date_to
                END AS date_to
            FROM project_project AS pp 
            INNER JOIN project_member AS p ON pp.id = p.project_id 
            INNER JOIN hr_leave AS l ON p.employee_id = l.employee_id and 
                (l.request_date_from < p.date_to or p.date_to is null) and p.date_from < l.request_date_to
            INNER JOIN
            hr_employee AS e ON l.employee_id = e.id 
            WHERE l.state != 'refuse' and e.active=TRUE and pp.active=TRUE
        )""")
