# -*- coding: utf-8 -*-
{
    'name': "Hotel Room Management",

    'summary': """
        Helps to manage hotel accommodation""",

    'description': """
        manage the workflow
    """,

    'author': "Minions 6",

    'version': '15.0.1.0',
    'depends': ['base', 'mail', 'web', 'account'],
    'data': [
        'security/hotel_room_management_security.xml',
        'security/ir.model.access.csv',
        'data/daily_rent_calculation.xml',
        'data/hotel_accommodation_sequence.xml',
        'views/hotel_accommodation_views.xml',
        'views/hotel_facility_views.xml',
        'views/hotel_room_views.xml',
        'views/food_menu_views.xml',
        'views/food_category_views.xml',
        'views/food_order_views.xml',
        'report/hotel_room_management_templates.xml',
        'report/hotel_management_report_views.xml',
        'views/hotel_room_management_menu_item.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'hotel_room_management/static/src/js/action_manager.js'
        ]
    },
}
