{
    'name': 'Ks Project Extension',
    'version': '18.0.1.0.0',
    'summary': 'Customizations related to project app',
    'description': 'Customizations related to project app',
    'author': 'Ksolves India Ltd.',
    'depends': ['base','project','ks_custom_security'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'report/daily_construction_report.xml',
        'views/daily_construction_report_views.xml',
        'views/project_project.xml',
        'views/type_of_work.xml',
        'views/project_task_views.xml',
        'wizard/daily_construction_comment_wizard.xml',
        'wizard/project_weather_fetch_wizard_views.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
