{
    'name': 'Orion MIS quotation',
    'version': '1.0',
    'author': 'Sarthak Pradip Samgir',
    'depends': ['base', 'product', 'mrp', 'orion_mis_reports_base', 'account', 'report_py3o'],
    'data': [
        'security/ir.model.access.csv',

        'views/quotation_tab.xml',
        'views/quotation_report.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'orion_mis_invoice/reports/**/*',
    #     ],
    # },
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}
