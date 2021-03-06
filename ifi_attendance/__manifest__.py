# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'IFI Attendance',
    'version': '1.1',
    'category': 'Human Resources',
    'description': """
""",
    'depends': ['ifi_employee', 'hr_attendance', 'ifi_leaves'],
    'data': ['security/ir.model.access.csv',
             'data/hr_attendance_data.xml',
             'wizard/generate_attendances_view.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
