{
    'name': 'Repair Dispatch Tracking',
    'version': '16.0.1.0.0',
    'category': 'Repair',
    'summary': 'Track Dispatch to Warehouse transfer with dates in Repair Order',
    'description': """
Automatically transfers repaired product from Dispatch Location
to Warehouse Location and stores both locations with date.
""",
    'author': 'Orion Instruments',
    'depends': ['repair', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/repair_order_view.xml',
    ],
    'installable': True,
    'application': False,
}
