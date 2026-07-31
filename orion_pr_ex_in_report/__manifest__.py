{
    'name': 'Orion export proforma invoice reports',
    'version': '1.0',
    'license': 'LGPL-3',
    'category': 'Reporting',
    'summary': 'Module to generate Py3o reports for sales and purchase RFQs',
    'author': 'sarthak samgir',
    'depends': ['base','sale', 'report_py3o'],
    'data': [
        'views/export_proforma.xml',
        'views/res_bank.xml',

    ],
    'external_dependencies': {
        'python': ['py3o.template', 'py3o.fusion'],
    },
    'sequence': -100,
    'installable': True,
    'application': True,
}

