{
    'name': 'Orion Invoice Report',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'Sarthak Pradip Samgir',
    'summary': 'Custom Invoice Report with Py3o',
    'depends': ['base', 'account', 'sale', 'report_py3o'],
    'data': [
        'views/export_invoice.xml',
        'views/export_invoice_button.xml',

        'views/tax_invoice.xml',
        'views/tax_invoice_report_button.xml',

        'views/dispatch_report.xml',
        'views/dispatch_note_button.xml',

        'views/packing_list.xml',
        'views/packing_list_button.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': False,
}
