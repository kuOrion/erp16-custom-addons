{
    'name': 'Orion GRN Report',
    'version': '16.0.1.0.0',
    'category': 'Reporting',
    'summary': 'Module to generate Py3o reports for sales and purchase RFQs',
    'author': 'Sarthak Samgir',
    'depends': ['base', 'stock', 'purchase', 'base_setup', 'report_py3o'],
    'data': [
        # 'data/grn_number.xml',
        'views/grn_report.xml',
        'views/grn_report_button.xml',
        'views/grn_report_config_setting.xml',
    ],
    'external_dependencies': {
        'python': ['py3o.template', 'py3o.fusion'],
    },
    'sequence': -100,
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
    'images': ['static/description/icon.png'],
}
