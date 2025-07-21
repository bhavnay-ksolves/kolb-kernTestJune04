{
    'name': 'Ks Risk Assessment',
    'version': '18.0.1.0.0',
    'summary': 'Risk management',
    'description': 'Risk management',
    'author': 'Ksolves India Ltd.',
    'depends': ['base','project','ks_custom_security'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/project_project.xml',
        'views/risk_assessment_template.xml',
        'report/risk_assessment_report.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
