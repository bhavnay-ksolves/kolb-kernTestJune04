# -*- coding: utf-8 -*-

from odoo.tools import get_timedelta

from odoo import api, fields, models, _


class SaleOrderTemplateLine(models.Model):
    _inherit = 'sale.order.template.line'

    ks_pos = fields.Float(string="POS")

    @api.model_create_multi
    def create(self, vals):
        # Auto-assign sequence if not provided and parent is known
        if not vals[0].get('ks_pos') and vals[0].get('sale_order_template_id'):
            parent = self.env['sale.order.template'].browse(vals[0].get('sale_order_template_id'))
            if parent.exists():
                existing_sequences = parent.sale_order_template_line_ids.mapped('ks_pos')
                vals[0]['ks_pos'] = max(existing_sequences or [0.0]) + 1.0
            else:
                vals[0]['ks_pos'] = 1.0
        elif not vals[0].get('ks_pos'):
            # Fallback if no parent
            vals[0]['ks_pos'] = 1.0

        return super(SaleOrderTemplateLine, self).create(vals)
