from odoo import models, fields, api, _


class MeasurementCalculation(models.Model):
    _name = 'measurement.calculation'
    _inherit = ['mail.thread']
    _description = 'Measurement Calculation'

    name = fields.Char(string='Version', tracking=True)
    closing_date = fields.Date(string='Closing Date', tracking=True,
                               default=lambda self: fields.date.today())
    order_id = fields.Many2one('sale.order', string='Sale Order')
    measurement_ids = fields.One2many(comodel_name='measurement.calculation.line',
                                      inverse_name='measurement_id', tracking=True,
                                      string="Measurement Calculation")
    state = fields.Selection(selection=[('draft', 'Draft'),
                                        ('posted', 'Posted'),
                                        ('cancel', 'Cancelled')],
        string='Status', required=True, readonly=True, copy=False,
        tracking=True, default='draft')
    project_id = fields.Many2one(related='order_id.project_id', store=True)


    def move_to_posted(self):
        """To move the record to posted stage"""
        for rec in self:
            rec.state = 'posted'

    def move_to_cancelled(self):
        """To move the record to cancelled stage"""
        for rec in self:
            rec.state = 'cancel'

    def move_to_draft(self):
        """To move the record to draft stage"""
        for rec in self:
            rec.state = 'draft'

    def action_get_sale_order(self):
        """To call SO form view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Sales"),
            'view_mode': 'form',
            'res_model': 'sale.order',
            'domain': [('measurement_ids', 'in', [self.id])],
        }

    def action_get_invoice(self):
        """To call SO form view."""
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
