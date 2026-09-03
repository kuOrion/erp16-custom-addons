{
    'name': 'Orion purchase Reports',
    'version': '1.0',
    'category': 'Reporting',
    'summary': 'Module to generate Py3o reports for sales and purchase RFQs',
    'author': 'Your Name',
    'depends': ['base','stock' ,'purchase', 'report_py3o'],
    'data': [
        'reports/purchase.xml',
        'reports/orion_purchase_report_button.xml',
        'reports/rfq.xml',

    ],
    'license': 'LGPL-3',
    'sequence': -100,
    'installable': True,
    'application': True,
}

