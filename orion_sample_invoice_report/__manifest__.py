{
    'name': 'Orion16 Sample invoice Report',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'Sarthak Pradip Samgir',
    'summary': 'Custom Invoice Report with Py3o',
    'depends': ['base', 'account', 'sale', 'orion_sales', 'report_py3o'],
    'data': [
        'views/sample_invoice.xml',
        'views/res_config.xml',
        'views/report_button.xml',
    ],

    'external_dependencies': {
        'python': ['py3o.template', 'py3o.fusion'],
    },

    'installable': True,
    'application': False,
}
