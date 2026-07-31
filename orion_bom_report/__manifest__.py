# -*- coding: utf-8 -*-
{
    'name': 'BOM Cost Tracking',
    'version': '16.0.1.0.0',
    'summary': 'Track quoted, budgeted, and actual costs for BOMs',
    'description': """
        This module adds fields to track different cost types for products and
        provides a report to display costs for bill of materials.
    """,
    'category': 'Manufacturing',
    'author': 'sarthak samgir',
    'depends': ['product', 'stock', 'mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/bom.xml',
        'views/py3o_bom.xml',
        # 'views/mrp_bom_views_cost.xml',
    ],
    'installable': True,
    'application': False,
}