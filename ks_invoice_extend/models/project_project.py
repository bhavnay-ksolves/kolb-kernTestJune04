# -*- coding: utf-8 -*-
from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _prepare_invoice(self):
        """
        Prepare invoice values with additional project_id field.

        Returns:
            dict: Updated invoice values including project_id.
        """
        values = super()._prepare_invoice()
        values.update({
            'project_id': self.project_id.id
        })
        return values

class ProjectProject(models.Model):
    _inherit = 'project.project'

    def print_kolb_kern_invoices(self):
        return self.env.ref('ks_invoice_extend.action_kolb_kern_invoice_pdf').report_action(self)
