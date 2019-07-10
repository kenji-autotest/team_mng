# See LICENSE file for full copyright and licensing details.

{
    'name': 'IFI Project Members',
    'author': 'IFI Solution',
    'maintainer': 'IFI Solution',
    'summary': 'Project Team Management',
    'category': 'Project Management',
    'website': 'http://www.ifisolution.com',
    'version': '12',
    'license': 'AGPL-3',
    'depends': ['project','hr_timesheet'],
    'data': ['security/ir.model.access.csv',
             'views/project_team_member_view.xml',
             'wizard/generate_timesheet_batches_view.xml'
    ],
    'installable': True,
}
