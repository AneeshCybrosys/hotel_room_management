# -*- coding: utf-8 -*-
from odoo import models, fields


class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room Management'

    name = fields.Char(string='Room Number', required=True)
    bed = fields.Selection([('single', 'Single'),
                            ('double', 'Double'),
                            ('dormitory', 'Dormitory')], string='Bed')
    available_beds = fields.Integer(string='Available Beds')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id, string='Currency')
    rent = fields.Float(string='Rent')
    facility_ids = fields.Many2many('hotel.facility',
                                    string="Facilities")
    available = fields.Boolean(default=True, string='Available')
    food_order = fields.Boolean(string='Food Order')
