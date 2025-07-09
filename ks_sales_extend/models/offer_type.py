from odoo import models, fields


class OfferType(models.Model):
    _name = 'offer.type'
    _description = 'Offer Type'

    name = fields.Char(string='Name', required=True)
