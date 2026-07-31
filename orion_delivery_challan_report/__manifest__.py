{
    'name': 'Orion delivery challan report',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'Sarthak Pradip Samgir',
    'summary': 'Custom Invoice Report with Py3o',
    'depends': ['base','account', 'sale', 'report_py3o'],
    'data': [
        # 'views/repair_quotation.xml',
        'views/delivery_challan.xml',
        'views/dellivery_Challan_button.xml',

        ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',

}