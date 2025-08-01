from odoo import models, fields


class ProductTemplate(models.Model):
    """
    Extension of the Product Template model to include a field for PDF printing.

    This model adds a boolean field to indicate whether the product should be printed
    on a PDF. It inherits from the base 'product.template' model.
    """
    _inherit = 'product.template'  # Inherits from the base 'product.template' model.

    # Boolean field to specify if the product should be printed on a PDF.
    # Default value is False.
    to_be_printed_on_pdf = fields.Boolean(
        string='To Be Printed on PDF',
        default=False
    )


class ProductProduct(models.Model):
    _inherit = 'product.product'

    # Related to filter Main position
    to_be_printed_on_pdf = fields.Boolean(related='product_tmpl_id.to_be_printed_on_pdf', default=False)
