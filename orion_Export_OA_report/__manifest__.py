{
    'name': 'Orion Export OA Report',
    'version': '1.0',
    'category': 'Reporting',
    'license': 'LGPL-3',
    'summary': 'Module to generate Py3o reports for sales and purchase RFQs',
    'author': 'Sarthak Samgir',
    'depends': ['base', 'sale', 'report_py3o'],
    'data': [
        # 'reports/py3o_quotation.xml',
        'views/orion_sale_OA_export.xml',
    ],
    'external_dependencies': {
        'python': ['py3o.template', 'py3o.fusion'],
    },
    'license': 'LGPL-3',
    'sequence': -100,
    'installable': True,
    'application': True,
}
