{
    'name': 'Ks Employee Extension',
    'version': '18.0.1.0.0',
    'summary': 'Customizations related to employee app',
    'description': 'Customizations related to employee app',
    'author': 'Ksolves India Ltd.',
    'depends': ['base','hr','ks_custom_security','hr_hourly_cost'],
    'data': [
    #     'security/ir.model.access.csv',
        'views/hr_employee.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
