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
        'ifi_employee',
        'hr'
    ],
    'description': "",
    'data': [
        # 'security/performance_appraisal_security.xml',
        # 'security/ir.model.access.csv',
        'views/performance_appraisal_menu.xml',
        'views/performance_strategy_views.xml',
    ],
    'qweb': [],
    'demo': [],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
