# -*- coding: utf-8 -*-
"""
Extension of the hr.employee model to include additional fields and functionality.

This module adds custom fields to the Employee model for tracking performance, productive hours,
date of working, and a unique short name. It also includes a method for computing a custom display name.

Classes:
    Employee: Extends the `hr.employee` model to include additional fields and constraints.

Attributes:
    performance (Float): Represents the performance percentage of the employee.
    productive_hours (Float): Tracks the productive hours worked by the employee.
    date_of_working (Date): Records the date of working for the employee.
    short_name (Char): A unique short name for the employee, required for identification.

SQL Constraints:
    short_name_unique: Ensures that the short name is unique across all employees.

Methods:
    _compute_display_name: Computes a custom display name using the employee's name and short name.
"""

from odoo import models, fields


class Employee(models.Model):
    """
    Extension of the hr.employee model to include additional fields and functionality.
    """
    _inherit = 'hr.employee'

    # Represents the performance percentage of the employee
    performance = fields.Float(string="Performance (%)")
    # Tracks the productive hours worked by the employee
    productive_hours = fields.Float(string="Productive Hours")
    # Records the date of working for the employee
    date_of_working = fields.Date(string="Date of Working")
    # A unique short name for the employee, required for identification
    short_name = fields.Char(string='Short name of Employee', required=True)

    # SQL constraint to ensure the short name is unique across all employees
    _sql_constraints = [
        ('short_name_unique', 'unique(short_name)',
         'This short name already exists for another employee. Please enter a different short name. '
         'The short name must be unique.')
    ]

    def _compute_display_name(self):
        """
        Computes a custom display name using the employee's name and short name.

        Iterates through the records and combines the `name` and `short_name` fields to create a
        display name. If the `short_name` is not provided, the display name defaults to the `name`.

        Returns:
            list: A list of computed display names for the records.
        """
        result = []
        for record in self:
            name = record.name or ''
            short_name = record.short_name or ''
            display_name = f"{name} - {short_name}" if short_name else name
            record.display_name = display_name
        return result
