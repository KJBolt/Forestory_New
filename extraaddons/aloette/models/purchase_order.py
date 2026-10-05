from odoo import models, fields, api

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    use = fields.Text(string='Use', compute='_compute_use', store=True)

    @api.depends('product_id')
    def _compute_use(self):
        for line in self:
            if not line.product_id: continue
            line.use = line.product_id.use
