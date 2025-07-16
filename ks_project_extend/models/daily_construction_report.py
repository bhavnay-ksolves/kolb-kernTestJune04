from odoo import models, fields, api
from datetime import date

class DailyConstructionReport(models.Model):
    _name = 'daily.construction.report'
    _description = 'Daily Construction Report'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', string="Project", required=True)
    site_location = fields.Char(string="Site Location")
    attendance = fields.Char(string="Attendance")
    date = fields.Date(string="Date", default=fields.Date.context_today)
    weather = fields.Float(string="Weather")

    # Stage field
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='new', tracking=True)

    # Execution Tab
    description = fields.Char(string="Description")
    machine = fields.Char(string="Machine")
    delivery = fields.Char(string="Delivery")

    # Incidents Tab
    incidents = fields.Char(string="Incidents")
    incident_1 = fields.Char(string="Incidents")
    incident_2 = fields.Char(string="Incidents")
    incident_3 = fields.Char(string="Incidents")
    incident_4 = fields.Char(string="Incidents")
    incident_5 = fields.Char(string="Incidents")
    incident_attachment = fields.Binary(string="Incident Attachment")

    # Sign Off Tab
    responsible = fields.Many2many(related='project_id.responsible', readonly=True)
    supervisor_signature = fields.Binary(string="Supervisor Signature")
    client_signature = fields.Binary(string="Client Signature")
    signoff_attachment = fields.Binary(string="Sign-Off Attachment")

    approval_comment = fields.Text(string="Approval/Rejection Comment")

    def open_approval_comment_wizard(self):
        """Opens the wizard to add an approval comment."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Add Comment',
            'res_model': 'daily.construction.comment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_action_type': self.env.context.get('action_type'),
                'default_report_id': self.id,
            },
        }

    def action_start_progress(self):
        """Marks the report as in progress and posts a message."""
        for rec in self:
            rec.state = 'in_progress'
            rec.message_post(body="Report is in progress")

    def action_approve(self):
        """Approves the report and posts a message."""
        for rec in self:
            rec.state = 'approved'
            rec.message_post(body="Report has been approved.")

    def action_reject(self):
        """Rejects the report, resets it to draft, and posts messages."""
        for rec in self:
            rec.state = 'rejected'
            rec.message_post(body="Report has been rejected.")

            # Immediately set it back to draft (new)
            rec.state = 'new'
            rec.message_post(body="Report moved back to draft after rejection.")

    def action_submit(self):
        """Submits the report and posts a message."""
        for rec in self:
            rec.state = 'submitted'
            rec.message_post(body="Report has been submitted.")

    def daily_construction_report(self):
        """Generate PDF report for Execution, Incidents, and Sign Off."""
        return self.env.ref('ks_project_extend.action_daily_construction_pdf').report_action(self)



