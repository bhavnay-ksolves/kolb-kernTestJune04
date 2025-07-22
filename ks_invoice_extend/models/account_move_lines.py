from odoo import models, fields

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    delivered_work = fields.Text(string='Delivered Work')
    ks_pos = fields.Char(string="POS", digits='Product Price', default='POS 1')