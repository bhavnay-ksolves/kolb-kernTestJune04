# -*- coding: utf-8 -*-
"""
Extension of the Sale Order model to add functionality for downloading GAEB files.

This module defines methods for generating and downloading GAEB files in .x86 and .d86 formats.
It uses QWeb templates to render the file content and creates attachments for download.

Classes:
    SaleOrder: Extends the `sale.order` model to include GAEB file download functionality.

Attributes:
    ks_name (Char): Custom field added to the Sale Order model.

Methods:
    action_download_x86_file: Generates and downloads a GAEB .x86 file for the sale order.
    action_download_d86_file: Generates and downloads a GAEB .d86 file for the sale order.
"""

import base64
import logging
from datetime import datetime

from odoo.http import request

from odoo import models, fields, api, exceptions

_logger = logging.getLogger(__name__)
THUNDERSTORM_WEATHER_CODES = [95, 96, 97, 98, 99]


class SaleOrder(models.Model):
    """
    Extension of the Sale Order model to add GAEB file download functionality.
    """
    _inherit = 'sale.order'

    # Custom field added to the Sale Order model
    ks_name = fields.Char()

    def action_download_x86_file(self):
        """
        Generates and downloads a GAEB .x86 file for the sale order.

        This method renders a QWeb template to generate the XML content of the .x86 file,
        creates an attachment for the file, and returns an action to download it.

        Returns:
            dict: Action to download the generated .x86 file.
        """
        self.ensure_one()
        now = datetime.now()

        # Render QWeb template
        values = {
            'order': self,
            'date': now.strftime('%Y-%m-%d'),
            'time': now.strftime('%H:%M:%S'),
        }
        xml_body = request.env['ir.ui.view']._render_template('ks_gaeb.x86_sale_order_template', values)

        # Prepend the XML declaration manually
        full_xml = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_body}'

        # Create attachment for download
        filename = f"{self.name}.x86"
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

    def action_download_d86_file(self):
        """
        Generates and downloads a GAEB .d86 file for the sale order.

        This method renders a QWeb template to generate the text content of the .d86 file,
        creates an attachment for the file, and returns an action to download it.

        Returns:
            dict: Action to download the generated .d86 file.
        """
        self.ensure_one()

        currency = self.currency_id.name if self.currency_id else 'EUR'

        rendered_text = request.env['ir.ui.view']._render_template(
            'ks_gaeb.gaeb_d86_sale_template',
            {
                'order': self,
                'currency': currency,
            }
        )

        # Rendered text is a list of strings joined by newlines
        content = rendered_text.strip()

        filename = f"{self.name}.d86"
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
