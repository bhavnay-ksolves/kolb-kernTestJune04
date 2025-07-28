# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
from odoo.exceptions import UserError


class DailyConstructionReport(models.Model):
    _name = 'daily.construction.report'
    _description = 'Daily Construction Report'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', string="Project", required=True)
    site_location = fields.Char(string="Site Location",required=True,tracking=True)
    attendance = fields.Char(string="Attendance (number,function,duration)",required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    weather = fields.Float(string="Weather",required=True)

    company_id = fields.Many2one(
        'res.company', string="Company",
        related='project_id.company_id',required=True
    )
    # Stage field
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Status', default='new', tracking=True)

    # Execution Tab
    description = fields.Text(string="Description of the work carried out and the progress", required=True)
    machine = fields.Text(string="Machine devices")
    areas_worked_on = fields.Text(string="Areas worked on")
    delivery = fields.Text(string="Consumed materials/delivery")

    # Incidents Tab
    incidents = fields.Html(string="Incidents")
    images_ids = fields.One2many('daily.construction.report.image', 'report_id', string="Images")
    incidents_image = fields.One2many('ir.attachment', 'res_id', string="Incident Images")
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
        """Generate PDF report for Execution, Incidents, and Release Grant."""
        return self.env.ref('ks_project_extend.action_daily_construction_pdf').report_action(self)

    def action_send_esignature_report(self):
        """This functions will redirect the page to sign the customer on daily construction report"""
        self.ensure_one()

        # Get the report and render PDF
        report = self.env['ir.actions.report']._get_report_from_name(
            'ks_project_extend.report_daily_construction')
        if not report:
            raise UserError("Daily Construction Report not found.")

        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'ks_project_extend.report_daily_construction', self.id
        )

        # Create PDF attachment
        attachment = self.env['ir.attachment'].create({
            'name': f"Daily_Construction_Report_{self.project_id.name or self.id}.pdf",
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        # Create new template from attachment
        sign_template = self.env['sign.template'].create({
            'attachment_id': attachment.id,
            'name': f"Daily Construction Template - {self.project_id.name or self.id}",
            'project_id': self.project_id.id,
        })
        return {
            "type": "ir.actions.client",
            "tag": "sign.Template",
            "name": f"Template {attachment.name}",
            "target": "current",
            "params": {
                "sign_edit_call": "sign_send_request",  # this can be True or custom context
                "id": sign_template.id,
                "sign_directly_without_mail": False,
                "resModel": self._name,
            },
        }

class DailyConstructionReportImage(models.Model):
    _name = 'daily.construction.report.image'
    _description = 'Daily Construction Report Image'

    name = fields.Char('Name', required=True)
    report_id = fields.Many2one('daily.construction.report', required=True)
    image = fields.Binary('Image')





