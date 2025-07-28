# -*- coding: utf-8 -*-
from odoo import models, fields, api
class SignRequest(models.Model):
    _inherit = 'sign.template'

    project_id = fields.Many2one('project.project', string="Project")
