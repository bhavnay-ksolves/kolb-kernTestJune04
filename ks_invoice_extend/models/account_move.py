# -*- coding: utf-8 -*-
from odoo import models, fields

class ProductProduct(models.Model):
    _inherit = 'product.product'

    to_be_printed_on_pdf = fields.Boolean(string='To Be Printed on PDF', default=False)

class AccountMove(models.Model):
    _inherit = 'account.move'

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        help='Related project for this invoice'
    )
    invoice_stage = fields.Selection([
        ('intermediate', 'Intermediate Invoice'),
        ('final', 'Final Invoice'),
    ], string='Invoice Stage', default='intermediate',required=True)
    qr_code = fields.Binary("Payment QR Code",tracking=True)
    project_number = fields.Char(
        string='Project Number',
        related='project_id.sequence_code',
        readonly=True
    )
    period_start = fields.Datetime(string="Period Start")
    period_end = fields.Datetime(string="Period End")
    measurement_id = fields.Many2one(
        'measurement.calculation',  # Replace with your actual model name
        string='Measurement Calculation',
        help='Select the measurement record associated with this invoice'
    )
