# -*- coding: utf-8 -*-
"""
Module for GAEB File Importer.

This module defines the `GaebImporter` class, which provides functionality to import GAEB files (.x83 and .d83)
and process their contents into Odoo models. It includes methods for parsing, validating, and creating records
based on the imported data.

Classes:
    GaebImporter: Handles the import and processing of GAEB files.

Attributes:
    gaeb_file (Binary): The uploaded GAEB file.
    filename (Char): The name of the uploaded file.
    file_type (Selection): The type of GAEB file being imported (.x83 or .d83).

Methods:
    _create_efb_line: Creates an EFB line based on the imported data.
    _import_x83: Handles the import of .x83 file type.
    _import_d83: Handles the import of .d83 file type.
    action_import_file: Validates and initiates the import process based on the file type.
"""

import base64
import os
import re

from lxml import etree
from odoo.exceptions import UserError

from odoo import models, fields, api


class GaebImporter(models.TransientModel):
    """
    GAEB File Importer class.

    This class provides methods to import GAEB files (.x83 and .d83) and process their contents into Odoo models.
    """
    _name = 'gaeb.importer'
    _description = 'GAEB File Importer'

    # Binary field to store the uploaded GAEB file
    gaeb_file = fields.Binary("GAEB File", required=True)
    # Char field to store the filename of the uploaded file
    filename = fields.Char("Filename")
    # Selection field to specify the type of GAEB file being imported
    file_type = fields.Selection([
        ('x83', 'GAEB (.x83)'),
        ('d83', 'GAEB (.d83)'),
    ], string="File Type", default='x83', required=True)

    def _create_efb_line(self, item, desc_lines, efb_model, chatter_lines):
        """
        Creates an EFB line based on the imported data.

        Args:
            item (dict): Dictionary containing item details (quantity, unit, price, etc.).
            desc_lines (list): List of description lines for the item.
            efb_model (Model): The model to create the EFB line in.
            chatter_lines (list): List to store summary lines for the chatter.
        """
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

    def _import_x83(self):
        """
        Handles the import of .x83 file type.

        Parses the XML content of the uploaded .x83 file and processes its elements to create records in Odoo.
        """
        try:
            content = base64.b64decode(self.gaeb_file)
            tree = etree.fromstring(content)
        except Exception as e:
            raise UserError(f"Invalid XML file: {e}")

        # Detect GAEB version and namespace
        root_ns = tree.nsmap.get(None)
        if root_ns not in ["http://www.gaeb.de/GAEB_DA_XML/DA83/3.2", "http://www.gaeb.de/GAEB_DA_XML/DA83/3.3",
                           "http://www.gaeb.de/GAEB_DA_XML/200407"]:
            raise UserError(f"Unsupported GAEB namespace: {root_ns}")
        ns = {'g': root_ns}

        efb_model = self.env['offer.efb']
        order = self.env[self._context['active_model']].browse(self._context['active_id'])

        # Handle <AddText> and <Remark> with clean HTML formatting
        html_sections = []

        # AddText content
        addtext_nodes = tree.xpath('//g:AddText', namespaces=ns)
        for addtext in addtext_nodes:
            html_parts = []

            outlines = addtext.xpath('.//g:OutlineAddText//g:p', namespaces=ns)
            details = addtext.xpath('.//g:DetailAddText//g:p', namespaces=ns)

            for p in outlines + details:
                html_parts.append(etree.tostring(p, method='html', encoding='unicode'))

            if html_parts:
                html_sections.append("<div><h3 style='color:#2a2a2a'>AddText:</h3>" + "".join(html_parts) + "</div>")

        # Remark content
        remark_nodes = tree.xpath('//g:Remark//g:CompleteText//g:DetailTxt//g:Text//g:p', namespaces=ns)
        remark_parts = []
        for p in remark_nodes:
            remark_parts.append(etree.tostring(p, method='html', encoding='unicode'))

        if remark_parts:
            html_sections.append("<div><h3 style='color:#2a2a2a'>Remarks:</h3>" + "".join(remark_parts) + "</div>")

        # Write to sale order note
        if html_sections:
            order.note = "<br/><br/>".join(html_sections)

        # Import EFB lines from <Item>
        items = tree.xpath('//g:Item', namespaces=ns)
        if not items:
            raise UserError("No <Item> elements found in GAEB file.")

        chatter_lines = []

        for item in items:
            qty = float(item.findtext('g:Qty', namespaces=ns) or 0.0)
            unit = item.findtext('g:QU', namespaces=ns) or ''
            uom = self.env['uom.uom'].sudo().search([('name', 'ilike', unit)], limit=1)

            if not uom:
                raise UserError(f"UoM not found for unit: {unit}")

            # Outline (short) description
            desc_nodes = item.xpath('.//g:Description//g:CompleteText//g:OutlineText//g:OutlTxt//g:TextOutlTxt//g:span',
                                    namespaces=ns)
            desc = " ".join(span.text.strip() for span in desc_nodes if span.text)

            # Detail (long) description
            span_nodes = item.xpath('.//g:Description//g:CompleteText//g:DetailTxt//g:Text//g:span', namespaces=ns)
            full_description = " ".join(span.text.strip() for span in span_nodes if span.text)

            efb_model.create({
                'order_id': order.id,
                'description': desc or 'No description',
                'long_desc': full_description or 'No description',
                'product_uom_qty': qty,
                'product_uom': uom.id,
            })

            chatter_lines.append(f"{desc or 'No name'} — Qty: {qty}, Unit: {unit}")

        # Post import summary to chatter
        if chatter_lines:
            order.message_post(
                body="<pre>GAEB (.x86) Import:\n" + "\n".join(chatter_lines) + "</pre>",
                subtype_xmlid="mail.mt_note"
            )

    def _import_d83(self):
        """
        Handles the import of .d83 file type.

        Parses the content of the uploaded .d83 file and processes its elements to create records in Odoo.
        """
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
                if line[:6].strip() in ("111", "110101"):
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
        """
        Validates and initiates the import process based on the file type.

        Raises:
            UserError: If the file type or extension does not match the selected file type.
        """
        if not self.gaeb_file or not self.filename:
            raise UserError("Please upload a GAEB file.")

        ext = os.path.splitext(self.filename)[1].lower()

        if self.file_type == 'x83':
            if ext != '.x83':
                raise UserError("Selected file type is .x83 but uploaded file is not .x83.")
            self._import_x83()

        elif self.file_type == 'd83':
            if ext != '.d83':
                raise UserError("Selected file type is .d83 but uploaded file is not .d83.")
            self._import_d83()
        else:
            raise UserError("Unsupported file type.")


    # def _import_d83(self):
    #     """
    #     Import GAEB .d83 file:
    #     - Optional products (marked with NEN) → added to sale_order_option_ids
    #     - Other products → fallback to offer.efb model
    #     """
    #     content = base64.b64decode(self.gaeb_file)
    #     lines = content.decode("utf-8", errors="ignore").splitlines()
    #
    #     efb_model = self.env["offer.efb"]
    #     chatter_lines = []
    #
    #     current_item = {}
    #     description_lines = []
    #     current_title = ""
    #     processing = False
    #
    #     for line in lines:
    #         code = line[:2]
    #
    #         if not processing:
    #             if line[:6].strip() in ("111", "110101"):
    #                 processing = True
    #             continue
    #
    #         if code == "11":
    #             current_title = line[2:70].strip()
    #             continue
    #
    #         elif code == "21":
    #             # Finalize previous item
    #             if current_item:
    #                 self._create_efb_or_optional(current_item, description_lines, efb_model, chatter_lines)
    #                 current_item = {}
    #                 description_lines = []
    #
    #             item_number = line[3:7].strip()
    #
    #             # Check if 'NEN' is present in attribute/code area
    #             nen_code = line[7:15].strip().upper()
    #             is_optional = "NEN" in nen_code
    #
    #             # Extract quantity and unit
    #             raw_qty_unit = line[30:43].strip()
    #             qty, unit = 0.0, ""
    #             match = re.match(r"(\d+)([A-Za-z]+)", raw_qty_unit)
    #             if match:
    #                 qty = int(match.group(1)) / 1000.0
    #                 unit_code = match.group(2)
    #
    #                 # Try to find matching UoM record by name or symbol
    #                 uom = self.env['uom.uom'].search([('name', 'ilike', unit_code)], limit=1)
    #                 if not uom:
    #                     uom = self.env['uom.uom'].search([('uom_type', '=', 'reference')], limit=1)  # fallback
    #
    #                 unit = uom.id if uom else False
    #
                # current_item = {
                #     "ks_pos": float(item_number),
                #     "qty": qty,
                #     "unit": unit,
                #     "price": 0.0,
                #     "total": 0.0,
                #     "title": current_title or "",
                #     "is_optional": is_optional,
                # }
    #
    #         elif code == "23" and current_item:
    #             price_str = line[22:34].strip()
    #             total_str = line[36:48].strip()
    #             try:
    #                 current_item["price"] = float(price_str) / 100
    #             except:
    #                 current_item["price"] = 0.0
    #             try:
    #                 current_item["total"] = float(total_str) / 100
    #             except:
    #                 current_item["total"] = 0.0
    #
    #         elif code == "26":
    #             text = line[5:70].strip()
    #             if text:
    #                 description_lines.append(text)
    #
    #         elif code == "25":
    #             if current_item:
    #                 self._create_efb_or_optional(current_item, description_lines, efb_model, chatter_lines)
    #                 current_item = {}
    #                 description_lines = []
    #
    #     # Final item
    #     if current_item:
    #         self._create_efb_or_optional(current_item, description_lines, efb_model, chatter_lines)
    #
    #     # Post summary to chatter
    #     if chatter_lines:
    #         self.env.user.partner_id.message_post(
    #             body="<pre>GAEB (.d83) Import:\n" + "\n".join(chatter_lines) + "</pre>",
    #             subtype_xmlid="mail.mt_note"
    #         )
    #
    # def _create_efb_or_optional(self, item, description_lines, efb_model, chatter_lines):
    #     description = "\n".join(description_lines).strip()
    #     is_optional = item.get("is_optional", False)
    #
    #     # Try to match product
    #     product = self._match_product(description)
    #     if not product:
    #         chatter_lines.append(f"⚠️ No product matched: {description}")
    #         return
    #     ks_order_id = self.env[self._context['active_model']].browse(self._context['active_id'])
    #     if is_optional:
    #         ks_order_id.sale_order_option_ids.create({
    #                 'order_id': ks_order_id.id,
    #                 'product_id': product.id,
    #                 'name': description,
    #                 'quantity': item['qty'],
    #                 'uom_id': product.uom_id.id,
    #                 'price_unit': item['price'],
    #         })
    #         chatter_lines.append(f"(Optional) Added: {description}")
    #     else:
    #         efb_model.create({
    #             'order_id': ks_order_id.id,
    #             'ks_pos': item.get("ks_pos"),
    #             'product_uom_qty': item.get("qty"),
    #             'product_uom': item.get("unit"),
    #             'price_unit': item.get("price"),
    #             'price_subtotal': item.get("total"),
    #             'description': description,
    #             # 'title': item.get("title"),
    #         })
    #         chatter_lines.append(f"Added regular EFB line: {description}")
    #
    # def _match_product(self, description):
    #     """
    #     Try to find a product by partial name match.
    #     """
    #     product_pool = self.env['product.product']
    #     # product = product_pool.search([('name', 'ilike', description)], limit=1)
    #     product = product_pool.search([('name', 'ilike', 'main Position')], limit=1)
    #     return product or False

    # def _import_d83(self):
    #     """
    #     Import GAEB .d83 file:
    #     - Optional items (with NEN) are added to sale_order_option_ids
    #     - Items are created ONLY if a 25 line confirms completion
    #     - uom is resolved to a Many2one uom.uom record
    #     """
    #     content = base64.b64decode(self.gaeb_file)
    #     lines = content.decode("utf-8", errors="ignore").splitlines()
    #
    #     efb_model = self.env["offer.efb"]
    #     chatter_lines = []
    #
    #     current_item = {}
    #     description_lines = []
    #     current_title = ""
    #     processing = False
    #
    #     for line in lines:
    #         code = line[:2]
    #
    #         if not processing:
    #             if line[:6].strip() in ("111", "110101"):
    #                 processing = True
    #             continue
    #
    #         if code == "11":
    #             current_title = line[2:70].strip()
    #             continue
    #
    #         elif code == "21":
    #             current_item = {}
    #             description_lines = []
    #
    #             item_number = line[2:7].strip()
    #             nen_code = line[7:15].strip().upper()
    #             is_optional = "NEN" in nen_code
    #
    #             raw_qty_unit = line[30:43].strip()
    #             qty, uom_id = 0.0, False
    #             match = re.match(r"(\d+)([A-Za-z]+)", raw_qty_unit)
    #             if match:
    #                 qty = int(match.group(1)) / 1000.0
    #                 unit_code = match.group(2)
    #                 uom = self.env['uom.uom'].search([('name', 'ilike', unit_code)], limit=1)
    #                 if not uom:
    #                     uom = self.env['uom.uom'].search([('uom_type', '=', 'reference')], limit=1)
    #                 uom_id = uom.id if uom else False
    #
    #             current_item = {
    #                 "ks_pos": float(item_number),
    #                 "qty": qty,
    #                 "unit": uom_id,
    #                 "price": 0.0,
    #                 "total": 0.0,
    #                 "title": current_title or "",
    #                 "is_optional": is_optional,
    #             }
    #
    #         elif code == "23" and current_item:
    #             price_str = line[22:34].strip()
    #             total_str = line[36:48].strip()
    #             try:
    #                 current_item["price"] = float(price_str) / 100
    #             except:
    #                 current_item["price"] = 0.0
    #             try:
    #                 current_item["total"] = float(total_str) / 100
    #             except:
    #                 current_item["total"] = 0.0
    #
    #         elif code == "26":
    #             text = line[5:70].strip()
    #             if text:
    #                 description_lines.append(text)
    #
    #         elif code == "25":
    #             if current_item:
    #                 self._create_efb_or_optional(current_item, description_lines, efb_model, chatter_lines)
    #                 current_item = {}
    #                 description_lines = []
    #
    #     # DO NOT create incomplete items — we skip any leftover current_item here
    #
    #     # Log import summary to chatter
    #     if chatter_lines:
    #         self.env.user.partner_id.message_post(
    #             body="<pre>GAEB (.d83) Import:\n" + "\n".join(chatter_lines) + "</pre>",
    #             subtype_xmlid="mail.mt_note"
    #         )

    # def _create_efb_or_optional(self, item, description_lines, efb_model, chatter_lines):
    #     description = "\n".join(description_lines).strip()
    #     is_optional = item.get("is_optional", False)
    #
    #     # Try to find a matching product
    #     product = self._match_product(description)
    #     if not product:
    #         chatter_lines.append(f"⚠️ No product matched: {description}")
    #         return
    #     ks_order_id = self.env[self._context['active_model']].browse(self._context['active_id'])
    #     if is_optional:
    #         ks_order_id.sale_order_option_ids.create({
    #             'order_id': ks_order_id.id,
    #             'product_id': product.id,
    #             'name': description,
    #             'quantity': item['qty'],
    #             'uom_id': product.uom_id.id,
    #             'price_unit': item['price'],
    #         })
    #         chatter_lines.append(f"(Optional) Added: {description}")
    #     else:
    #         efb_model.create({
    #             'order_id': ks_order_id.id,
    #             'ks_pos': item.get("ks_pos"),
    #             'product_uom_qty': item.get("qty"),
    #             'product_uom': item.get("unit"),
    #             'price_unit': item.get("price"),
    #             'price_subtotal': item.get("total"),
    #             'description': description,
    #             # 'title': item.get("title"),
    #         })
    #         chatter_lines.append(f"Added EFB line: {description}")

    # def _match_product(self, description):
    #     """
    #     Try to find a product by partial name match.
    #     """
    #     product_pool = self.env['product.product']
    #     # product = product_pool.search([('name', 'ilike', description)], limit=1)
    #     product = product_pool.search([('name', 'ilike', 'main Position')], limit=1)
    #     return product or False

