# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError


class HotelAccommodation(models.Model):
    _name = 'hotel.accommodation'
    _description = 'Hotel Room Accommodation'
    _inherit = 'mail.thread'
    _order = "check_in_date desc"

    name = fields.Char(string='Reference ID', readonly=True, copy=False,
                       default='New')
    partner_id = fields.Many2one('res.partner', string="Guest", required=True)
    check_in_date = fields.Datetime(string='Check-In Date and Time',
                                    default=datetime.now())
    check_out_date = fields.Datetime(string='Check-Out Date and Time',
                                     readonly=True)
    room_id = fields.Many2one('hotel.room', string="Room", required=True)
    bed_type = fields.Selection(string='Bed Type', related='room_id.bed',
                                readonly=False, store=True)
    facility_ids = fields.Many2many('hotel.facility',
                                    string="Facilities")
    state = fields.Selection([('draft', 'Draft'),
                              ('check_in', 'Check-In'),
                              ('check_out', 'Check-Out'),
                              ('paid', 'Paid'),
                              ('cancel', 'Cancel')],
                             string="State", default='draft', readonly=True)
    expected_days = fields.Integer(string='Expected Days')
    expected_date = fields.Date(string='Expected Date', default=date.today())
    guest_ids = fields.One2many('hotel.guest', 'accommodation_id',
                                string='Guests')
    no_of_guest = fields.Integer(string='Number of guests')
    currency_id = fields.Many2one('res.currency',
                                  default=lambda self:
                                  self.env.user.company_id.currency_id.id,
                                  string='Currency')
    total = fields.Float(compute='_compute_total', string='Total',
                         readonly=True)
    payment_ids = fields.One2many('hotel.payment', 'accommodation_id',
                                  string='Payments')
    paid = fields.Boolean(default=False, String='Paid')

    @api.constrains('state')
    def _check_state(self):
        if self.state == 'draft':
            self.name = 'In Draft'

    @api.depends("payment_ids.subtotal")
    def _compute_total(self):
        self.total = sum(self.payment_ids.mapped('subtotal'))

    @api.onchange("expected_days")
    def _onchange_expected_days(self):
        self.expected_date = self.check_in_date.date() + timedelta(
            self.expected_days)

    def cancel_btn_action(self):
        self.state = 'cancel'

    def check_in_btn_action(self):
        if len(self.guest_ids) == self.no_of_guest:
            rec = self.env['ir.attachment'].search(
                [('res_id', '=', self.id), ('res_model', '=', self._name)])
            if rec:
                self.state = 'check_in'
                self.room_id.available = False
                self.check_in_date = datetime.now()
                self.name = self.env['ir.sequence'].next_by_code(
                    'hotel.accommodation')
                self.payment_ids = [
                    (0, 0, {'product_id': self.env['product.product'].search(
                        [('id', '=', 2)]).id,
                            'description': 'Room Rent',
                            'quantity': 1,
                            'uom_id': self.env['uom.uom'].search(
                                [('id', '=', 3)]).id,
                            'unit_price':
                                self.room_id.rent,
                            'subtotal':
                                self.room_id.rent,
                            })]
            else:
                raise ValidationError('"Please provide address proof"')
        else:
            raise ValidationError('"Please provide all guest details"')

    def check_out_btn_action(self):
        self.state = 'check_out'
        self.check_out_date = datetime.now()
        self.room_id.available = True
        self.room_id.food_order = False

        payments = self.env['hotel.payment'].search(
            [('accommodation_id', '=', self.id)])
        order_lines = []
        for line in payments:
            order_lines.append((0, 0, {
                'product_id': line.product_id,
                'name': line.description,
                'quantity': line.quantity,
                'price_unit': line.unit_price,
            }))

        move = self.env['account.move'].create([
            {
                'payment_reference': self.name,
                'accommodation_id': self.id,
                'move_type': 'out_invoice',
                'partner_id': self.partner_id,
                'date': self.check_out_date,
                'invoice_date': self.check_out_date,
                'tax_totals_json': self.total,
                'invoice_line_ids': order_lines,
            }])
        return {
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
            'type': 'ir.actions.act_window',
        }

    def button_invoice(self):
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('move_type', '=', 'out_invoice'),
                       ('accommodation_id', '=', self.id)],
            'context': "{'create': False}"
        }
