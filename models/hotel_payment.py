# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class HotelPayment(models.Model):
    _name = 'hotel.payment'
    _description = 'Payment Information'

    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Char(string='Description')
    quantity = fields.Integer(string='Quantity')
    uom_id = fields.Many2one('uom.uom', string='Uom')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id,
                                  string='Currency')
    unit_price = fields.Float(string='Unit Price')
    subtotal = fields.Float(compute='_compute_subtotal', string='Subtotal')
    accommodation_id = fields.Many2one('hotel.accommodation',
                                       string="Accommodation")

    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            if rec.quantity:
                rec.subtotal = rec.quantity * rec.unit_price

    def rent_calculation(self):
        record_set = self.env['hotel.payment'].search(
            [('product_id', '=', 2),
             ('accommodation_id.state', '=', 'check_in')])
        print(record_set, "record")
        for rec in record_set:
            print(
                (date.today() - rec.accommodation_id.check_in_date.date()).days,
                "check_in")
            checkin_date = rec.accommodation_id.check_in_date.date()
            today = date.today()
            days = (today - checkin_date).days
            if days == 0:
                days = 1
            rec.quantity = days
