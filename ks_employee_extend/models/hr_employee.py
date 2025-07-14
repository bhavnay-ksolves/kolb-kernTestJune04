# -*- coding: utf-8 -*-
from odoo import models, fields

class Employee(models.Model):
    _inherit = 'hr.employee'

    performance = fields.Float(string="Performance (%)")
    productive_hours = fields.Float(string="Productive Hours")
    date_of_working = fields.Date(string="Date of Working")
    short_name = fields.Char(string='Short name of Employee',required=True)

    _sql_constraints = [
        ('short_name_unique', 'unique(short_name)',
         'This short name already exists for another employee. Please enter a different short name. The short name must be unique.')
    ]
    def _compute_display_name(self):
        result = []
        for record in self:
            name = record.name or ''
            short_name = record.short_name or ''
            display_name = f"{name} - {short_name}" if short_name else name
            record.display_name = display_name
        return result
