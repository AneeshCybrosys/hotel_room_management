# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.tools import date_utils
import json
import io

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class HotelManagementReport(models.TransientModel):
    _name = 'hotel.management.report'
    _description = 'Hotel Management Report'

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    guest = fields.Many2one('res.partner', string="Guest")

    def _query(self):
        query = """ SELECT res_partner.name,check_in_date,check_out_date,state 
                                FROM hotel_accommodation
                                inner join res_partner 
                                on res_partner.id = hotel_accommodation.partner_id
                                where hotel_accommodation.state != 'cancel'"""
        if self.from_date and self.to_date and self.guest.id:
            query += "\n And check_in_date Between '%s' and '%s' " \
                     "And '%d' = hotel_accommodation.partner_id" \
                     % (self.from_date, self.to_date, self.guest.id)
        elif self.from_date and self.to_date and not self.guest.id:
            query += "\n And check_in_date Between '%s' and '%s' " \
                     % (self.from_date, self.to_date)
        elif self.from_date and self.guest.id and not self.to_date:
            query += "\n And check_in_date > '%s' " \
                     "And '%d' = hotel_accommodation.partner_id" \
                     % (self.from_date, self.guest.id)
        elif self.to_date and self.guest.id and not self.from_date:
            query += "\n And check_in_date < '%s' " \
                     "And '%d' = hotel_accommodation.partner_id" \
                     % (self.to_date, self.guest.id)
        elif self.from_date and not self.to_date and not self.guest.id:
            query += "\n And check_in_date > '%s' " \
                     % self.from_date
        elif self.to_date and not self.from_date and not self.guest.id:
            query += "\n And check_in_date < '%s' " \
                     % self.to_date
        elif self.guest.id and not self.to_date and not self.from_date:
            query += "\n And '%d' = hotel_accommodation.partner_id" \
                     % self.guest.id

        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        selection = \
            dict(self.env['hotel.accommodation'].fields_get(allfields=['state'])
                 ['state']['selection'])
        data = {
            'to_date': self.to_date,
            'from_date': self.from_date,
            'guest': self.guest.name,
            'result': result,
            'selection': selection
        }
        return data

    def print_pdf(self):
        data = self._query()
        return self.env.ref(
            'hotel_room_management.action_hotel_management_report_pdf') \
            .report_action(
            self, data=data)

    def print_xlsx(self):
        data = self._query()
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'hotel.management.report',
                     'options': json.dumps(data,
                                           default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Hotel Management Report',
                     },
            'report_type': 'xlsx',
        }

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '20px'})
        sub_head = workbook.add_format(
            {'align': 'center', 'bold': True, 'font_size': '10px'})
        txt = workbook.add_format({'font_size': '10px', 'align': 'center'})
        sheet.set_column(4, 0, 18)
        sheet.merge_range('A2:E3', 'Hotel Management Report', head)
        if data['from_date']:
            sheet.write('A4', 'Date From:', sub_head)
            sheet.write('B4', data['from_date'], txt)
        if data['to_date']:
            sheet.write('A5', 'Date To:', sub_head)
            sheet.write('B5', data['to_date'], txt)
        if data['guest']:
            sheet.write('D4', 'Guest:', sub_head)
            sheet.write('E4', data['guest'], txt)
        headers = ['SL.NO', 'Guest', 'Check-In', 'Check-Out', 'State']
        row = 6
        for header in headers:
            col = headers.index(header)
            sheet.write(row, col, header, sub_head)
        row = 7
        count = 1
        for rows in data['result']:
            col = 0
            sheet.write(row, col, count, txt)
            sheet.write(row, col + 1, rows['name'], txt)
            sheet.write(row, col + 2, rows['check_in_date'], txt)
            sheet.write(row, col + 3, rows['check_out_date'], txt)
            value = \
            dict(self.env['hotel.accommodation'].fields_get(allfields=['state'])
                 ['state']['selection'])[rows['state']]
            sheet.write(row, col + 4, value, txt)
            row += 1
            count += 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
