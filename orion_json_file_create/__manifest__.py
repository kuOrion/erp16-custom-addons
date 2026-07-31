{
    'name': 'Orion E-Invoice JSON Creator',
    'version': '16.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Generate GST e-invoice JSON format for invoices',
    'description': """
        This module allows you to generate e-invoice JSON files
        for selected customer invoices according to Indian GST requirements.
        The module supports both domestic and export invoices.
    """,
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'views/json_file.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
