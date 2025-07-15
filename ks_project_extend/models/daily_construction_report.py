from odoo import models, fields, api
from datetime import date

class DailyConstructionReport(models.Model):
    _name = 'daily.construction.report'
    _description = 'Daily Construction Report'

    project_id = fields.Many2one('project.project', string="Project", required=True)
    site_location = fields.Text(string="Site Location")
    attendance = fields.Text(string="Attendance")
    date = fields.Date(string="Date", default=fields.Date.context_today)
    weather = fields.Float(string="Weather")

    # Execution Tab
    description = fields.Char(string="Description")
    machine = fields.Char(string="Machine")
    delivery = fields.Char(string="Delivery")

    # Incidents Tab
    incidents = fields.Text(string="Incidents")
    incident_attachment = fields.Binary(string="Incident Attachment")

    # Sign Off Tab
    responsible = fields.Many2many(related='project_id.responsible', readonly=True)
    supervisor_signature = fields.Binary(string="Supervisor Signature")
    client_signature = fields.Binary(string="Client Signature")
    signoff_attachment = fields.Binary(string="Sign-Off Attachment")
