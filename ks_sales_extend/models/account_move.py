from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    measurement_id = fields.Many2one('measurement.calculation',
                                     string='Measurement Calculation', tracking=True)

    def action_print_measurement_calculation(self):
        """This print's connected measurement calculation's report in pdf format."""
        # TODO - Add printing report functionality here
        pass