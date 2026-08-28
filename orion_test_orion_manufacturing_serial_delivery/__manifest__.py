{
    'name': 'Auto Attach Serials on Delivery Orders',
    'version': '16.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Automatically fetch and assign available serials on deliveries',
    'depends': ['sale',
                'stock',
                'mrp',
                'orion_test_sh_mo_auto_serial_no',
                ],
    'data': [
        # 'views/auto_delivery_serial.xml',
        # 'views/stock_move_line.xml',
    ],
    'application': False,
}
