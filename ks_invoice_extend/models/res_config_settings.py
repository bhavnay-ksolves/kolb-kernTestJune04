from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    qrcode = fields.Binary("Payment QR Code")

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param(
            'ks_invoice_extend.qrcode', self.qrcode)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        qrcode = self.env['ir.config_parameter'].sudo().get_param('ks_invoice_extend.qrcode')
        res.update(
            qrcode=qrcode,
        )
        return res
