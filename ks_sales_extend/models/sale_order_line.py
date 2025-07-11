from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    efb_line = fields.One2many(comodel_name='offer.efb', inverse_name='order_id', string="EFB Lines")

    offer_id = fields.Many2one('offer.type', string='Offer Type')
    category = fields.Selection([
        ("build", "Building for one person"),
        ("commercial", "Commercial"),
        ("skyscrapper", "Sky Scrapper"),
    ], default='build')
    is_same_delivery_address = fields.Boolean("Is Same Delivery Address", default=False)
    on_site = fields.Boolean("Employee on Construction Site", default=False)
    is_unproductive = fields.Boolean("Is Unproductive", default=False)
    is_portal_date = fields.Date(string="Portal Date")
    start_date = fields.Date(string="Start Date Of the Project")
    end_date = fields.Date(string="End Date Of the Project")
    send_offer_by = fields.Selection(
        selection=[
            ('email', 'Email'),
            ('post', 'Post'),
            ('both', 'Both')
        ],
        string="Send Offer By",
        default='email'
    )
    show_efb_to_order_btn = fields.Boolean(
        compute="_compute_show_efb_to_order_btn",
        string="Show Copy EFB to Order Button"
    )

    # efb_amount_untaxed = fields.Monetary(
    #     string="EFB Subtotal",
    #     compute="_compute_efb_totals",
    #     store=True,
    #     currency_field='currency_id'
    # )
    # efb_amount_tax = fields.Monetary(
    #     string="EFB Taxes",
    #     compute="_compute_efb_totals",
    #     store=True,
    #     currency_field='currency_id'
    # )
    # efb_amount_total = fields.Monetary(
    #     string="EFB Total",
    #     compute="_compute_efb_totals",
    #     store=True,
    #     currency_field='currency_id'
    # )

    # @api.depends('efb_line.price_subtotal', 'efb_line.price_total', 'efb_line.tax_id')
    # def _compute_efb_totals(self):
    #     """Compute method for total calculation
    #     1) Calculate subtotal.
    #     2) Calculate total tax.
    #     3) Calculate total amount.
    #     """
    #     for order in self:
    #         amount_untaxed = 0.0
    #         amount_total = 0.0
    #         amount_tax = 0.0
    #
    #         currency = order.currency_id
    #         partner = order.partner_id
    #
    #         for line in order.efb_line:
    #             taxes = line.tax_id.compute_all(
    #                 line.price_unit,
    #                 currency=currency,
    #                 quantity=line.product_uom_qty,
    #                 product=line.product_template_id,
    #                 partner=partner,
    #             )
    #             amount_untaxed += taxes['total_excluded']
    #             amount_total += taxes['total_included']
    #             amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
    #
    #         order.efb_amount_untaxed = amount_untaxed
    #         order.efb_amount_tax = amount_tax
    #         order.efb_amount_total = amount_total

    @api.depends('order_line')
    def _compute_show_efb_to_order_btn(self):
        """Compute method for ture 'show_efb_to_order_btn' boolean
         and hide 'action_copy_efb_to_offer' button."""
        for order in self:
            order.show_efb_to_order_btn = bool(order.order_line)

    def action_copy_efb_to_offer(self):
        """method for copy main position data from EFB table to order_line table"""
        for order in self:
            new_order_lines = []
            # ks_msg = []
            ks_msg = ''
            for efb_line in order.efb_line:
                new_order_lines.append((0, 0, {
                    'product_template_id': self.env['ir.model.data']._xmlid_to_res_id('ks_sales_extend.product_main_position'),
                    'product_uom_qty': efb_line.product_uom_qty,
                    'product_uom': efb_line.product_uom.id,
                    # 'price_unit': efb_line.price_unit,
                    # 'tax_id': [(6, 0, efb_line.tax_id.ids)],
                    'name': efb_line.description,
                }))
                ks_msg += f"{efb_line.description}: Qty {efb_line.product_uom_qty}" + "\n"
                # ks_msg.append(
                #     f"{efb_line.product_id.display_name} — "
                #     f"Qty: {efb_line.product_uom_qty}, "
                #     f"Unit Price: {efb_line.price_unit:.2f}, "
                #     f"Total: {efb_line.price_total:.2f}"
                # )
            order.order_line = [(5, 0, 0)] + new_order_lines
            # ✅ Post to chatter
            # message = "\n".join(ks_msg)
            order.message_post(
                body=f"EFB to Offer:\n{ks_msg}",
                subtype_xmlid="mail.mt_note"
            )

    def action_copy_offer_to_efb(self):
        """method for copy main position data from order_line table to EFB table
        1) Copy data.
        2) Delete existing record if any on EFB table.
        """
        for order in self:
            efb_lines = []
            ks_msg = []
            if order.efb_line:
                order.efb_line.unlink()
            for line in order.order_line:
                if line.product_id.to_be_printed_on_pdf:
                    efb_lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'product_template_id': line.product_template_id.id,
                        'product_uom_qty': line.product_uom_qty,
                        'product_uom': line.product_uom.id,
                        'price_unit': line.price_unit,
                        'tax_id': [(6, 0, line.tax_id.ids)],
                        'description': line.name,
                        'price_subtotal': line.price_subtotal,
                        'price_total': line.price_total,
                    }))
                    ks_msg.append(
                        f"{line.product_id.display_name} — "
                        f"Qty: {line.product_uom_qty}, "
                        f"Unit Price: {line.price_unit:.2f}, "
                        f"Total: {line.price_total:.2f}"
                    )
            order.efb_line = [(5, 0, 0)] + efb_lines
            # ✅ Post to chatter
            message = "\n".join(ks_msg)
            order.message_post(
                body=f"Offer to EFB:\n{message}",
                subtype_xmlid="mail.mt_note"
            )


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    to_be_printed_on_pdf = fields.Boolean(string='To Be Printed on PDF', default=False)
    efb_id = fields.Many2one('offer.efb', string='EFB Reference')

    @api.onchange('product_id')
    def _onchange_product_id_set_pdf_flag(self):
        """Onchange to autopopulate 'To be printed on pdf' boolean"""
        if self.product_id:
            self.to_be_printed_on_pdf = self.product_id.to_be_printed_on_pdf
