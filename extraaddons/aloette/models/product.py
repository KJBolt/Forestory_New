from odoo import models, fields, api


class Product(models.Model):
    _inherit = 'product.template'

    use = fields.Text(string='Use')
