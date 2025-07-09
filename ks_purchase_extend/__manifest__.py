{
    'name': 'Ks Purchase Extension',
    'version': '18.0.1.0.0',
    'summary': 'Customizations related to purchase app',
    'description': 'Customizations related to purchase app',
    'author': 'Ksolves India Ltd.',
    'depends': ['base','purchase','ks_custom_security'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_order_line_views.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
