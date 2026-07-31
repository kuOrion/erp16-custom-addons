{
    'name': 'Orion sale order line',
    'version': '1.0',
    'depends': ['base','sale'],
    'license': 'LGPL-3',
    'data': [
        # 'views/schedule.xml',
        'security/ir.model.access.csv',

        'views/form_orderline.xml',
        # 'views/confirm_sale_order.xml', #sale Team dont want Sale Order Status menu tab

    ],
    'author': 'sarthak',
    'installable': True,
    'application': True,
    'auto_install': False,
    'sequence': 200,
    'license': 'LGPL-3'
}
