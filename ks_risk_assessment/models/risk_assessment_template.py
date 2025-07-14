# -*- coding: utf-8 -*-
from odoo import models, fields

class RiskAssessmentTemplate(models.Model):
    _name = 'risk.assessment.template'
    _description = 'Risk Assessment Template'

    name = fields.Char(string="Risk Type", required=True)
    threat_measures = fields.Text(string="Measures against the threat")
    implementation = fields.Text(string="Implementation of the measures")
    review = fields.Text(string="Review of implementation")
    project_id = fields.Many2one('project.project', string="Project")
