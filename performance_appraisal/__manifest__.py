# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Performance Appraisal',
    'version': '1.1',
    'website': '',
    'category': 'Human Resources',
    'sequence': 10,
    'summary': 'Employee Performance Appraisal',
    'depends': [
        'base_setup',
        'hr',
        'ifi_employee',

    ],
    'description': "",
    'data': [
        'security/performance_appraisal_security.xml',
        'security/ir.model.access.csv',
        'views/menu.xml',
        'views/performance_strategy_views.xml',
        'views/performance_indicator_views.xml',
        'views/performance_indicator_values_views.xml',
        'views/employee_views.xml',
        'views/performance_appraisal_views.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
