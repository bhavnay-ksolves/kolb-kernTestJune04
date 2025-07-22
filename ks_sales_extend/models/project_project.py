from odoo import models, fields, api, _


class ProjectProject(models.Model):
    """
    Extension of the Project model to include measurement calculations.

    This model adds functionality to manage and interact with measurement calculations
    associated with projects. It includes fields for storing related measurement records
    and methods for counting and accessing these records.
    """
    _inherit = 'project.project'  # Inherits from the base 'project.project' model.

    # One2many relation to measurement calculations associated with the project.
    measurement_ids = fields.One2many(
        comodel_name='measurement.calculation',
        inverse_name='order_id',
        string="Measurement Calculation"
    )

    # Integer field to store the count of measurement calculations, computed dynamically.
    measurement_count = fields.Integer(
        string="Measurement Cals",
        compute='measurement_calculation_count',
        default=0
    )

    def measurement_calculation_count(self):
        """
        Compute the count of measurement calculations associated with the project.

        This method searches for measurement calculations linked to the current project
        and updates the `measurement_count` field with the result.
        """
        for rec in self:
            rec.measurement_count = self.env['measurement.calculation'].search_count([
                ('project_id', '=', self.id)
            ])

    def action_get_measurement_calculation_record(self):
        """
        Open the Measurement Calculation tree view filtered by the current project.

        Returns:
            dict: Action dictionary to open the Measurement Calculation tree view.
        """
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Measurement Calculations"),
            'view_mode': 'list,form',
            'res_model': 'measurement.calculation',
            'context': "{'default_order_id': active_id}",
            'domain': [('project_id', '=', self.id)],
        }
