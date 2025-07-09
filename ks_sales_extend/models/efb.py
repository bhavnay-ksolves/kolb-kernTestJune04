from odoo import models, fields


class EfbOffer(models.Model):
    _name = 'offer.efb'
    _description = 'EFB'

    order_id = fields.Many2one('sale.order', string='Order Reference', ondelete='cascade')
    description = fields.Char(string='Description')
    quantity = fields.Float(string='Quantity')
