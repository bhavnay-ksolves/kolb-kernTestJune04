from odoo import models, fields


class EfbOffer(models.Model):
    _name = 'offer.efb'
    _description = 'EFB'

    order_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade')
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity')
    # category = fields.Selection([
    #     ("build", "Building for one person"),
    #     ("commercial", "Commercial"),
    #     ("skyscrapper", "Sky Scrapper"),
    # ], default='build')
    # is_same_delivery_address = fields.Boolean("Is Same Delivery Address", default=False)
    # on_site = fields.Boolean("Employee on Construction Site", default=False)
    # is_unproductive = fields.Boolean("Is Unproductive", default=False)
    # is_offer_date = fields.Date(string="Offer Date")
    # is_portal_date = fields.Date(string="Portal Date")
    # start_date = fields.Date(string="Start Date Of the Project")
    # end_date = fields.Date(string="End Date Of the Project")
    # send_offer_by = fields.Selection(
    #     selection=[
    #         ('email', 'Email'),
    #         ('post', 'Post'),
    #         ('both', 'Both')
    #     ],
    #     string="Send Offer By",
    #     default='email'
    # )

