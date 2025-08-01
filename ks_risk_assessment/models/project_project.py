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

    def action_open_risk_report_wizard(self):
        """
        Opens the risk report wizard for the current project.

        This method returns an action dictionary that opens a form view of the
        `risk.report.wizard` model. The wizard is used to generate or manage
        risk reports for the project.

        Returns:
            dict: An action dictionary containing the type, model, view mode,
            target, and context for opening the wizard.
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'risk.report.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id}
        }

    def print_instruction_report(self):
        return self.env.ref('ks_risk_assessment.action_instruction_report_pdf').report_action(self)
