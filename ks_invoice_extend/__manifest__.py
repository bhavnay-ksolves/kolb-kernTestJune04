{
    'name': 'Ks Invoice Extension',
    'version': '18.0.1.0.0',
    'summary': 'Customizations related to invoice app',
    'description': 'Customizations related to invoice app',
    'author': 'Ksolves India Ltd.',
    'depends': ['base','product','account','ks_custom_security'],
    'data': [
        # 'security/ir.model.access.csv',
        # 'security/security.xml',
        # 'views/daily_construction_report_views.xml',
        # 'views/project_project.xml',
        'views/account_move_views.xml',
        # 'report/daily_construction_report.xml',
        # 'wizard/daily_construction_comment_wizard.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
