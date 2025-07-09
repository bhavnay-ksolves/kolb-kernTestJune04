# -*- coding: utf-8 -*-
from odoo import models, fields

class RiskAssessment(models.Model):
    _name = 'risk.assessment'
    _description = 'Risk Assessment'

    risk = fields.Text(string="Risk")
    threat_measures = fields.Text(string="Measures Against the Threat")
    implementation = fields.Text(string="Implementation of the Measures")
    review = fields.Text(string="Review of Implementation")
    project_id = fields.Many2one('project.task', string="Project")

class ProjectTask(models.Model):
    _inherit = 'project.task'

    # comment

    risk_assessment_ids = fields.One2many(
        'risk.assessment',
        'project_id',
        string='Risk Assessments'
    )

