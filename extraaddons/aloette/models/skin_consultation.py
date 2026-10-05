from odoo import models, fields, api
import json
import logging

_logger = logging.getLogger(__name__)

class SkinConsultation(models.Model):
    _name = 'skin.consultation'
    _description = 'Skin Consultation'
    _order = 'customer_id desc'
    _rec_name = 'customer_id'

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    like_about_skin = fields.Text(string='Skin Likes', help='Array of skin attributes the customer likes')
    like_about_skin_display = fields.Char(string='Skin Likes', compute='_compute_like_about_skin_display')

    improve_about_skin = fields.Text(string='Skin Improvements', help='Array of skin attributes the customer wants to improve')
    improve_about_skin_display = fields.Char(string='Skin Improvements', compute='_compute_improve_about_skin_display')

    vascularity = fields.Selection([
        ('hypo', 'Hypo'),
        ('normal', 'Normal'),
        ('hyper', 'Hyper'),
        ('other', 'Other')
    ], string='Vascularity')
    skin_texture = fields.Selection([
        ('thin', 'Thin'),
        ('medium', 'Medium'),
        ('thick', 'Thick'),
        ('other', 'Other')
    ], string='Skin Texture')
    pigmentation = fields.Selection([
        ('superficial', 'Superficial'),
        ('dermal', 'Dermal'),
        ('both', 'Both'),
        ('other', 'Other')
    ], string='Depth of Pigmentation')
    hydration = fields.Selection([
        ('extreme_dehydrated', 'Extreme Dehydrated'),
        ('dehydrated', 'Dehydrated'),
        ('normal', 'Normal'),
        ('other', 'Other')
    ], string='Hydration Level')
    sebaceous_activity = fields.Selection([
        ('hypo', 'Hypo'),
        ('normal', 'Normal'),
        ('hyper', 'Hyper'),
        ('other', 'Other')
    ], string='Sebaceous Activity')

    # Comment Fields
    vascularity_comment = fields.Char(string='Vascularity Comment', default='No comment')
    skin_texture_comment = fields.Char(string='Skin Texture Comment', default='No comment')
    pigmentation_comment = fields.Char(string='Pigmentation Comment', default='No comment')
    hydration_comment = fields.Char(string='Hydration Comment', default='No comment')
    sebaceous_activity_comment = fields.Char(string='Sebaceous Activity Comment', default='No comment')


    @api.depends('like_about_skin')
    def _compute_like_about_skin_display(self):
        for record in self:
            if record.like_about_skin:
                try:
                    likes = json.loads(record.like_about_skin)
                    record.like_about_skin_display = ', '.join(likes)
                except:
                    record.like_about_skin_display = record.like_about_skin
            else:
                record.like_about_skin_display = ''

    @api.depends('improve_about_skin')
    def _compute_improve_about_skin_display(self):
        for record in self:
            if record.improve_about_skin:
                try:
                    improvements = json.loads(record.improve_about_skin)
                    record.improve_about_skin_display = ', '.join(improvements)
                except:
                    record.improve_about_skin_display = record.improve_about_skin
            else:
                record.improve_about_skin_display = ''


    def action_prescribe(self):
        # Get the customer from the consultation
        customer = self.customer_id
        
        # Create a new quotation with the customer
        quotation = self.env['sale.order'].create({
            'partner_id': customer.id
        })
        
        # Redirect to the quotation form view
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': quotation.id,
            'view_mode': 'form',
            'target': 'current',
        }