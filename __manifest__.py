# -*- coding: utf-8 -*-
{
    'name': "toonproject",

    'summary': """
        Project managing system for cartoon production""",

    'description': """
        Work in progress
    """,

    'author': "Revival",
    'website': "http://www.revival.ru",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Toonproject',
    'version': '0.11',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'web'],

    # always loaded
    'data': [
		'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/dashboard_form.xml',
        'views/templates.xml',
        'views/eternal_data.xml',
        'views/preset_data.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}