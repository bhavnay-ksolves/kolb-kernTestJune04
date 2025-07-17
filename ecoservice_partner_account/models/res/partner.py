# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from odoo import fields, models

ACCOUNT_TYPE_PAYABLE: str = 'liability_payable'
ACCOUNT_TYPE_RECEIVABLE: str = 'asset_receivable'


# noinspection PyAttributeOutsideInit,PyTypeChecker
class ResPartner(models.Model):
    _inherit = 'res.partner'

    has_custom_payable = fields.Boolean(
        related='property_account_payable_id.is_partner_account',
        string='Custom Payable',
    )

    has_custom_receivable = fields.Boolean(
        related='property_account_receivable_id.is_partner_account',
        string='Custom Receivable',
    )

    @property
    def company(self):
        return self.company_id or self.env.company

    def employing_company(self):
        """Get company that employs the current partner (self)"""
        # 110909 - DO NOT CHANGE BEHAVIOUR!
        if self.is_company:
            return self

        parents = []
        parent = self.parent_id
        while parent:
            # Loop parents until we reach a company
            if parent.is_company:
                return parent

            if parent.id in parents:
                # We're in an endless loop. Abort loop.
                break

            parents.append(parent.id)
            parent = parent.parent_id

        return self

    # region View

    def action_create_payable_account(self) -> bool:
        """
        Create a payable account from the GUI.

        Creating an account from the GUI always counts as manual creation.
        Thus any automatic account creation setting is ignored. The sharing
        setting is taken into account though.
        """
        self.ensure_one()
        self.create_accounts([ACCOUNT_TYPE_PAYABLE])
        return True

    def action_create_receivable_account(self) -> bool:
        """
        Create a receivable account from the GUI.

        Creating an account from the GUI always counts as manual creation.
        Thus any automatic account creation setting is ignored. The sharing
        setting is taken into account though.
        """
        self.ensure_one()
        self.create_accounts([ACCOUNT_TYPE_RECEIVABLE])
        return True

    # endregion

    def create_accounts(self, account_types: list = []) -> bool:
        for partner in self:
            account_types = account_types or partner.default_account_types()
            partner._create_accounts(account_types)
            partner._share_partner_accounts(account_types)
        return True

    def _share_partner_accounts(self, account_types):
        for account_type in account_types:
            self._share_partner_account(account_type)

    def _share_partner_account(self, account_type):
        all_companies = self.env['res.company'].sudo().search([])
        self = self.with_context(
            allowed_company_ids=self._context.get('allowed_company_ids', []) + all_companies.ids
        ).sudo()
        if not self.company.shared_partner_accounts:
            return

        companies = self.company
        if self.company.shared_partner_accounts:
            companies = self.company.sudo().search([
                ('shared_partner_accounts', '=', True)
            ])

        ftype = (
            'payable'
            if account_type == ACCOUNT_TYPE_PAYABLE else
            'receivable'
        )
        fname = f'property_account_{ftype}_id'
        main_code = getattr(self, fname).code

        # sort companys by main company and branches
        main_company_branches = {}
        for company in companies:
            main_company = company
            while main_company.parent_id:
                main_company = main_company.parent_id
            main_company_branches.setdefault(
                main_company, []
            ).append(company)

        for main_company, branches in main_company_branches.items():
            partner = self.with_company(company=main_company)
            account = getattr(partner, fname)
            ignore_existing_account = (
                account.code != main_code
                and 'DE' in account.company_ids.account_fiscal_country_id.mapped('code')
            )
            if (
                not account.is_partner_account
                or ignore_existing_account
            ):
                existing_account = account.search([
                    ('company_ids', '=', main_company.id),
                    ('is_partner_account', '=', True),
                    ('code', '=', main_code),
                    ('account_type', '=', account_type),
                ])
                if not existing_account:
                    partner.with_context(
                        ignore_existing_account=ignore_existing_account
                    )._create_account(account_type, main_code)
                    new_account = getattr(partner, fname)
                    if not main_company.shared_partner_accounts:
                        # reset the account to the old account
                        setattr(partner, fname, account)
                    account = new_account
                else:
                    account = existing_account
                    if main_company.shared_partner_accounts:
                        setattr(partner, fname, account)
            elif account.code != main_code:
                account.write({
                    'code': main_code,
                })

            for branch in branches:
                partner_branch = self.with_company(company=branch)
                account_branch = getattr(partner_branch, fname)
                if account_branch != account:
                    setattr(partner_branch, fname, account)

    def _create_accounts(self, account_types: list):
        self.ensure_one()

        for account_type in account_types:
            self._create_account(account_type)

    def _create_account(self, account_type: str, code=None):
        self.ensure_one()
        all_companies = self.env['res.company'].sudo().search([])
        self = self.with_context(
            allowed_company_ids=self._context.get('allowed_company_ids', []) + all_companies.ids
        ).sudo()

        ftype = (
            'payable'
            if account_type == ACCOUNT_TYPE_PAYABLE else
            'receivable'
        )
        fname = f'property_account_{ftype}_id'
        account = getattr(self, fname)

        if account.is_partner_account and not self._context.get('ignore_existing_account'):
            return account

        company = self.employing_company()  # 110909: DO NOT CHANGE!
        if not code:
            # !! (Their) company != (Our) self.company
            code = self.company.next_account_code(account_type)

        new_account = account.create({
            'is_partner_account': True,
            'currency_id': self.company.currency_id.id,
            'code': code,
            'name': company.name,
            'reconcile': True,
            'account_type': account_type,
            'tag_ids': [(6, 0, account.tag_ids.ids)]
        })

        result = {}
        result[fname] = new_account.id

        if self.company.partner_ref_source == account_type and not self.ref:
            result['ref'] = new_account.code

        self.write(result)

    def default_account_types(self) -> list:
        self.ensure_one()

        # When creating a new partner, supplier and customer rank is always
        # False. Checking for them to decide account types is pointless.
        return [
            ACCOUNT_TYPE_RECEIVABLE,
            ACCOUNT_TYPE_PAYABLE,
        ]
