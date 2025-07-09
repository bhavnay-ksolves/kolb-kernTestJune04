from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    to_be_printed_on_pdf = fields.Boolean(string='To Be Printed on PDF',default=False)
