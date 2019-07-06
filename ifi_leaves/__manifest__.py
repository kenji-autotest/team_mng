# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'IFI Employee Leave',
    'version': '1.1',
    'category': 'Human Resources',
    'description': """
Allows multiple managers to approve Leave
""",
    'depends': ['hr_holidays', 'ifi_employee'],
    'data': ['views/department_view.xml',
             'views/leave_view.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
