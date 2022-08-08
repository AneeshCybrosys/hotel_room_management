# -*- coding: utf-8 -*-
from odoo import models, fields, api


class FoodOrderLine(models.Model):
    _name = 'food.order.line'
    _description = 'Order Lines'

    food_menu_id = fields.Many2one('food.menu', string='Food')
    order_id = fields.Many2one('food.order', string='Food Order')
    food_description = fields.Text()
    quantity = fields.Integer()
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    food_price = fields.Float('Unit Price')
    subtotal = fields.Float(compute='_compute_subtotal', string="SubTotal")

    @api.depends('quantity', 'food_price')
    def _compute_subtotal(self):
        for rec in self:
            if rec.quantity:
                rec.subtotal = rec.quantity * rec.food_price
