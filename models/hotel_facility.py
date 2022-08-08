# -*- coding: utf-8 -*-
from odoo import models, fields


class HotelFacility(models.Model):
    _name = 'hotel.facility'
    _description = 'Hotel Facilities'

    name = fields.Char(string='Facility')
