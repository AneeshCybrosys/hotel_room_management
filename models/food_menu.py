# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.exceptions import ValidationError


class FoodMenu(models.Model):
    _name = 'food.menu'
    _description = 'Food Menu'

    name = fields.Char(string='Food', required=True)
    food_description = fields.Text(string='Description')
    food_price = fields.Float(string='Unit Price')
    category_id = fields.Many2one('food.category', required=True)
    image = fields.Image(string='Image')
    currency_id = fields.Many2one('res.currency', string='Currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id)
    quantity = fields.Integer(string='Quantity')

    def button_add_to_list(self):
        instance_id = self.env.context.get('active_id')
        if self.quantity > 0:
            instant = self.env['food.order'].search([('id', '=', instance_id)])
            order_line = instant.order_line_ids.filtered(
                lambda r: r.food_menu_id == self)
            if not order_line:
                instant.order_line_ids = [(0, 0, {'food_menu_id': self.id,
                                                  'order_id': instance_id,
                                                  'food_description':
                                                      self.food_description,
                                                  'food_price':
                                                      self.food_price,
                                                  'quantity': self.quantity,
                                                  'subtotal': (
                                                          self.food_price
                                                          * self.quantity)})]
            else:
                instant.order_line_ids = [
                    (1, order_line.id, {'food_menu_id': self.id,
                                        'order_id': instance_id,
                                        'food_description':
                                            self.food_description,
                                        'food_price':
                                            self.food_price,
                                        'quantity': order_line.quantity + self.quantity,
                                        })]

            payment_lines = instant.accommodation_id.payment_ids.filtered(
                lambda r: r.product_id.id == 1)
            if not payment_lines:
                instant.accommodation_id.payment_ids = [
                    (0, 0, {'product_id': self.env['product.product'].search(
                            [('id', '=', 1)]).id,
                            'description': 'Food Orders',
                            'quantity': self.quantity,
                            'uom_id': self.env['uom.uom'].search(
                                [('id', '=', 1)]).id,
                            'unit_price':
                                self.food_price,
                            'subtotal':
                                self.quantity * self.food_price,
                            })]
            else:
                subtotal = payment_lines.subtotal + (
                        self.quantity * self.food_price)
                quantity = payment_lines.quantity + self.quantity
                unit_price = subtotal / quantity
                instant.accommodation_id.payment_ids = [
                    (1, payment_lines.id, {'quantity': quantity,
                                           'uom_id': self.env['uom.uom'].search(
                                               [('id', '=', 1)]).id,
                                           'unit_price': unit_price,
                                           })]
        else:
            raise ValidationError('"Please check the order quantity"')
