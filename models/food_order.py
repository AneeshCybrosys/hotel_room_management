# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class HotelFoodOrder(models.Model):
    _name = 'food.order'
    _description = 'Food orders'
    _rec_name = 'room_id'

    room_id = fields.Many2one('hotel.room', string='Room',
                              required=True)
    partner_id = fields.Many2one('res.partner', string='Guest', store=True)
    order_time = fields.Datetime(string='Order Date and Time',
                                 default=datetime.now())
    food_category_ids = fields.Many2many('food.category',
                                         string='Food Categories', required=True)
    food_menu_ids = fields.Many2many('food.menu', string='Food Menu')
    order_line_ids = fields.One2many('food.order.line', 'order_id',
                                     string='Order Line', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    total = fields.Float(compute='_compute_total', string='Total')
    accommodation_id = fields.Many2one('hotel.accommodation',
                                       string='Reference ID', store=True)

    @api.constrains('room_id')
    def _check_food_order(self):
        self.room_id.food_order = True

    @api.onchange("food_category_ids")
    def _onchange_food_category(self):
        self.food_menu_ids = False
        if self.food_category_ids:
            rec = self.env['food.menu'].search(
                [('category_id', 'in', self.food_category_ids.ids)])
            self.food_menu_ids = rec

    @api.onchange("room_id")
    def _onchange_room_id(self):
        rec = self.env['hotel.accommodation'].search(
            [('state', '=', 'check_in'), ('room_id', '=', self.room_id.id)])
        self.partner_id = rec.partner_id
        self.accommodation_id = rec

    @api.depends("order_line_ids")
    def _compute_total(self):
        self.total = sum(self.order_line_ids.mapped('subtotal'))
