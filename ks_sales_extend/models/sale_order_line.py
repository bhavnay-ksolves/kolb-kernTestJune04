from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    efb_line = fields.One2many(comodel_name='offer.efb',
                               inverse_name='order_id', string="EFB Lines")

    offer_id = fields.Many2one('offer.type', string='Offer Type')
    category = fields.Selection([
        ("build", "Building for one person"),
        ("commercial", "Commercial"),
        ("skyscrapper", "Sky Scrapper"),
    ], default='build')
    is_same_delivery_address = fields.Boolean("Is Same Delivery Address", default=False)
    on_site = fields.Boolean("Employee on Construction Site", default=False)
    is_unproductive = fields.Boolean("Is Unproductive", default=False)
    is_offer_date = fields.Date(string="Offer Date")
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
    measurement_ids = fields.One2many(comodel_name='measurement.calculation',
                                      inverse_name='order_id', string="Measurement Calculation")
    measurement_count = fields.Integer(string="Measurement Cals",
                                       compute='measurement_calculation_count',
                                       default=0)
    show_efb_to_order_btn = fields.Boolean(
        compute="_compute_show_efb_to_order_btn",
        string="Show Copy EFB to Order Button"
    )

    efb_total_price = fields.Float(
        string="EFB Total Amount",
        compute="_compute_efb_line_totals",
        store=True
    )
    efb_total_unit_price = fields.Float(
        string="EFB Total Unit Price",
        compute="_compute_efb_line_totals",
        store=True
    )

    @api.depends('efb_line.price_unit', 'efb_line.product_uom_qty')
    def _compute_efb_line_totals(self):
        """Compute for the total and unit price"""
        for order in self:
            total_price = 0.0
            total_unit_price = 0.0
            for line in order.efb_line:
                total_price += line.product_uom_qty * line.price_unit
                total_unit_price += line.price_unit
            order.efb_total_price = total_price
            order.efb_total_unit_price = total_unit_price

    @api.depends('order_line')
    def _compute_show_efb_to_order_btn(self):
        """Compute method for ture 'show_efb_to_order_btn' boolean
         and hide 'action_copy_efb_to_offer' button."""
        for order in self:
            order.show_efb_to_order_btn = bool(order.order_line)

    def action_copy_efb_to_offer(self):
        """method for copy main position data from EFB table to Detail offer table
        1) Copy data.
        """
        ks_product = self.env['product.template'].browse(self.env['ir.model.data']._xmlid_to_res_id('ks_sales_extend.product_main_position')).product_variant_id.id
        """method for copy main position data from EFB table to order_line table"""
        for order in self:
            new_order_lines = []
            ks_msg = ''
            for efb_line in order.efb_line:
                new_order_lines.append((0, 0, {
                    'product_id': ks_product,
                    'long_desc': efb_line.long_desc,
                    'to_be_printed_on_pdf': True,
                    'product_uom_qty': efb_line.product_uom_qty,
                    'product_uom': efb_line.product_uom.id,
                    'name': efb_line.description,
                }))
                ks_msg += f"{efb_line.description}: Qty {efb_line.product_uom_qty}" + "\n"

            order.order_line = [(5, 0, 0)] + new_order_lines
            # ✅ Post to chatter
            order.message_post(
                body=f"EFB to Offer:\n{ks_msg}",
                subtype_xmlid="mail.mt_note"
            )

    def action_copy_offer_to_efb(self):
        """method for copy main position data from order_line table to EFB table
        1) Copy data.
        2) Delete existing record if any on EFB table.
        """
        include_taxes = True  # Set to False if needed

        for order in self:
            efb_lines = []
            ks_msg = []

            if order.efb_line:
                order.efb_line.unlink()

            lines = order.order_line.filtered(lambda l: l.product_id)
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.product_id.to_be_printed_on_pdf:
                    main_line = line
                    sub_lines = []
                    total_qty = 0.0
                    total_price = 0.0

                    # Collect subposition lines
                    i += 1
                    while i < len(lines) and not lines[i].product_id.to_be_printed_on_pdf:
                        sub = lines[i]
                        qty = sub.product_uom_qty
                        price = sub.price_total if include_taxes else sub.price_subtotal

                        total_qty += qty
                        total_price += price
                        sub_lines.append(sub)
                        i += 1

                    # Avoid divide by zero
                    unit_price = total_price / total_qty if total_qty else 0.0

                    efb_lines.append((0, 0, {
                        'product_uom_qty': total_qty,
                        'product_uom': main_line.product_uom.id,
                        'description': main_line.name,
                        'long_desc': main_line.long_desc,
                        'price_unit': unit_price,
                    }))

                    ks_msg.append(
                        f"{main_line.product_id.display_name} — "
                        f"Qty: {total_qty}, Unit Price: {unit_price:.2f}, Total: {total_price:.2f}"
                    )

                    # Optional: Log sub lines
                    for sub in sub_lines:
                        ks_msg.append(
                            f"  ↳ {sub.product_id.display_name} — "
                            f"Qty: {sub.product_uom_qty}, "
                            f"Unit Price: {sub.price_unit:.2f}, "
                            f"Total: {sub.price_total:.2f}"
                        )
                else:
                    i += 1

            order.efb_line = [(5, 0, 0)] + efb_lines

            if ks_msg:
                order.message_post(
                    body="Offer to EFB (Main + Subpositions Aggregate):\n" + "\n".join(ks_msg),
                    subtype_xmlid="mail.mt_note"
                )

    def measurement_calculation_count(self):
        """Get count of Measurement Calculations."""
        for rec in self:
            rec.measurement_count = self.env['measurement.calculation'].search_count([
                ('order_id', '=', self.id)])

    def action_get_measurement_calculation_record(self):
        """To call Measurement Calculation tree view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Measurement Calculations"),
            'view_mode': 'list,form',
            'res_model': 'measurement.calculation',
            'context': "{'default_order_id': active_id}",
            'domain': [('order_id', '=', self.id)],
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    to_be_printed_on_pdf = fields.Boolean(string='To Be Printed on PDF', default=False)
    efb_id = fields.Many2one('offer.efb', string='EFB Reference')
    long_desc = fields.Text(string='Long Description')
    ks_pos = fields.Char(string="POS", digits='Product Price', default='POS 1')

    @api.onchange('product_id')
    def _onchange_product_id_set_pdf_flag(self):
        """Onchange to autopopulate 'To be printed on pdf' boolean"""
        if self.product_id:
            self.to_be_printed_on_pdf = self.product_id.to_be_printed_on_pdf
