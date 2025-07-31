# -*- coding: utf-8 -*-
from odoo import models, fields, api
import base64
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError
import magic

class DailyConstructionReport(models.Model):
    _name = 'daily.construction.report'
    _description = 'Daily Construction Report'
    _inherit = ['mail.thread','mail.activity.mixin']
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', string="Project", required=True)
    site_location = fields.Text(string="Site Location",required=True,tracking=True)
    attendance = fields.Char(string="Attendance (number,function,duration)",required=True)
    date = fields.Date(string="Date", default=fields.Date.context_today)
    temperature = fields.Float(string="Temperature")
    weather = fields.Char(string="Weather")

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
    description = fields.Text(string="Description of the work carried out and the progress")
    machine = fields.Text(string="Machine devices")
    areas_worked_on = fields.Text(string="Areas worked on")
    delivery = fields.Text(string="Consumed materials/delivery")

    # Incidents Tab
    changes_in_benefits = fields.Text(
        string="Changes in Benefits"
    )
    disabilities_difficulties = fields.Text(
        string="Disabilities / Difficulties"
    )
    special_incidents = fields.Text(
        string="Special Incidents"
    )
    # Sign Off Tab
    responsible = fields.Many2many(related='project_id.responsible', readonly=True)
    supervisor_signature = fields.Binary(string="Supervisor Signature")
    signoff_attachment = fields.One2many(
        'ir.attachment',
        'res_id',
        string="Sign-Off PDFs",
        domain=lambda self: [('res_model', '=', 'daily.construction.report'), ('mimetype', '=', 'application/pdf')]
    )
    approval_comment = fields.Text(string="Approval/Rejection Comment")
    incidents_image = fields.One2many(
        'ir.attachment',
        'res_id',
        string="Incident Images",
        domain=lambda self: [
            ('res_model', '=', 'daily.construction.report'),
            ('mimetype', 'in', ['image/jpeg', 'image/png'])
        ]
    )

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

    @api.constrains('incidents_image')
    def _check_image_file(self):
        """
        Validate that uploaded incident images are either JPEG or PNG files.
        Skips validation if no images are uploaded.
        """
        allowed_mime_types = ['image/jpeg', 'image/png']  # Allowed image formats
        for record in self:
            # If no file is uploaded, skip validation
            if not record.incidents_image:
                continue

            for attachment in record.incidents_image:
                # If file exists, validate it
                if attachment.datas:
                    file_data = base64.b64decode(attachment.datas)
                    mime_type = magic.from_buffer(file_data, mime=True)

                    if mime_type not in allowed_mime_types:
                        raise ValidationError("Only JPEG or PNG image files are allowed.")

    @api.constrains('signoff_attachment')
    def _check_signoff_attachment_pdf(self):
        """
        Validate that all sign-off attachments are PDF files.
        Skips validation if no files are uploaded.
        """
        for record in self:
            if not record.signoff_attachment:
                continue  # No files uploaded, skip

            for attachment in record.signoff_attachment:
                if attachment.datas:  # Ensure attachment has data
                    file_data = base64.b64decode(attachment.datas)
                    mime_type = magic.from_buffer(file_data, mime=True)

                    if mime_type != 'application/pdf':
                        raise ValidationError("Only PDF files are allowed for sign-off attachment.")


    def _validate_execution_fields(self):
        """
        Shared validation logic for required execution fields.
        """
        for record in self:
            missing = []
            if not record.weather:
                missing.append("Weather")
            if not record.temperature:
                missing.append("Temperature")
            if not record.description:
                missing.append("Description")
            if not record.machine:
                missing.append("Machine Devices")
            if not record.areas_worked_on:
                missing.append("Areas Worked On")
            if not record.delivery:
                missing.append("Consumed Materials/Delivery")
            if not record.changes_in_benefits:
                missing.append("Changes in Benefits")
            if not record.special_incidents:
                missing.append("Special Incidents")
            if not record.disabilities_difficulties:
                missing.append("Disabilities/Difficulties")
            if not record.project_id.responsible:
                missing.append("Responsible (set in Project)")

            if missing:
                raise ValidationError(
                    "Cannot proceed. Missing fields: %s" % ", ".join(missing)
                )

    def action_start_progress(self):
        """
        Move report to 'in_progress' stage with validation.
        """
        self._validate_execution_fields()
        self.write({'state': 'in_progress'})
        self.message_post(body="Report is now In Progress.")

    def action_approve(self):
        """
        Approve the daily report — requires supervisor signature and log to chatter.
        """
        for record in self:
            if not record.supervisor_signature:
                raise ValidationError("Please upload Supervisor Signature before approving.")

            # Change state
            record.write({'state': 'approved'})

            # Post message in chatter
            record.message_post(body="Report has been approved.")

    def action_reject(self):
        """
        Reject the daily report — requires supervisor signature and log to chatter.
        """
        for record in self:
            if not record.supervisor_signature:
                raise ValidationError("Please upload Supervisor Signature before rejecting.")

            # Change state
            record.write({'state': 'rejected'})

            # Immediately set it back to draft (new)
            record.state = 'new'
            # Post message in chatter
            record.message_post(body="Report moved back to draft after rejection.")

    def action_submit(self):
        """
        Submit report for approval with same validation.
        """
        self._validate_execution_fields()
        self.write({'state': 'submitted'})
        self.message_post(body="Report has been Submitted for Approval.")

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

        tag = self.env['sign.template.tag'].search([('name', '=', 'Daily Construction Report')], limit=1)
        # Create new template from attachment
        sign_template = self.env['sign.template'].create({
            'attachment_id': attachment.id,
            'name': f"Daily Construction Template - {self.project_id.name or self.id}",
            'project_id': self.project_id.id,
            'tag_ids': [(6, 0, [tag.id])] if tag else [],
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

# For image
# class DailyConstructionReportImage(models.Model):
#     _name = 'daily.construction.report.image'
#     _description = 'Daily Construction Report Image'
#
#     name = fields.Char('Name', required=True)
#     report_id = fields.Many2one('daily.construction.report', required=True)
#     image = fields.Binary('Image')





