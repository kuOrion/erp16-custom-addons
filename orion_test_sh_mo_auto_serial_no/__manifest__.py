# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    'name': 'Manufacturing Auto Serial Number',
    "author": "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Manufacturing",
    "license": "OPL-1",
    "summary": "Manufacturing Auto Serial Number ",
    "description": """Manufacturing Auto Serial Number""",
    "version": "16.0.9",
    'depends': [ 'stock', 'mrp','product','sale_mrp','sale_management'],
    'application': True,

    'data': [
        "security/ir.model.access.csv",
        "data/ir_cron.xml",
        "views/product_views.xml",
        "views/res_config_setting_views.xml",
        "views/mrp_production_views.xml",
        "views/sh_finished_product_views.xml",
        "views/stock_move_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_lot_views.xml"
    ],
    "auto_install": False,
    "installable": True,
   
}
