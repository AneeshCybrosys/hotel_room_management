# -*- coding: utf-8 -*-
from odoo import models, fields


class FoodCategory(models.Model):
    _name = 'food.category'
    _description = 'Food Category'

    name = fields.Char(string='Category', required=True)
