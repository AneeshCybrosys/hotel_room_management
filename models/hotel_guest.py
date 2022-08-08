# -*- coding: utf-8 -*-
from odoo import models, fields


class GuestInformation(models.Model):
    _name = 'hotel.guest'
    _description = 'Guest Information'

    name = fields.Char(string='Guest')
    accommodation_id = fields.Many2one('hotel.accommodation', string='Room')
    guest_gender = fields.Selection([('male', 'Male'),
                                     ('female', 'Female'),
                                     ('other', 'Other')],
                                    string='Gender')
    age = fields.Integer(string='Age')
