from odoo import models, fields, api


class EfbOffer(models.Model):
    _name = 'offer.efb'
    _description = 'EFB'

    order_id = fields.Many2one('sale.order', string='Order Reference')
    order_line_id = fields.Many2one('sale.order.line', string='Order Line Reference')
    # product_id = fields.Many2one(comodel_name='product.product', string="Product")
    description = fields.Char(string='Description')
    long_desc = fields.Text(string='Long Description')
    # currency_id = fields.Many2one('res.currency', string='Currency', related='order_id.currency_id', store=True,
    #                               readonly=True)
    # product_template_id = fields.Many2one(
    #     string="Product Template",
    #     comodel_name='product.template')
    product_uom_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=1.0)
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="UOM")
    # tax_id = fields.Many2many(
    #     comodel_name='account.tax',
    #     string="Taxes")
    # price_unit = fields.Float(
    #     string="Unit Price",
    #     digits='Product Price')
    # price_subtotal = fields.Monetary(string="Subtotal", currency_field='currency_id', compute="_compute_amount", store=True)
    # price_total = fields.Monetary(string="Total", currency_field='currency_id', compute="_compute_amount", store=True)

    # @api.onchange('product_template_id')
    # def _onchange_product_id(self):
    #     if not self.product_template_id:
    #         return
    #     self.description = self.product_template_id.name
    #     self.price_unit = self.product_template_id.list_price
    #     self.product_uom_qty = 1.0
    #     self.tax_id = self.product_template_id.taxes_id.filtered(lambda t: t.company_id == self.order_id.company_id)

    # @api.depends('product_uom_qty', 'price_unit')
    # def _compute_amount(self):
    #     for line in self:
    #         quantity = line.product_uom_qty
    #         price_unit = line.price_unit
    #         taxes = line.tax_id.compute_all(
    #             price_unit,
    #             currency=line.order_id.currency_id,
    #             quantity=quantity,
    #             product=line.product_template_id,
    #             partner=line.order_id.partner_id
    #         )
    #         line.price_subtotal = taxes['total_excluded']
    #         line.price_total = taxes['total_included']
    #
    # @api.onchange('product_uom_qty', 'price_unit')
    # def _onchange_quantity_or_price(self):
    #     self._compute_amount()


