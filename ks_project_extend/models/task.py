from odoo.exceptions import UserError

from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = 'project.task'

    weather_ids = fields.One2many('project.task.weather', 'task_id', string="Weather Reports")
    ks_weather = fields.Selection(selection=[('bad', 'Bad'),('clear', 'Clear Skies')],string="Weather",default='clear',tracking=True)

    def action_fetch_weather(self):
        self.ensure_one()
        if not self.project_id.latitude or not self.project_id.longitude:
            raise UserError("Project has no latitude or longitude configured.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Fetch Weather',
            'res_model': 'project.weather.fetch.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
            },
        }
