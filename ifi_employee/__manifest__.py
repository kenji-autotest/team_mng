# -*- coding: utf-8 -*-
#################################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2018-Today Ascetic Business Solution <www.asceticbs.com>
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

{
    'name': "IFI Employees",
    'author': 'IFI Solution',
    'category': 'Human Resources',
    'summary': """Display more info on Employee form and add new group Department Manager""",
    'license': 'AGPL-3',
    'website': 'http://www.ifisolution.com',
    'description': """
""",
    'version': '1.0',
    'depends': ['hr', 'base_encrypted_field'],
    'data': ['security/employee_security.xml',
             'security/ir.model.access.csv',
             'views/employee_view.xml',
             'views/employee_department_view.xml'],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
