{
    'name': 'Ks Invoice Extension',
    'version': '18.0.1.0.0',
    'summary': 'Customizations related to invoice app',
    'description': 'Customizations related to invoice app',
    'author': 'Ksolves India Ltd.',
    'depends': ['base','product','project_sequence','sale','account','ks_custom_security'],
    'data': [
        'report/invoice_report.xml',
        'views/account_move_views.xml',
        'views/account_move_lines_views.xml',
        'views/res_config_settings_views.xml',
        'views/project_project.xml',
        'data/product_data.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
