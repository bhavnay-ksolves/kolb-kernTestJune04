from odoo import models, fields, api


class EfbOffer(models.Model):
    _name = 'offer.efb'
    _description = 'EFB'

    order_id = fields.Many2one('sale.order', string='Order Reference')
    order_line_id = fields.Many2one('sale.order.line', string='Order Line Reference')
    description = fields.Char(string='Description')
    long_desc = fields.Text(string='Long Description')
    sequence = fields.Float(string="Sequence", digits='Product Price', default=0.0)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, index=True)
    product_uom_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=1.0)
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="UOM")

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """Compute for the total(Unit price x QTY)"""
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit

    price_unit = fields.Float(string="Unit Price", digits='Product Price')
    price_subtotal = fields.Float(string="Total", compute="_compute_amount", store=True)

    @api.model
    def create(self, vals):
        """Sequence Generated"""
        max_seq = self.search([], order='sequence desc', limit=1).sequence or 0
        vals['sequence'] = max_seq + 1
        return super().create(vals)
