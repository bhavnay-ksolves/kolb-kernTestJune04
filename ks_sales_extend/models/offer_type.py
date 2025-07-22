from odoo import models, fields

class OfferType(models.Model):
    """
    Represents the Offer Type model in Odoo.

    This model is used to define different types of offers that can be linked
    with sale orders. Each offer type has a unique name.

    Attributes:
        name (fields.Char): The name of the offer type. This field is required.
    """
    _name = 'offer.type'  # Internal name of the model
    _description = 'Offer Type'  # Description of the model

    name = fields.Char(string='Name', required=True)  # Name of the offer type