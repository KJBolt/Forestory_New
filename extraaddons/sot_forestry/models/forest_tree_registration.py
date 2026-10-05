from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError


class ForestTreeRegister(models.Model):
    _name = "forest.tree"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Forest Tree Register"
    _order = 'id desc'

    active = fields.Boolean(string="Active", default=True)
    note = fields.Text(string="Note")
    name = fields.Char(string="Serial No", required=True, default=lambda self: _("New"), tracking=True, readonly=True)
    forest_reverse_id = fields.Many2one("forest.reverse", string="Forest Name")
    diameter = fields.Integer(string="Diameter")
    remarks = fields.Text(string="Remarks")
    plot_compartment_id = fields.Many2one('forest.reverse.line', string="Plot/Compartment")
    document_date = fields.Date(string="Document Date")
    stripe_id = fields.Many2one('forest.reverse.line.stripe', string="Strip Line")
    diameter_id = fields.Many2one("uom.uom", string="Diameter Type")
    latitude = fields.Char(related='plot_compartment_id.latitude', string="Latitude")
    longitude = fields.Char(related='plot_compartment_id.longitude', string="Longitude")

    line_ids = fields.One2many('forest.tree.line', 'tree_id', string="Forest Reverse Details")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('cancel', 'Canceled')],
        default='draft',
        string="Status",
        tracking=True,
    )

    @api.onchange('forest_reverse_id')
    def _onchange_forest_reverse_id(self):
        if self.forest_reverse_id:
            plot_compartment_id = self.env['forest.reverse.line'].search(
                [('reverse_id', '=', self.forest_reverse_id.id)], limit=1)
            if plot_compartment_id:
                if not plot_compartment_id.is_used_plot_compartment:
                    self.plot_compartment_id = plot_compartment_id.id
                else:
                    self.plot_compartment_id = False
            else:
                self.plot_compartment_id = False
        else:
            self.plot_compartment_id = False

    @api.onchange('plot_compartment_id')
    def _onchange_plot_compartment_id(self):
        if self.stripe_id.reserve_line_id != self.plot_compartment_id:
            self.stripe_id = False

    @api.constrains('line_ids')
    def _check_line_ids(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError(_("Please add tree details."))

    def set_approved(self):
        for rec in self:
            rec.state = 'approved'
            rec.plot_compartment_id.is_used_plot_compartment = True

    def set_cancel(self):
        for rec in self:
            rec.state = 'cancel'
            rec.plot_compartment_id.is_used_plot_compartment = False

    def action_reset_draft(self):
        for rec in self:
            rec.write({'state': 'draft'})
            rec.plot_compartment_id.is_used_plot_compartment = False

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('forest.tree.registration')
        result = super(ForestTreeRegister, self).create(vals)
        return result


class ForestFellingLine(models.Model):
    _name = "forest.tree.line"
    _description = "Forest Tree Line"

    def _default_uom(self):
        uom = self.env.ref('uom.product_uom_meter', raise_if_not_found=False)
        return uom.id

    name = fields.Char(string="Stock Number")

    # Get Raw material species
    product_id = fields.Many2one(
        "product.product", 
        string="Species", 
        help="Product with species attribute",
        domain="[('categ_id.name', 'ilike', 'Raw Material-RM')]"
    )
    species_id = fields.Many2one("product.attribute.value", string="Species")
    tree_id = fields.Many2one('forest.tree', string="Parent")
    forest_reverse_id = fields.Many2one('forest.reverse', related='tree_id.forest_reverse_id', string="Forest Name")
    plot_compartment_id = fields.Many2one(
        'forest.reverse.line', related='tree_id.plot_compartment_id',
        string="Plot/Compartment"
    )
    condition_score = fields.Float(string="Condition Score")
    diameter = fields.Float(string="Diameter")
    uom_id = fields.Many2one("uom.uom", string="UoM", default=_default_uom)
    latitude = fields.Char(string="Latitude")
    longitude = fields.Char(string="Longitude")
    approved = fields.Boolean(string="Approved?")
    is_used = fields.Boolean(string="Is Used?")
    state = fields.Selection([
        ('standing', 'Standing'),
        ('fallen', 'Fallen')],
        default='standing',
        string="Status"
    )

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            # Get all attribute values linked to the selected product
            product_template = self.product_id.product_tmpl_id

            # Get the 'species' attribute based on your is_species field
            species_attribute = self.env['product.attribute'].search([('is_species', '=', True)], limit=1)

            if species_attribute:
                # Filter product's attribute values related to the 'Species' attribute
                species_values = product_template.valid_product_template_attribute_line_ids.mapped(
                    'value_ids').filtered(
                    lambda val: val.attribute_id == species_attribute
                )

                # Return a domain to restrict the species_id dropdown to these filtered values
                return {'domain': {'species_id': [('id', 'in', species_values.ids)]}}
        else:
            # No product selected, so clear the domain
            return {'domain': {'species_id': []}}

    @api.constrains('state')
    def _check_state(self):
        for rec in self:
            if rec.state == 'fallen' and not rec.approved:
                raise ValidationError(_("Please approve the tree before falling it."))

            if rec._origin and rec._origin.state == 'fallen' and rec.state != 'fallen':
                raise ValidationError(_("You cannot change the state of a fallen tree."))

    def action_approve(self):
        for rec in self:
            rec.approved = True

    def action_unapprove(self):
        fallen_tree_exists = self.filtered(lambda x: x.state == 'fallen')
        if fallen_tree_exists:
            raise ValidationError(_("You cannot unapprove a fallen tree."))

        for rec in self:
            rec.approved = False

    def preview_lat_log(self):
        self.ensure_one()
        if not self.latitude or not self.longitude:
            raise UserError("Latitude and Longitude must be set to preview the map.")

        return {
            'type': 'ir.actions.act_url',
            'target': '_blank',
            'url': f"https://www.google.com.sa/maps/search/{self.latitude},{self.longitude}",
        }
