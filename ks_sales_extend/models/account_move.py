from odoo import models, fields, api, _


class AccountMove(models.Model):
    """
    Extends the Account Move model in Odoo to include a relationship with
    Measurement Calculation.

    Attributes:
        measurement_id (fields.Many2one): A reference to the Measurement Calculation model,
            allowing the account move to be linked to a specific measurement calculation.
    """
    _inherit = 'account.move'

    measurement_id = fields.Many2one(
        'measurement.calculation',
        string='Measurement Calculation',
        tracking=True
    )

    def action_print_measurement_calculation(self):
        """
        Placeholder method for printing the connected measurement calculation's report
        in PDF format.

        This method is intended to be implemented with functionality to generate and
        print the report.
        """
        # TODO - Add printing report functionality here
        pass
