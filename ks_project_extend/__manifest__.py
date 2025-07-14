{
    'name': 'Ks Project Extension',
    'version': '18.0.1.0.0',
    'summary': 'Customizations related to project app',
    'description': 'Customizations related to project app',
    'author': 'Ksolves India Ltd.',
    'depends': ['base','project','ks_custom_security'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_project.xml',
        'views/type_of_work.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
