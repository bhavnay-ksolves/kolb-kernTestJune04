# -*- coding: utf-8 -*-

import base64
import os
from gaeb_parser import XmlGaebParser
import tempfile
# from xml.etree import ElementTree as ET
from lxml import etree
import re

from odoo.exceptions import UserError
from odoo import models, fields, api


class GaebImporter(models.TransientModel):
    _name = 'gaeb.importer'
    _description = 'GAEB File Importer'

    gaeb_file = fields.Binary("GAEB File", required=True)
    filename = fields.Char("Filename")

    def action_import_x83(self):
        if not self.gaeb_file or not self.filename:
            raise UserError("Please upload a GAEB file.")

        ext = os.path.splitext(self.filename)[1].lower()
        if ext != '.x83':
            raise UserError("Only .x83 (XML) GAEB files are supported in this version.")

        # Decode XML
        try:
            content = base64.b64decode(self.gaeb_file)
            tree = etree.fromstring(content)
        except Exception as e:
            raise UserError(f"Invalid XML file: {e}")

        # GAEB namespace
        ns = {'g': 'http://www.gaeb.de/GAEB_DA_XML/DA83/3.2'}

        items = tree.xpath('//g:Item', namespaces=ns)
        if not items:
            raise UserError("No <Item> elements found in GAEB file.")

        efb_model = self.env['offer.efb']
        # product_model = self.env['product.template']
        chatter_lines = []

        for item in items:
            qty = float(item.findtext('g:Qty', namespaces=ns) or 0.0)
            unit = item.findtext('g:QU', namespaces=ns) or False

            # 2. Match with uom.uom
            uom = self.env['uom.uom'].sudo().search([('name', 'ilike', unit)], limit=1)

            if not uom:
                raise UserError(f"UoM not found for symbol: {unit}")

            uom_id = uom.id

            desc_nodes = item.xpath('.//g:Description//g:CompleteText//g:OutlineText//g:OutlTxt//g:TextOutlTxt//g:span',
                                    namespaces=ns)
            desc = " ".join(span.text.strip() for span in desc_nodes if span.text)

            # Find all span elements under Description > CompleteText > DetailTxt > Text
            span_nodes = item.xpath('.//g:Description//g:CompleteText//g:DetailTxt//g:Text//g:span', namespaces=ns)

            # Merge and clean text
            full_description = " ".join(span.text.strip() for span in span_nodes if span.text)

            # # Search in English (en_US) context
            # product = product_model.with_context(lang='en_US').search([('name', 'ilike', desc)], limit=1)
            #
            # # fallback to base language if translation fails
            # if not product:
            #     # Search in German (de_DE) context
            #     product = product_model.with_context(lang='de_DE').search([('name', 'ilike', desc)], limit=1)
            #
            # if not product:
            #     print()

            # price_unit = product.list_price if product else 0.0
            # taxes = [(6, 0, product.taxes_id.ids)] if product and product.taxes_id else []

            # Create EFB line
            efb_model.create({
                # 'product_template_id': product.id if product else False,
                'order_id': self.env[self._context['active_model']].browse(self._context['active_id']).id,
                'description': desc or 'No description',
                'long_desc': full_description or 'No description',
                'product_uom_qty': qty,
                'product_uom': uom_id or False,
                # 'price_unit': price_unit,
                # 'tax_id': taxes,
            })

            chatter_lines.append(
                f"{desc or 'No name'} — Qty: {qty}, Unit: {unit}"
            )

        # Post to chatter (on user’s partner)
        if chatter_lines:
            self.env.user.partner_id.message_post(
                body="<pre>GAEB Import:\n" + "\n".join(chatter_lines) + "</pre>",
                subtype_xmlid="mail.mt_note"
            )

        # return {
        #     'type': 'ir.actions.act_window',
        #     'res_model': 'sale.efb.line',
        #     'view_mode': 'tree,form',
        #     'name': 'Imported EFB Lines',
        # }

    # def action_import_x83(self):
    #     if not self.gaeb_file or not self.filename:
    #         raise UserError("Please upload a GAEB file.")
    #
    #     ext = os.path.splitext(self.filename or "")[1].lower()
    #     content = base64.b64decode(self.gaeb_file)
    #
    #     # Create Sale Order
    #     sale_order = self.env['sale.order'].create({
    #         'partner_id': self.env.user.partner_id.id,
    #         'origin': self.filename,
    #     })
    #
    #     if ext == '.x83':
    #         try:
    #             tree = etree.fromstring(content)
    #             for node in tree.xpath('//Item'):
    #                 name = node.findtext('Name') or 'Unnamed Item'
    #                 qty = float(node.findtext('Quantity') or 1)
    #                 price = float(node.findtext('Price') or 0.0)
    #                 self.env['sale.order.line'].create({
    #                     'order_id': sale_order.id,
    #                     'name': name,
    #                     'product_uom_qty': qty,
    #                     'price_unit': price,
    #                 })
    #         except Exception as e:
    #             raise UserError(f"Invalid GAEB XML file. Error: {e}")
    #
    #     elif ext == '.d83':
    #         try:
    #             lines = content.decode('utf-8').splitlines()
    #             for line in lines:
    #                 if line.startswith("112"):
    #                     text = line[6:].strip()
    #                     name = text.split("Qty:")[0].strip()
    #                     qty_raw = text.split("Qty:")[1].split("Price:")[0].strip()
    #                     qty = float(qty_raw)
    #                     price_raw = text.split("Price:")[1].strip()
    #                     price = float(price_raw.split()[0])  # take only the price number
    #                     self.env['sale.order.line'].create({
    #                         'order_id': sale_order.id,
    #                         'name': name,
    #                         'product_uom_qty': qty,
    #                         'price_unit': price,
    #                     })
    #
    #         except Exception as e:
    #             raise UserError(f"Error parsing .d86 file: {e}")
    #
    #     else:
    #         raise UserError("Only .x83 (XML) and .d83 (Text) files are supported.")
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'sale.order',
    #         'view_mode': 'form',
    #         'res_id': sale_order.id,
    #     }

    # def action_import_x86(self):
    #     if not self.gaeb_file or not self.filename:
    #         raise UserError("Please upload a GAEB file.")
    #
    #     ext = os.path.splitext(self.filename)[1].lower()
    #     if ext not in ('.x86', '.d86'):
    #         raise UserError("Only .x86 and .d86 file types are supported.")
    #
    #     content = base64.b64decode(self.gaeb_file)
    #     parsed_items = []
    #
    #     with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
    #         tmp.write(content)
    #         tmp.flush()
    #         filepath = tmp.name
    #
    #     if ext == '.x86':
    #         if not XmlGaebParser:
    #             raise UserError(
    #                 "The gaeb_parser library is not installed. Please install it with `pip install gaeb-parser`.")
    #         try:
    #             df = XmlGaebParser(filepath)
    #             for _, row in df._parse_gaeb(filepath):
    #                 parsed_items.append({
    #                     'description': row.get('description', 'No description'),
    #                     'quantity': row.get('quantity', 1.0),
    #                     'price': row.get('unit_price', 0.0),
    #                 })
    #         except Exception as e:
    #             raise UserError(f"Error parsing .x86 file: {e}")
    #
    #     elif ext == '.d86':
    #         try:
    #             with open(filepath, 'r', encoding='utf-8') as f:
    #                 lines = f.readlines()
    #                 for line in lines:
    #                     if line.startswith('112'):
    #                         match = re.search(r'112\s+[PN]\s+(.*?)\s+Qty:\s*([\d.]+)\s+Price:\s*([\d.]+)', line)
    #                         if match:
    #                             desc, qty, price = match.groups()
    #                             parsed_items.append({
    #                                 'description': desc.strip(),
    #                                 'quantity': float(qty),
    #                                 'price': float(price),
    #                             })
    #         except Exception as e:
    #             raise UserError(f"Error parsing .d86 file: {e}")
    #
    #     if not parsed_items:
    #         raise UserError("No sale order lines found in the GAEB file.")
    #
    #     order = self.env['sale.order'].create({
    #         'partner_id': self.env.user.partner_id.id,
    #         'origin': self.filename,
    #     })
    #
    #     for item in parsed_items:
    #         self.env['sale.order.line'].create({
    #             'order_id': order.id,
    #             'name': item['description'],
    #             'product_uom_qty': item['quantity'],
    #             'price_unit': item['price'],
    #         })
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'sale.order',
    #         'view_mode': 'form',
    #         'res_id': order.id,
    #     }