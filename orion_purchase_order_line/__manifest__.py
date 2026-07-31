{
    'name': 'Purchase Order Line Specifications',
    'version': '16.0.1.0.0',
    'category': 'Purchases',
    'summary': 'Add specification notes to purchase order lines',
    'description': """
        This module adds a notes field to purchase order lines
        where you can enter specifications for each product line.
    """,
    'author': 'Your Company',
    'depends': ['purchase', 'orion_purchase_report'],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}