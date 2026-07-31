{
    'name': 'Orion MIS Salewise',
    'depends': ['base', 'sale', 'product','orion_mis_reports_base', 'account', 'mrp', 'report_py3o'],
    # 'data_files': [
    #     ('orion_mis_reports/reports', ['reports/invoice_report.odt'])
    # ],
    'author': 'Sarthak Pradip Samgir',

    'data': [

        'views/salewise.xml',
        'views/salewise_py3o.xml',
        'security/ir.model.access.csv',

        # 'views/invoice.xml',
        # 'views/invoice_report.xml',

    ],
    'license': 'LGPL-3',
    'installable': True,
}
