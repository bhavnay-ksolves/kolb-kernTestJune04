# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    delivered_work = fields.Text(string='Delivered Work')
    ks_pos = fields.Float(string="POS")
    short_description = fields.Char(string='Short Description', help='Short description for the invoice line')
    long_description = fields.Text(string='Long Description', help='Long description for the invoice line')

