# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from odoo.http import request
import base64
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def action_download_x81_file_po(self):
        self.ensure_one()
        now = datetime.now()

        # Render QWeb template
        values = {
            'order': self,
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
        }
        xml_body = request.env['ir.ui.view']._render_template(
            'ks_gaeb.x81_purchase_order_template', values
        )

        # Prepend the XML declaration manually
        full_xml = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_body}'

        # Create attachment for download
        filename = f"{self.name}.x81"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(full_xml.encode('utf-8')),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'application/octet-stream',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_download_d81_file_po(self):
        self.ensure_one()

        currency = self.currency_id.name if self.currency_id else 'EUR'

        rendered_text = request.env['ir.ui.view']._render_template(
            'ks_gaeb.gaeb_d81_purchase_template',
            {
                'order': self,
                'currency': currency,
            }
        )

        # Rendered text is a list of strings joined by newlines
        content = rendered_text.strip()

        filename = f"{self.name}.d81"
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'type': 'binary',
            'datas': base64.b64encode(content.encode('utf-8')),
            'res_model': self._name,
            'res_id': self.id,
            'mimetype': 'text/plain',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }
