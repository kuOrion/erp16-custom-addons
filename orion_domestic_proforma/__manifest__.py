{
    'name': 'Orion Domestic Proforma',
    'version': '16.0',
    'category': 'Reporting',
    'license': 'LGPL-3',
    'summary': 'Module to generate Py3o reports for Domestic Proforma',
    'author': 'Sarthak Samgir',
    'depends': ['base', 'sale', 'report_py3o'],
    'data': [
        'data/proforma_sequence.xml',
        'views/orion_proforma.xml',
        'views/res_config_settings_view.xml',
        'views/domestic_proforma.xml',
    ],
    'license': 'LGPL-3',
    'sequence': -100,
    'installable': True,
    'application': True,
}
