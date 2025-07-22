from odoo import models, fields, api


class MeasurementCalculationLine(models.Model):
    """
    Represents a line in the Measurement Calculation model in Odoo.

    This model is used to define individual measurement calculation lines
    with details such as type, position, rental information, quantities, and pricing.

    Attributes:
        type (fields.Selection): Type of the measurement calculation line (BP or POS).
        position (fields.Char): Position description.
        rental_position (fields.Char): Rental position description.
        gvh (fields.Char): Rental free time.
        gvh_unit (fields.Many2one): Unit of measure for GVH.
        description (fields.Char): Short description of the line.
        target_rental_quantity (fields.Float): Target rental quantity.
        quantity (fields.Float): Actual quantity.
        quantity_erected (fields.Float): Quantity erected.
        uom_id (fields.Many2one): Unit of measure for the line.
        currency_id (fields.Many2one): Currency used for monetary fields, defaults to the company's currency.
        total_price (fields.Monetary): Total price (EP) of the line.
        target_quantity (fields.Float): Target rental quantity.
        rental_quantity (fields.Float): Rental quantity.
        rental_unit (fields.Many2one): Unit of measure for rental quantity.
        rental_unit_price (fields.Monetary): Price per rental unit.
        measurement_id (fields.Many2one): Reference to the related Measurement Calculation.
        order_id (fields.Many2one): Reference to the related order, inherited from Measurement Calculation.
    """
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
    """
    Represents a subtable in the Measurement Calculation model in Odoo.

    This model is used to define additional details for measurement calculations,
    including rental positions, dimensions, quantities, and rental amounts.

    Attributes:
        position (fields.Many2one): Reference to a product for the position, excluding rental products.
        rental_position (fields.Many2one): Reference to a rental product for the rental position.
        description (fields.Char): Short description of the subtable entry.
        quantity (fields.Integer): Quantity of the product.
        length (fields.Float): Length of the product.
        width (fields.Float): Width of the product.
        height (fields.Float): Height of the product.
        delivered_quantity (fields.Float): Computed delivered quantity based on dimensions and quantity.
        rental_start_date (fields.Date): Start date for the rental, defaults to today.
        rental_cut_off_date (fields.Date): Cut-off date for the rental, defaults to today.
        rental_end_date (fields.Date): End date for the rental, defaults to today.
        end_date_gvh (fields.Date): End date for GVH, defaults to today.
        week (fields.Integer): Number of weeks for the rental.
        rental_total_amount (fields.Monetary): Computed total rental amount based on dimensions, quantity, and weeks.
        currency_id (fields.Many2one): Currency used for monetary fields, defaults to the company's currency.
        measurement_id (fields.Many2one): Reference to the related Measurement Calculation.
    """
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

    @api.depends('length', 'width', 'height', 'quantity')
    def _compute_delivered_quantity(self):
        """
        Computes the delivered quantity based on length, width, height, and quantity.

        This method updates the `delivered_quantity` field by multiplying
        the dimensions and quantity.
        """
        for rec in self:
            rec.delivered_quantity = (rec.length * rec.width *
                                      rec.height * rec.quantity)

    @api.depends('length', 'width', 'height', 'quantity', 'week')
    def _compute_rental_total_amount(self):
        """
        Computes the total rental amount based on week count, dimensions, and quantity.

        This method updates the `rental_total_amount` field by multiplying
        the dimensions, quantity, and weeks.
        """
        for rec in self:
            rec.rental_total_amount = (rec.length * rec.width *
                                       rec.height * rec.quantity * rec.week)
