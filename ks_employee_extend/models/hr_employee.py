# -*- coding: utf-8 -*-
from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'

    performance = fields.Float(string="Performance (%)")
    productive_hours = fields.Float(string="Productive Hours")
    date_of_working = fields.Date(string="Date of Working")
    last_working_date = fields.Date(string="Last Working Date")

    short_name = fields.Char(string='Short name of Employee')

    def _compute_display_name(self):
        result = []
        for record in self:
            name = record.name or ''
            short_name = record.short_name or ''
            display_name = f"{name} - {short_name}" if short_name else name
            record.display_name = display_name
        return result
