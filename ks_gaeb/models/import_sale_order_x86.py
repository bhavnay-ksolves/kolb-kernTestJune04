# -*- coding: utf-8 -*-

import base64
import os
import re

from lxml import etree
from odoo.exceptions import UserError

from odoo import models, fields, api


class GaebImporter(models.TransientModel):
    _name = 'gaeb.importer'
    _description = 'GAEB File Importer'

    gaeb_file = fields.Binary("GAEB File", required=True)
    filename = fields.Char("Filename")
    file_type = fields.Selection([
        ('x83', 'GAEB (.x83)'),
        ('d83', 'GAEB (.d83)'),
    ], string="File Type", default='x83', required=True)

    def _create_efb_line(self, item, desc_lines, efb_model, chatter_lines):
        uom = self.env['uom.uom'].sudo().search([('name', 'ilike', item['unit'])], limit=1)
        if not uom:
            raise UserError(f"UoM not found for: {item['unit']}")

        desc = desc_lines[0] if desc_lines else "No description"
        long_desc = "\n".join(desc_lines)

        efb_model.create({
            'order_id': self.env[self._context['active_model']].browse(self._context['active_id']).id,
            'description': desc,
            'long_desc': long_desc,
            'product_uom_qty': item['qty'],
            'product_uom': uom.id,
            'price_unit': item['price'],
        })

        chatter_lines.append(
            f"{desc} — Qty: {item['qty']}, Unit: {item['unit']}, Price: {item['price']}"
        )

    def _import_x86(self):
        try:
            content = base64.b64decode(self.gaeb_file)
            tree = etree.fromstring(content)
        except Exception as e:
            raise UserError(f"Invalid XML file: {e}")

        ns = {'g': 'http://www.gaeb.de/GAEB_DA_XML/DA83/3.2'}
        items = tree.xpath('//g:Item', namespaces=ns)
        if not items:
            raise UserError("No <Item> elements found in GAEB file.")

        efb_model = self.env['offer.efb']
        chatter_lines = []

        for item in items:
            qty = float(item.findtext('g:Qty', namespaces=ns) or 0.0)
            unit = item.findtext('g:QU', namespaces=ns) or False
            uom = self.env['uom.uom'].sudo().search([('name', 'ilike', unit)], limit=1)

            if not uom:
                raise UserError(f"UoM not found for symbol: {unit}")

            desc_nodes = item.xpath('.//g:Description//g:CompleteText//g:OutlineText//g:OutlTxt//g:TextOutlTxt//g:span',
                                    namespaces=ns)
            desc = " ".join(span.text.strip() for span in desc_nodes if span.text)

            span_nodes = item.xpath('.//g:Description//g:CompleteText//g:DetailTxt//g:Text//g:span', namespaces=ns)
            full_description = " ".join(span.text.strip() for span in span_nodes if span.text)

            efb_model.create({
                'order_id': self.env[self._context['active_model']].browse(self._context['active_id']).id,
                'description': desc or 'No description',
                'long_desc': full_description or 'No description',
                'product_uom_qty': qty,
                'product_uom': uom.id,
            })

            chatter_lines.append(f"{desc or 'No name'} — Qty: {qty}, Unit: {unit}")

        if chatter_lines:
            self.env.user.partner_id.message_post(
                body="<pre>GAEB (.x86) Import:\n" + "\n".join(chatter_lines) + "</pre>",
                subtype_xmlid="mail.mt_note"
            )

    def _import_d86(self):
        content = base64.b64decode(self.gaeb_file)
        lines = content.decode("utf-8", errors="ignore").splitlines()

        efb_model = self.env["offer.efb"]
        chatter_lines = []

        current_item = {}
        description_lines = []

        processing = False  # Flag to start parsing only after 111
        for line in lines:
            code = line[:2]

            # Start processing only after '111' code appears
            if not processing:
                if line[:3] == "111":
                    processing = True
                continue

            if code == "21":
                item_number = line[2:7].strip()
                raw_qty_unit = line[30:43].strip()

                match = re.match(r"(\d+)([A-Za-z]+)", raw_qty_unit)
                if match:
                    qty = int(match.group(1)) / 1000
                    unit = match.group(2)
                else:
                    qty = 0.0
                    unit = ""

                current_item = {
                    "item_number": item_number,
                    "qty": qty,
                    "unit": unit,
                    "price": 0.0,
                    "total": 0.0,
                }

            elif code == "23" and current_item:
                price_str = line[22:34].strip()
                total_str = line[36:48].strip()

                try:
                    current_item["price"] = float(price_str) / 100
                except:
                    current_item["price"] = 0.0
                try:
                    current_item["total"] = float(total_str) / 100
                except:
                    current_item["total"] = 0.0

            elif code == "26":
                # Note: first character was missing due to incorrect slice (fixed now)
                text = line[5:70].strip()
                if text:
                    description_lines.append(text)

            elif code == "25":
                if current_item:
                    self._create_efb_line(current_item, description_lines, efb_model, chatter_lines)
                    current_item = {}
                    description_lines = []

        # In case file doesn't end with '25' but has pending item
        if current_item:
            self._create_efb_line(current_item, description_lines, efb_model, chatter_lines)

        # Post import summary to chatter
        if chatter_lines:
            self.env.user.partner_id.message_post(
                body="<pre>GAEB (.d83) Import:\n" + "\n".join(chatter_lines) + "</pre>",
                subtype_xmlid="mail.mt_note"
            )

    def action_import_file(self):
        if not self.gaeb_file or not self.filename:
            raise UserError("Please upload a GAEB file.")

        ext = os.path.splitext(self.filename)[1].lower()

        if self.file_type == 'x83':
            if ext != '.x83':
                raise UserError("Selected file type is .x83 but uploaded file is not .x83.")
            self._import_x86()

        elif self.file_type == 'd83':
            if ext != '.d83':
                raise UserError("Selected file type is .d83 but uploaded file is not .d83.")
            self._import_d86()
        else:
            raise UserError("Unsupported file type.")
