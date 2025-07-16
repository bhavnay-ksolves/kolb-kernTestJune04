# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import exceptions, fields, models

ACCOUNT_TYPE_PAYABLE: str = 'liability_payable'
ACCOUNT_TYPE_RECEIVABLE: str = 'asset_receivable'


class ResCompany(models.Model):
    _inherit = 'res.company'

    # region Fields
    asset_receivable_sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
    )
    liability_payable_sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
    )
    partner_account_generate_automatically = fields.Boolean(
        string='Automatic Account Generation',
        help=(
            'Generate partner payable or receivable account with first '
            'in or out going invoice related to the partner.'
        )
    )
    partner_ref_source = fields.Selection(
        selection=[
            ('none', 'None'),
            ('asset_receivable', 'Receivable'),
            ('liability_payable', 'Payable'),
        ],
        string='Partner Reference',
        default='none',
        required=True,
    )

    # ~~~~~ Developer Notice ~~~~~
    # The idea of shared partner accounts is not really compatible with odoo.
    # Account field "company_id" is required and has a bound unique constraint.
    # Removing the required attribute will keep account bookings bound the
    # to the company_id of the account - which now would be False or null.
    # Booking into the account of another company leads to data inconsistency
    # and conflicts with other accounting modules. Remember that all account
    # property fields carry the company_dependent attribute - making such
    # conditional is not possible.

    shared_partner_accounts = fields.Boolean(
        string='Share Accounts',
        default=False,
        help=(
            'Instead of using company specific partner accounts, use partner '
            'accounts shared across all companies that have this option enabled.'
        ),
    )

    # endregion

    def write(self, vals):
        self._vals_shared_partner_accounts(vals)
        return super().write(vals)

    @property
    def account_company_id(self) -> int:
        if self.shared_partner_accounts:
            return False
        return self.id

    def _vals_shared_partner_accounts(self, vals: dict):
        if 'shared_partner_accounts' not in vals:
            return

        irseq = self.env['ir.sequence'].sudo()

        # ACCOUNT_TYPE_RECEIVABLE
        asset_receivable_sequence_id = irseq.search([
            ('code', '=', f'{ACCOUNT_TYPE_RECEIVABLE}'),
            ('company_id', '=', self.id),
        ]) or irseq.create(
            self._create_account_sequence_values(ACCOUNT_TYPE_RECEIVABLE),
        )

        # ACCOUNT_TYPE_PAYABLE
        liability_payable_sequence_id = irseq.search([
            ('code', '=', f'{ACCOUNT_TYPE_PAYABLE}'),
            ('company_id', '=', self.id),
        ]) or irseq.create(
            self._create_account_sequence_values(ACCOUNT_TYPE_PAYABLE),
        )

        vals.update({
            'asset_receivable_sequence_id': asset_receivable_sequence_id.id,
            'liability_payable_sequence_id': liability_payable_sequence_id.id,
        })

    def account_sequence(self, account_type):
        self.ensure_one()
        fname = f'{account_type}_sequence_id'
        field = getattr(self, fname)

        if not field:
            seq = self.env['ir.sequence'].create(
                self._create_account_sequence_values(account_type),
            )
            self.write({
                fname: seq,
            })

        return getattr(self, fname)

    def _create_account_sequence_values(self, account_type):
        digits = self.get_account_code_digits() + 1
        return {
            'code': f'{account_type}',
            'company_id': self.id,
            'name': f'{account_type}: {self.name}',
            'number_next': self.min_account_codes()[account_type],
            'padding': digits,
        }

    def get_account_code_digits(self) -> int:
        account_chart = self.env['account.chart.template'].sudo()
        account_chart_data = account_chart._get_chart_template_data(
            self.chart_template
        )
        template_data = account_chart_data.pop('template_data')
        code_digits = template_data.get('code_digits')
        if not code_digits:
            # Sometimes it's just a dict without contents
            raise exceptions.ValidationError(
                'Please set a Fiscal Localization Package for your company '
                'in the settings'
            )

        if isinstance(code_digits, str) and code_digits.isnumeric():
            code_digits = int(code_digits)

        if not isinstance(code_digits, int):
            raise exceptions.ValidationError(
                'Please set a Fiscal Localization Package for your company '
                'in the settings'
            )

        return code_digits

    def min_account_codes(self) -> dict:
        digits = self.get_account_code_digits() + 1
        return {
            ACCOUNT_TYPE_PAYABLE: int('7'.ljust(digits, '0')),
            ACCOUNT_TYPE_RECEIVABLE: int('1'.ljust(digits, '0')),
        }

    def max_account_codes(self) -> dict:
        digits = self.get_account_code_digits() + 1
        return {
            ACCOUNT_TYPE_PAYABLE: int('9'.ljust(digits, '9')),
            ACCOUNT_TYPE_RECEIVABLE: int('6'.ljust(digits, '9')),
        }

    def next_account_code(self, account_type):
        """
        Return the next available account code.

        :type params: dict
        :param params: Parameter necessary to find the next account code
        :rtype: int|bool
        :return: Next available account code
        """

        if self.shared_partner_accounts:
            # Don't use sequence for shared accounts! It'll only be in constant
            # conflict with non-shared and DB constraints.
            companies = self.search([
                ('shared_partner_accounts', '=', True)
            ])
            # Don't work with order by. int type strings sorting is messy.
            accs = self.env['account.account'].sudo().search([
                ('account_type', '=', account_type),
                ('company_ids', 'in', companies.ids),
            ])

            min_code = self.min_account_codes()[account_type]
            max_code = self.max_account_codes()[account_type]
            codes = [
                int(c)
                for c in accs.mapped('code')
                if int(c) >= min_code
            ] or [min_code - 1]
            code = max(codes) + 1

            if code > max_code:
                raise exceptions.UserError(
                    f'Limit of account code {max_code} reached for '
                    f'{account_type}. Please increase account chart digits.'
                )

            return code

        # Ensure all gaps are used and prevent traceback with already
        # existing account codes. account_type is irrelevant for the
        # odoo standard constraint!
        seq = self.account_sequence(account_type)
        while True:
            code = seq.next_by_id()
            accs = self.env['account.account'].sudo().search(
                [
                    ('code', '=', code),
                    ('company_ids', '=', self.id),
                ],
                limit=1,
            )
            if not accs:
                return code
