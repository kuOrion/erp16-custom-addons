{
    'name': 'Create FG to STOCK Report',
    'depends': ['base', 'stock', 'report_py3o', 'orion_inventory_product_transfer'],
    'license': 'LGPL-3',
    'data': [
        'views/fg_to_stock.xml',
        'views/py3o_fgtostock.xml',

        'security/ir.model.access.csv',
    ],
    'installable': True,
    'license': 'LGPL-3',
    'application': True,
    'auto_install': False,
}
