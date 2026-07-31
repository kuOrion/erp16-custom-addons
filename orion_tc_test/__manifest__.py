# Working module
{
    'name': 'Test TC Certificate',
    'version': '16.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Module to generate Py3o reports for stock picking',
    'author': 'Sarthak Samgir',
    'depends': ['base', 'stock', 'sale','report_py3o'],
    'data': [
        'views/orion_tc_report.xml',
        'views/tc_report_button.xml',
        'data/sequences.xml',
        'views/res_config_settings_views.xml'

    ],
    'sequence': -1000,
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
