from odoo import models, fields


class ProjectWeather(models.Model):
    _name = 'project.project.weather'
    _description = 'Project Weather Report'

    project_id = fields.Many2one('project.project', string="Project")
    report_date = fields.Date(string="Date")
    temp_min = fields.Float(string="Min Temp(°C)")
    temp_max = fields.Float(string="Temperature maximum (°C)")
    humidity = fields.Float(string="Humidity")
    conditions = fields.Char(string="Weather Condition")
    # wind_speed = fields.Float(string="Wind Speed (km/h)")


class ProjectTaskWeather(models.Model):
    _name = 'project.task.weather'
    _description = 'Task Weather Report'

    task_id = fields.Many2one('project.task', string="Task")
    report_date = fields.Date(string="Date")
    temp_min = fields.Float(string="Min Temp(°C)")
    temp_max = fields.Float(string="Temperature maximum (°C)")
    humidity = fields.Float(string="Humidity")
    conditions = fields.Char(string="Weather Condition")
    # wind_speed = fields.Float(string="Wind Speed (km/h)")
