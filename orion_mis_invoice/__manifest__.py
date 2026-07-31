{
    'name': 'Orion MIS Invoicewise',
    'version': '1.0',
    'depends': ['base', 'product', 'mrp', 'orion_mis_reports_base', 'account', 'report_py3o'],
    'author': 'Sarthak Pradip Samgir',
    'data': [
        'security/ir.model.access.csv',
        'views/invoice.xml',
        'views/invoice_report.xml',
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
