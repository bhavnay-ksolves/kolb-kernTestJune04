from odoo import models, fields, api


class EfbOffer(models.Model):
    """
    Represents the EFB Offer model in Odoo.

    This model is used to manage offers linked to sale orders and order lines,
    with additional details such as description, quantity, unit price, and total price.

    Attributes:
        order_id (fields.Many2one): Reference to the related sale order.
        order_line_id (fields.Many2one): Reference to the related sale order line.
        description (fields.Char): Short description of the offer.
        long_desc (fields.Text): Detailed description of the offer.
        sequence (fields.Float): Sequence number for ordering, defaults to 0.0.
        company_id (fields.Many2one): Reference to the company, defaults to the current company.
        product_uom_qty (fields.Float): Quantity of the product, defaults to 1.0.
        product_uom (fields.Many2one): Unit of measure for the product.
        price_unit (fields.Float): Unit price of the product.
        price_subtotal (fields.Float): Total price, computed as quantity multiplied by unit price.
    """
    _name = 'offer.efb'
    _description = 'EFB'

    order_id = fields.Many2one('sale.order', string='Order Reference')
    order_line_id = fields.Many2one('sale.order.line', string='Order Line Reference')
    description = fields.Char(string='Description')
    long_desc = fields.Text(string='Long Description')
    ks_pos = fields.Float(string="POS")
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, index=True)
    product_uom_qty = fields.Float(
        string="Quantity",
        digits='Product Unit of Measure', default=1.0)
    product_uom = fields.Many2one(
        comodel_name='uom.uom',
        string="UOM")

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_amount(self):
        """
        Computes the total price (Unit price x Quantity) for the offer.

        This method updates the `price_subtotal` field based on the quantity
        and unit price of the product.
        """
        for line in self:
            line.price_subtotal = line.product_uom_qty * line.price_unit

    price_unit = fields.Float(string="Unit Price", digits='Product Price')
    price_subtotal = fields.Float(string="Total", compute="_compute_amount", store=True)

    @api.model_create_multi
    def create(self, vals):
        # Auto-assign sequence if not provided and parent is known
        if not vals[0].get('ks_pos') and vals[0].get('order_id'):
            parent = self.env['sale.order'].browse(vals[0].get('order_id'))
            if parent.exists():
                existing_sequences = parent.efb_line.mapped('ks_pos')
                vals[0]['ks_pos'] = max(existing_sequences or [0.0]) + 1.0
            else:
                vals[0]['ks_pos'] = 1.0
        elif not vals[0].get('ks_pos'):
            # Fallback if no parent
            vals[0]['ks_pos'] = 1.0

        return super(EfbOffer, self).create(vals)

