{
    'name': 'Automatic Tax Selection for Sales',
    'version': '1.0',
    'summary': 'Automatically select taxes based on fiscal position',
    'description': """
        Automatically sets CGST+SGST for intrastate and IGST for interstate transactions
    """,
    'author': 'Your Name',
    'depends': ['sale', 'account'],
    'data': [
        'views/fiscal_position_data.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
