# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.
{
    # App Information
    'name': 'Debtor & Creditor Numbers',
    'summary': 'New debit and credit account following a sequence per company for partner.',
    'category': 'Accounting',
    'version': '18.0.1.1.5',
    'license': 'OPL-1',
    'application': False,
    'installable': True,
    # Author
    'author': 'ecoservice GbR',
    'maintainer': 'ecoservice GbR',
    'website': 'https://www.ecoservice.de/shop/debitoren-kreditorennummern-177',
    'live_test_url': 'https://www.ecoservice.de/odoo-demo',
    # Odoo Apps Store
    'price': 650.00,
    'currency': 'EUR',
    'images': [
        'images/main_screenshot.gif',
    ],
    # Dependencies
    'depends': [
        'base',
        'account',
    ],
    # Data
    'data': [
        'views/res/config/settings/form.xml',
        'views/res/partner/form.xml',
        'views/res/partner/action.xml',
        'views/res/account/form.xml',
    ],
}
