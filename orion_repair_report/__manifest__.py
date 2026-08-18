{
    'name': 'Orion delivery challan report for repairs',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'Sarthak Pradip Samgir',
    'summary': 'Custom Invoice Report with Py3o',
    'depends': ['base','repair', 'stock', 'report_py3o'],
    'data': [
        'views/repair_quotation.xml',
        'views/dispatch_to_repair.xml',
        'views/workshop_to_dispatch.xml',
        'views/delivery_challan_customer_report.xml',

        ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
    

}
