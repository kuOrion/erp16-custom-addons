{
    'name': 'Orion sale reports',
    'version': '1.0',
    'category': 'Reporting',
    'license': 'LGPL-3',
    'summary': 'Module to generate Py3o reports for sales',
    'author': 'Sarthak Samgir',
    'depends': ['base', 'sale', 'report_py3o'],
    'data': [
        # 'reports/py3o_quotation.xml',
        'reports/orion_sale_technical_quotation.xml',
        'reports/orion_sale_report_button.xml',


        'data/ir_sequence.xml',
    ],
    'license': 'LGPL-3',
    'sequence': -100,
    'installable': True,
    'application': True,
}
