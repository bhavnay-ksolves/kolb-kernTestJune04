# -*- coding: utf-8 -*-
from odoo import models, fields

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    manufacturer_special_price = fields.Monetary(string="Manufacturer Special Price")
    lvp = fields.Monetary(string="LVP")
    lot_barcode = fields.Many2one('stock.lot',string="EAN/GTIN")
    container = fields.Many2one('product.container',string='Container')
    default_code = fields.Char('Article Nr', index=True)

class StockContainer(models.Model):
    _name = 'product.container'
    _description = 'Container'

    name = fields.Char(string="Container Name", required=True)