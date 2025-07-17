from odoo import models, fields,api,_

class ProjectProject(models.Model):
    _inherit = 'project.project'

    measurement_ids = fields.One2many(comodel_name='measurement.calculation',
                                      inverse_name='order_id', string="Measurement Calculation")
    measurement_count = fields.Integer(string="Measurement Cals",
                                       compute='measurement_calculation_count',
                                       default=0)

    def measurement_calculation_count(self):
        """Get count of Measurement Calculations."""
        for rec in self:
            rec.measurement_count = self.env['measurement.calculation'].search_count([
                ('project_id', '=', self.id)])

    def action_get_measurement_calculation_record(self):
        """To call Measurement Calculation tree view."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Measurement Calculations"),
            'view_mode': 'list,form',
            'res_model': 'measurement.calculation',
            'context': "{'default_order_id': active_id}",
            'domain': [('project_id', '=', self.id)],
        }
