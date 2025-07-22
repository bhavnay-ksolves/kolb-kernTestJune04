# -*- coding: utf-8 -*-
from odoo import models, fields


class TypeOfWork(models.Model):
    _name = 'type.of.work'
    _description = 'Type of Work'

    name = fields.Char(string='Type of Work', required=True)