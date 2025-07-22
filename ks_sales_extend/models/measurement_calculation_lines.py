from odoo import models, fields, api


class MeasurementCalculationLine(models.Model):
    _name = 'measurement.calculation.line'
    _description = 'Measurement Calculation Line'

    type = fields.Selection([("bp", "BP"), ("pos", "POS")],
                            default="pos", string=' Typ')
    position = fields.Char(string='Position', tracking=True)
    rental_position = fields.Char(string='Rental Position', tracking=True)
    gvh = fields.Char(string="Rental free Time", tracking=True)
    gvh_unit = fields.Many2one('uom.uom', string='GVH-Unit', tracking=True)
    description = fields.Char(string='Short Description', tracking=True)
    target_rental_quantity = fields.Float(string='Target Qty', tracking=True)
    quantity = fields.Float(string='Actual Qty')
    quantity_erected = fields.Float(string='Qty Erected', tracking=True)
    uom_id = fields.Many2one('uom.uom', string='Unit')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self: self.env.company.currency_id,
                                  string='Currency', required=True)
    total_price = fields.Monetary(string='EP',
                                  currency_field='currency_id')
    target_quantity = fields.Float(string='Target rental qty', tracking=True)
    rental_quantity = fields.Float(string='Rental qty', tracking=True)
    rental_unit = fields.Many2one('uom.uom', string='Rental Unit', tracking=True)
    rental_unit_price = fields.Monetary(string='Rental Unit Price',
                                        tracking=True,
                                        currency_field='currency_id')
    measurement_id = fields.Many2one('measurement.calculation', tracking=True,
                                     string='Measurement')
    order_id = fields.Many2one(related='measurement_id.order_id', tracking=True, )


class MeasurementCalculationSubtable(models.Model):
    _name = 'measurement.calculation.subtable'
    _description = 'Measurement Calculation Subtable'

    position = fields.Many2one('product.product', string='Position',
                               tracking=True, domain=[('rent_ok', '!=', True)])
    rental_position = fields.Many2one('product.product', string='Rental Position',
                                      tracking=True, domain=[('rent_ok', '=', True)])
    description = fields.Char(string='Short Description', tracking=True)
    quantity = fields.Integer(string='Quantity', tracking=True)
    length = fields.Float(string='Length', tracking=True)
    width = fields.Float(string='Width', tracking=True)
    height = fields.Float(string='Height', tracking=True)
    delivered_quantity = fields.Float(string='Delivered Quantity', tracking=True,
                                      compute='_compute_delivered_quantity')
    rental_start_date = fields.Date(string='Rental start date',
                                    default=fields.Date.context_today)
    rental_cut_off_date = fields.Date(string='Rental date', tracking=True,
                                      default=fields.Date.context_today)
    rental_end_date = fields.Date(string='Rental end date', tracking=True,
                                  default=fields.Date.context_today)
    end_date_gvh = fields.Date(string='End date GVH', tracking=True,
                               default=fields.Date.context_today)
    week = fields.Integer(string='Weeks', tracking=True, )
    rental_total_amount = fields.Monetary(string='Rental Total Amount',
                                          compute='_compute_rental_total_amount',
                                          currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self: self.env.company.currency_id,
                                  required=True, tracking=True)
    measurement_id = fields.Many2one('measurement.calculation', tracking=True,
                                     string='Measurement')
    # order_id = fields.Many2one(related='measurement_id.order_id', tracking=True, )

    @api.depends('length', 'width', 'height', 'quantity')
    def _compute_delivered_quantity(self):
        """To calculate Delivered qty based on length, width, height and quantity."""
        for rec in self:
            rec.delivered_quantity = (rec.length * rec.width *
                                      rec.height * rec.quantity)

    @api.depends('length', 'width', 'height', 'quantity', 'week')
    def _compute_rental_total_amount(self):
        """To calculate Rental Total Amount based on week count,
        length, width, height and quantity."""
        for rec in self:
            rec.rental_total_amount = (rec.length * rec.width *
                                       rec.height * rec.quantity * rec.week)
