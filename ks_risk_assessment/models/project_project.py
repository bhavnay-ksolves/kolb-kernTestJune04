# -*- coding: utf-8 -*-
"""
Module for Risk Assessment and Project Task Extensions.

This module defines models for managing risk assessments and extends the `project.project` model
to include functionality for generating risk assessment reports and sending e-signature requests.

Classes:
    RiskAssessment: Represents a risk assessment associated with a project.
    ProjectTask: Extends the `project.project` model to include risk assessment functionality.

Attributes:
    RiskAssessment:
        danger (Many2one): Reference to the risk assessment template.
        threat_measures (Text): Measures against the identified threat.
        implementation (Text): Implementation details of the measures.
        review (Text): Review of the implementation.
        project_id (Many2one): Reference to the associated project.
        company_id (Many2one): Reference to the company, related to the project.

    ProjectTask:
        date_report_creation (Datetime): Timestamp for the creation of the risk assessment report.
        risk_assessment_ids (One2many): List of risk assessments associated with the project.

Methods:
    RiskAssessment:
        _onchange_danger: Updates related fields when the danger field is changed.

    ProjectTask:
        action_report: Generates the risk assessment PDF and sets the report creation date.
        action_send_esignature: Sends an e-signature request for the risk assessment report.
"""

from odoo import models, fields, api
from datetime import datetime
import base64
from odoo.exceptions import UserError


class RiskAssessment(models.Model):
    """
    Represents a risk assessment associated with a project.

    This model includes fields for identifying dangers, measures against threats, implementation details,
    and reviews. It is linked to a specific project and company.
    """
    _name = 'risk.assessment'
    _description = 'Risk Assessment'
    _rec_name = 'project_id'

    # Reference to the risk assessment template
    danger = fields.Many2one('risk.assessment.template', string="Danger", required=True)
    # Measures against the identified threat
    threat_measures = fields.Text(string="Measures against the threat", store=True)
    # Implementation details of the measures
    implementation = fields.Text(string="Implementation of the measures", store=True)
    # Review of the implementation
    review = fields.Text(string="Review of implementation", store=True)
    # Reference to the associated project
    project_id = fields.Many2one('project.project', string="Project")
    # Reference to the company, related to the project
    company_id = fields.Many2one(
        'res.company', string="Company", related='project_id.company_id', readonly=True
    )

    @api.onchange('danger')
    def _onchange_danger(self):
        """
        Updates related fields when the danger field is changed.

        Sets the `threat_measures`, `implementation`, and `review` fields based on the selected danger.
        """
        if self.danger:
            self.threat_measures = self.danger.threat_measures
            self.implementation = self.danger.implementation
            self.review = self.danger.review


class ProjectProject(models.Model):
    """
    Extends the `project.project` model to include risk assessment functionality.

    This model adds fields and methods for managing risk assessments, generating reports,
    and sending e-signature requests.
    """
    _inherit = 'project.project'

    # Timestamp for the creation of the risk assessment report
    date_report_creation = fields.Datetime(string='Date of Creating Risk Assessment Report')
    # List of risk assessments associated with the project
    risk_assessment_ids = fields.One2many(
        'risk.assessment',
        'project_id',
        string='Risk Assessments'
    )
    sign_request_ids = fields.One2many(
        'sign.template',
        'project_id',
        string='Sign Reports'
    )

    def action_report(self):
        """
        Generates the risk assessment PDF and sets the report creation date.

        Returns:
            dict: Action to generate and download the risk assessment report.
        """
        self.write({'date_report_creation': datetime.now()})
        return self.env.ref(
            'ks_risk_assessment.action_risk_assessment_pdf'
        ).report_action(self)

    def action_send_esignature(self):
        """
        Sends an e-signature request for the risk assessment report.

        Raises:
            UserError: If the customer does not have an email address or the report is not found.

        Returns:
            dict: Action to send the e-signature request.
        """
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
        tag = self.env['sign.template.tag'].search([('name', '=', 'Risk Assessment Report')], limit=1)
        # Create new template from attachment
        sign_template = self.env['sign.template'].create({
            'attachment_id': attachment.id,
            'name': f"Risk Assessment Template - {self.name or self.id}",
            'project_id': self.id,
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
