# -*- coding: utf-8 -*-
from odoo import models, fields,api
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = 'project.project'
    assigned_employees = fields.Many2many(
        'hr.employee',
        'project_assigned_employee_rel',
        'project_id',
        'employee_id',
        string="Assigned Employees",
        tracking=True,
    )

    responsible = fields.Many2many(
        'hr.employee',
        'project_responsible_employee_rel',
        'project_id',
        'employee_id',
        string="Responsible",
        tracking=True,
    )

    customer_address = fields.Text(string="Customer Address / Construction Address",tracking=True)
    date_start = fields.Datetime(string='Start Date',tracking=True)
    art_type = fields.Selection(selection=[('fixed', 'Fixed'),('temporary', 'Temporary')],string="Art Type",
                                required=True,tracking=True)
    work_order_description = fields.Char(string="Work Order Description",tracking=True)
    type_of_work_id = fields.Many2one('type.of.work', string="Type of Work",tracking=True,store=True)
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    company_id = fields.Many2one('res.company', string='Company', compute="_compute_company_id",
                                 inverse="_inverse_company_id", store=True, readonly=False,
                                 default=lambda self: self.env.company)

    daily_construction_report_ids = fields.One2many(
        'daily.construction.report',
        'project_id',
        string='Daily Construction Reports'
    )
    weather_ids = fields.One2many('project.project.weather', 'project_id', string="Weather Reports")

    @api.model
    def create(self, vals):
        """Overrides create to sync task user_ids after project creation."""
        project = super().create(vals)
        project._sync_task_user_ids()
        return project

    def write(self, vals):
        """Overrides write to sync task user_ids when user or responsible changes."""
        res = super().write(vals)
        if 'user_id' in vals or 'responsible' in vals:
            self._sync_task_user_ids()
        return res

    def _sync_task_user_ids(self):
        """Syncs user_ids of all tasks with project's user_id and responsible users."""
        for project in self:
            user_ids = []
            if project.user_id:
                user_ids.append(project.user_id.id)
            if project.responsible:
                user_ids += project.responsible.ids

            # Update user_ids on all related tasks
            project.task_ids.write({
                'user_ids': [(6, 0, user_ids)]
            })

    def action_fetch_weather(self):
        self.ensure_one()
        if not self.latitude or not self.longitude:
            raise UserError("Project has no latitude or longitude configured.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Fetch Weather',
            'res_model': 'project.weather.fetch.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_task_id': self.id,
            },
        }