# -*- coding: utf-8 -*-
from odoo import models, fields,api
from datetime import datetime

class RiskAssessment(models.Model):
    _name = 'risk.assessment'
    _description = 'Risk Assessment'
    _rec_name = 'project_id'

    danger = fields.Many2one('risk.assessment.template', string="Danger", required=True)
    threat_measures = fields.Text(string="Measures against the threat")
    implementation = fields.Text(string="Implementation of the measures")
    review = fields.Text(string="Review of implementation")
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

