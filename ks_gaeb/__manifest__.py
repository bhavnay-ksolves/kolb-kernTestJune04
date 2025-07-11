# -*- coding: utf-8 -*-
{
    'name': 'Sale Order X86 File',
    'version': '1.0',
    'depends': ['sale'],
    'author': 'Ksolves',
    'category': 'Sales',
    'description': 'Adds a button on Sale Order to import/export .x86 file',
    'data': [
        'security/ir.model.access.csv',
        'views/import_sale_order_x86_view.xml',
        'views/d86_sale_order_template.xml',
        'views/sale_order_template.xml',
        'views/sale_order_view.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
