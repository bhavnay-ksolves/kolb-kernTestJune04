from odoo import models, fields, api, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    efb_line = fields.One2many(comodel_name='offer.efb',
                               inverse_name='order_id', string="EFB Lines")

    offer_id = fields.Many2one('offer.type', string='Offer Type')
    category = fields.Selection([
        ("build", "Building for one person"),
        ("commercial", "Commercial"),
        ("skyscrapper", "Sky Scrapper"),
    ], default='build')
    is_same_delivery_address = fields.Boolean("Is Same Delivery Address", default=False)
    on_site = fields.Boolean("Employee on Construction Site", default=False)
    is_unproductive = fields.Boolean("Is Unproductive", default=False)
    is_offer_date = fields.Date(string="Offer Date")
    is_portal_date = fields.Date(string="Portal Date")
    start_date = fields.Date(string="Start Date Of the Project")
    end_date = fields.Date(string="End Date Of the Project")
    send_offer_by = fields.Selection(
        selection=[
            ('email', 'Email'),
            ('post', 'Post'),
            ('both', 'Both')
        ],
        string="Send Offer By",
        default='email'
    )
    measurement_ids = fields.One2many(comodel_name='measurement.calculation',
                                      inverse_name='order_id', string="Measurement Calculation")
    measurement_count = fields.Integer(string="Measurement Cals",
                                       compute='measurement_calculation_count',
                                       default=0)

    def measurement_calculation_count(self):
        """Get count of Measurement Calculations."""
        for rec in self:
            rec.measurement_count = self.env['measurement.calculation'].search_count([
                ('order_id', '=', self.id)])

    def action_get_measurement_calculation_record(self):
        """To call Measurement Calculation tree view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Measurement Calculations"),
            'view_mode': 'list,form',
            'res_model': 'measurement.calculation',
            'context': "{'default_order_id': active_id}",
            'domain': [('order_id', '=', self.id)],
        }

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    to_be_printed_on_pdf = fields.Boolean(string='To Be Printed on PDF', default=False)

    # @api.onchange('product_id')
    # def _onchange_product_id_set_pdf_flag(self):
    #     if self.product_id:
    #         self.to_be_printed_on_pdf = self.product_id.to_be_printed_on_pdf
