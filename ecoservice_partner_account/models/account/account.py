# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    is_partner_account = fields.Boolean()
