from odoo import models, fields, api, _


class MeasurementCalculation(models.Model):
    """
    Model for Measurement Calculation.

    This model is used to manage measurement calculations related to sales orders.
    It includes fields for tracking the version, closing date, associated sale order,
    measurement lines, and the state of the calculation. It also provides methods
    to change the state and interact with related records.
    """
    _name = 'measurement.calculation'
    _inherit = ['mail.thread']  # Inherits mail.thread for tracking changes.
    _description = 'Measurement Calculation'

    # Name of the measurement calculation version, tracked for changes.
    name = fields.Char(string='Version', tracking=True)

    # Closing date of the measurement calculation, tracked for changes.
    closing_date = fields.Date(
        string='Closing Date',
        tracking=True,
        default=lambda self: fields.date.today()
    )

    # Many2one relation to the associated sale order.
    order_id = fields.Many2one('sale.order', string='Sale Order')

    # One2many relation to measurement calculation lines, tracked for changes.
    measurement_ids = fields.One2many(
        comodel_name='measurement.calculation.line',
        inverse_name='measurement_id',
        tracking=True,
        string="Measurement Calculation"
    )

    # State of the measurement calculation, tracked for changes.
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled')
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft'
    )

    # Related field to fetch the project ID from the associated sale order.
    project_id = fields.Many2one(related='order_id.project_id', store=True)

    def move_to_posted(self):
        """
        Change the state of the record to 'posted'.
        """
        for rec in self:
            rec.state = 'posted'

    def move_to_cancelled(self):
        """
        Change the state of the record to 'cancelled'.
        """
        for rec in self:
            rec.state = 'cancel'

    def move_to_draft(self):
        """
        Change the state of the record to 'draft'.
        """
        for rec in self:
            rec.state = 'draft'

    def action_get_sale_order(self):
        """
        Open the Sale Order form view filtered by the current measurement calculation.

        Returns:
            dict: Action dictionary to open the Sale Order form view.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Sales"),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'domain': [('measurement_ids', 'in', [self.id])],
        }

    def action_get_invoice(self):
        """
        Placeholder method to open the Invoice form view.

        TODO:
            Implement the logic to open the Invoice form view.
        """
        self.ensure_one()
        pass
        # TODO: build the Invoice form
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': _("Sales"),
        #     'view_mode': 'form',
        #     'res_model': 'sale.order',
        #     'domain': [('measurement_ids', 'in', [self.id])],
        # }
