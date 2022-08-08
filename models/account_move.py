# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = "account.move"

    accommodation_id = fields.Many2one('hotel.accommodation')

    @api.constrains('payment_state')
    def change_state(self):
        for rec in self:
            if rec.payment_state == 'paid':
                self.accommodation_id.state = 'paid'

    # @api.onchange('payment_state')
    # def _onchange_payment_state(self):
    #     if self.payment_state == 'paid':
    #         self.accommodation_id.paid = True
