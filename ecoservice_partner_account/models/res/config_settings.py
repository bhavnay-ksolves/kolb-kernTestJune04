# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # region Fields

    partner_account_generate_automatically = fields.Boolean(
        related='company_id.partner_account_generate_automatically',
        readonly=False,
    )
    shared_partner_accounts = fields.Boolean(
        related='company_id.shared_partner_accounts',
        readonly=False,
    )
    partner_ref_source = fields.Selection(
        related='company_id.partner_ref_source',
        readonly=False,
        required=True,
    )
    property_account_receivable_id = fields.Many2one(
        'account.account',
        string="Default Receivable Account",
        default=lambda self: self._get_default_receivable_account()
    )

    property_account_payable_id = fields.Many2one(
        'account.account',
        string="Default Payable Account",
        default=lambda self: self._get_default_payable_account()
    )
    module_ecoservice_partner_account_confirm_sale = fields.Boolean(
        string='Create Debitor Account on Sale Order Confirm'
    )
    module_ecoservice_partner_account_confirm_purchase = fields.Boolean(
        string='Create Creditor Account on Puchase Order Confirm'
    )

    def _get_default_receivable_account(self):
        # Retrieve from ir.config_parameter, return ID or False
        return int(
            self.env['ir.config_parameter'].sudo().get_param(
                'property_account_receivable_id',
                default=False
            )
        )

    def _get_default_payable_account(self):
        # Retrieve from ir.config_parameter, return ID or False
        return int(
            self.env['ir.config_parameter'].sudo().get_param(
                'property_account_payable_id',
                default=False
            )
        )

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        # Retrieve existing values from ir.config_parameter
        receivable_account_id = self.env['ir.config_parameter'].sudo().get_param(
            'property_account_receivable_id'
        )
        payable_account_id = self.env['ir.config_parameter'].sudo().get_param(
            'property_account_payable_id'
        )

        # Update the values in the result dictionary
        res.update({
            'property_account_receivable_id': int(
                receivable_account_id
            ) if receivable_account_id else False,
            'property_account_payable_id': int(
                payable_account_id
            ) if payable_account_id else False,
        })

        # If values are not set, use default based on chart template
        if not receivable_account_id:
            if self.env.company.chart_template == 'de_skr03':
                receivable_account = self.env['account.account'].search(
                    [('code', '=', '1410')],
                    limit=1
                )
                res['property_account_receivable_id'] = (
                    receivable_account.id if receivable_account else False
                )

        if not payable_account_id:
            if self.env.company.chart_template == 'de_skr03':
                payable_account = self.env['account.account'].search(
                    [('code', '=', '1610')],
                    limit=1
                )
                res['property_account_payable_id'] = (
                    payable_account.id if payable_account else False
                )

        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # Ensure the account IDs are being set properly
        self.env['ir.config_parameter'].sudo().set_param(
            'property_account_receivable_id',
            self.property_account_receivable_id.id if self.property_account_receivable_id else False
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'property_account_payable_id',
            self.property_account_payable_id.id if self.property_account_payable_id else False
        )
