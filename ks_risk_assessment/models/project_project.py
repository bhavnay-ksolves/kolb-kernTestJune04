# -*- coding: utf-8 -*-
from odoo import models, fields,api
from datetime import datetime
import base64
from odoo.exceptions import UserError

class RiskAssessment(models.Model):
    _name = 'risk.assessment'
    _description = 'Risk Assessment'
    _rec_name = 'project_id'

    danger = fields.Many2one('risk.assessment.template', string="Danger", required=True)
    threat_measures = fields.Text(string="Measures against the threat",store=True)
    implementation = fields.Text(string="Implementation of the measures",store=True)
    review = fields.Text(string="Review of implementation",store=True)
    project_id = fields.Many2one('project.project', string="Project")

    @api.onchange('danger')
    def _onchange_danger(self):
        """Updates related fields when the danger field is changed.
        Sets threat_measures, implementation, and review based on the selected danger.
        """
        if self.danger:
            self.threat_measures = self.danger.threat_measures
            self.implementation = self.danger.implementation
            self.review = self.danger.review

class ProjectTask(models.Model):
    _inherit = 'project.project'

    date_report_creation = fields.Datetime(string='Date of Creating Risk Assessment Report')

    risk_assessment_ids = fields.One2many(
        'risk.assessment',
        'project_id',
        string='Risk Assessments'
    )


    def action_report(self):
        """Generates the risk assessment PDF and sets the report creation date."""
        self.write({'date_report_creation': datetime.now()})
        return self.env.ref(
            'ks_risk_assessment.action_risk_assessment_pdf'
        ).report_action(self)

    def action_send_esignature(self):
        self.ensure_one()

        # Check that partner has email
        if not self.partner_id or not self.partner_id.email:
            raise UserError("Customer must have an email address to send e-signature request.")

        # Get the report and render PDF
        report = self.env['ir.actions.report']._get_report_from_name(
            'ks_risk_assessment.report_risk_assessment_document')
        if not report:
            raise UserError("Risk report not found.")

        pdf_content, _ = self.env['ir.actions.report']._render_qweb_pdf(
            'ks_risk_assessment.report_risk_assessment_document', self.id
        )

        # Create PDF attachment
        attachment = self.env['ir.attachment'].create({
            'name': f"Risk_Assessment_{self.name or self.id}.pdf",
            'type': 'binary',
            'datas': base64.b64encode(pdf_content),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/pdf',
        })

        # Create new template from attachment
        sign_template = self.env['sign.template'].create({
            'attachment_id': attachment.id,
            'name': f"Risk Assessment Template - {self.name or self.id}",
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
