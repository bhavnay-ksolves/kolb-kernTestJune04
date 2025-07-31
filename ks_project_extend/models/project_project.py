# -*- coding: utf-8 -*-
from odoo import models, fields,api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class ProjectProject(models.Model):
    _inherit = 'project.project'
    assigned_employees = fields.Many2many(
        'hr.employee',
        string="Assigned Employees",
        tracking=True,
    )

    responsible = fields.Many2many(
        'res.users',
        string="Responsible",
        tracking=True,
    )

    customer_address = fields.Text(string="Customer Address / Construction Address",tracking=True)
    date_start = fields.Datetime(string='Start Date',tracking=True)
    art_type = fields.Selection(selection=[('fixed', 'Fixed'),('temporary', 'Temporary')],string="Art Type",
                                required=True,tracking=True)
    work_order_description = fields.Char(string="Work Order Description",tracking=True)
    type_of_work_id = fields.Many2one('type.of.work', string="Type of Work",tracking=True,store=True)
    # latitude = fields.Char(string="Latitude")
    # longitude = fields.Char(string="Longitude")
    company_id = fields.Many2one('res.company', string='Company', compute="_compute_company_id",
                                 inverse="_inverse_company_id", store=True, readonly=False,
                                 default=lambda self: self.env.company)

    daily_construction_report_ids = fields.One2many(
        'daily.construction.report',
        'project_id',
        string='Daily Construction Reports'
    )
    weather_ids = fields.One2many('project.project.weather', 'project_id', string="Weather Reports")

    # Define new fields to store the project's customer coordinates
    # These fields will be computed based on the linked partner_id's address.
    latitude = fields.Float(
        string='Project Latitude',
        digits=(10, 7),  # Standard precision for latitude/longitude
        help="The latitude of the project's customer address, automatically fetched.",
        compute='_compute_project_coordinates',  # This field is computed
        store=True,  # Store the computed value in the database for performance
        readonly=True,  # Prevent manual editing, as it's computed
    )
    longitude = fields.Float(
        string='Project Longitude',
        digits=(10, 7),  # Standard precision for latitude/longitude
        help="The longitude of the project's customer address, automatically fetched.",
        compute='_compute_project_coordinates',  # This field is computed
        store=True,  # Store the computed value in the database
        readonly=True,  # Prevent manual editing
    )

    @api.depends(
        'partner_id',  # Trigger computation if the customer is changed
        'partner_id.partner_latitude',  # Trigger if the customer's latitude changes
        'partner_id.partner_longitude',  # Trigger if the customer's longitude changes
        # Optionally, you can also depend on address fields if you want to re-compute
        # even if the partner's lat/lon are not yet populated but address changes.
        # However, it's generally assumed that partner.latitude/longitude will be
        # populated by Odoo's OOTB geolocalization or another mechanism.
        'partner_id.street',
        'partner_id.city',
        'partner_id.zip',
        'partner_id.state_id',
        'partner_id.country_id',
    )
    def _compute_project_coordinates(self):
        """
        Computes the project_latitude and project_longitude based on the
        latitude and longitude of the linked customer (partner_id).
        If the partner doesn't have coordinates, or no partner is linked,
        the project coordinates will be cleared.
        """
        for project in self:
            if project.partner_id and project.partner_id.partner_latitude is not None and project.partner_id.partner_longitude is not None:
                # If partner exists and has coordinates, copy them to the project
                project.latitude = project.partner_id.partner_latitude
                project.longitude = project.partner_id.partner_longitude
                _logger.info(
                    f"Project '{project.name}' coordinates updated from customer '{project.partner_id.display_name}': Lat={project.latitude}, Lng={project.longitude}")
            else:
                # If no partner, or partner has no coordinates, clear project coordinates
                project.latitude = False
                project.longitude = False
                if project.partner_id:
                    _logger.warning(
                        f"Customer '{project.partner_id.display_name}' for Project '{project.name}' does not have latitude/longitude. Clearing project coordinates.")
                else:
                    _logger.info(f"No customer linked to Project '{project.name}'. Clearing project coordinates.")

    @api.model
    def create(self, vals):
        """Overrides create to sync task user_ids after project creation."""
        project = super().create(vals)
        project._sync_task_user_ids()
        return project

    def write(self, vals):
        """Overrides write to sync task user_ids when user or responsible changes."""
        res = super().write(vals)
        if 'user_id' in vals or 'responsible' in vals or 'assigned_employees' in vals:
            self._sync_task_user_ids()
        return res

    def _sync_task_user_ids(self):
        """
        Sync user_ids on all tasks from:
        - responsible (res.users)
        - assigned_employees (hr.employee -> res.users)
        - site_manager (user_id)
        """
        for project in self:
            user_ids = set()

            # Add users from responsible (already res.users)
            if project.responsible:
                user_ids.update(project.responsible.ids)

            # Add users from assigned_employees (map employee -> user_id)
            if project.assigned_employees:
                user_ids.update(project.assigned_employees.mapped('user_id.id'))

            # Add site_manager (user_id on project)
            if project.user_id:
                user_ids.add(project.user_id.id)

            # Remove None (employees without user_id)
            user_ids.discard(False)

            # Update user_ids on related tasks
            project.task_ids.write({
                'user_ids': [(6, 0, list(user_ids))]
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