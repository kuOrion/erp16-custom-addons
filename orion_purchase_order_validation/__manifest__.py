{
    'name': 'Automatic Tax Selection and Validation for Purchase',
    'version': '1.0',
    'summary': 'Automatically select taxes based on fiscal position',
    'description': """
        Automatically sets CGST+SGST for Within and IGST for interstate transactions
    """,
    'author': 'Your Name',
    'depends': ['sale', 'account'],
    'data': [
        'views/purchase_order_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
